"""
Module Survival Analysis - Hệ thống Phân tích Sống Sót
Sử dụng Cox Proportional Hazards và Random Survival Forest để phân tích Time-to-Default
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.utils import median_survival_times
from sksurv.ensemble import RandomSurvivalForest
from sksurv.util import Surv
import pickle
import os


class SurvivalAnalysisSystem:
    """
    Hệ thống Phân tích Sống Sót (Survival Analysis System)

    Chức năng chính:
    1. Train Cox Proportional Hazards model
    2. Train Random Survival Forest
    3. Tính Kaplan-Meier estimator
    4. Dự báo survival curve cho DN mới
    5. Tính median time-to-default
    6. Tính hazard ratio cho từng chỉ số
    """

    def __init__(self):
        """Khởi tạo Survival Analysis System"""
        self.cox_model = None
        self.rsf_model = None
        self.km_model = None
        self.feature_names = [f'X_{i}' for i in range(1, 15)]
        self.hazard_ratios = {}
        self.training_data = None

        # Tên đầy đủ của 14 chỉ số
        self.indicator_names = {
            'X_1': 'Biên lợi nhuận gộp',
            'X_2': 'Biên lợi nhuận trước thuế',
            'X_3': 'ROA (Lợi nhuận/Tài sản)',
            'X_4': 'ROE (Lợi nhuận/VCSH)',
            'X_5': 'Nợ/Tài sản',
            'X_6': 'Nợ/Vốn chủ sở hữu',
            'X_7': 'Thanh toán hiện hành',
            'X_8': 'Thanh toán nhanh',
            'X_9': 'Khả năng trả lãi',
            'X_10': 'Khả năng trả nợ gốc',
            'X_11': 'Tạo tiền/VCSH',
            'X_12': 'Vòng quay hàng tồn kho',
            'X_13': 'Kỳ thu tiền bình quân',
            'X_14': 'Hiệu suất sử dụng tài sản'
        }

    def prepare_data_with_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Chuẩn bị dữ liệu với cột months_to_default
        Nếu chưa có, tạo synthetic data

        Args:
            df: DataFrame chứa 14 chỉ số (X_1 → X_14) + cột 'default'

        Returns:
            DataFrame với cột months_to_default
        """
        df_prepared = df.copy()

        # Kiểm tra xem đã có cột months_to_default chưa
        #if 'months_to_default' not in df_prepared.columns:
            print("⚠️ Chưa có cột months_to_default, tạo synthetic data...")

            # Tạo synthetic data
            df_prepared['months_to_default'] = df_prepared.apply(
                lambda row: self._generate_months_to_default(row), axis=1
            )

        return df_prepared

    def _generate_months_to_default(self, row: pd.Series) -> int:
        """
        Tạo months_to_default synthetic

        Args:
            row: Dòng dữ liệu

        Returns:
            months_to_default: Số tháng đến khi vỡ nợ (hoặc censored)
        """
        if row['default'] == 1:
            # DN vỡ nợ: Random 6-36 tháng
            # DN có chỉ số tệ hơn → vỡ nợ sớm hơn
            # Dùng PD từ các chỉ số để ước lượng

            # Tính risk score đơn giản từ 14 chỉ số
            risk_score = (
                -row['X_1'] - row['X_2'] - row['X_3'] - row['X_4']  # Sinh lời thấp → rủi ro cao
                + row['X_5'] + row['X_6']  # Nợ cao → rủi ro cao
                - row['X_7'] - row['X_8']  # Thanh khoản thấp → rủi ro cao
                - row['X_9'] - row['X_10']  # Trả nợ kém → rủi ro cao
            )

            # Normalize risk_score về [0, 1]
            # Risk score cao → vỡ nợ sớm
            base_months = 21  # 21 tháng trung bình
            noise = np.random.randint(-9, 9)  # +/- 9 tháng noise

            # Risk score càng cao, months càng thấp
            months = max(6, min(36, base_months + noise - int(risk_score * 3)))
            return months
        else:
            # DN không vỡ nợ: Censored tại 36 tháng
            return 36

    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train cả Cox PH và Random Survival Forest

        Args:
            df: DataFrame chứa 14 chỉ số + months_to_default + default

        Returns:
            Dict chứa thông tin training
        """
        print("🔄 Bắt đầu train Survival Analysis models...")

        # 1. CHUẨN BỊ DỮ LIỆU
        df_prepared = self.prepare_data_with_time(df)
        self.training_data = df_prepared

        # 2. TRAIN COX PROPORTIONAL HAZARDS
        print("📊 Training Cox Proportional Hazards model...")
        self.cox_model = CoxPHFitter()

        # Chuẩn bị dữ liệu cho Cox
        cox_data = df_prepared[self.feature_names + ['months_to_default', 'default']].copy()
        cox_data.rename(columns={'default': 'event'}, inplace=True)

        # Fit Cox model
        self.cox_model.fit(
            cox_data,
            duration_col='months_to_default',
            event_col='event'
        )

        # Lấy hazard ratios
        self.hazard_ratios = self.cox_model.hazard_ratios_.to_dict()

        print("✅ Cox PH model trained successfully!")

        # 3. TRAIN RANDOM SURVIVAL FOREST
        print("🌲 Training Random Survival Forest...")

        # Chuẩn bị dữ liệu cho RSF (scikit-survival)
        X = df_prepared[self.feature_names].values
        y = Surv.from_dataframe('event', 'months_to_default',
                                 cox_data.rename(columns={'event': 'event', 'months_to_default': 'months_to_default'}))

        self.rsf_model = RandomSurvivalForest(
            n_estimators=100,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            n_jobs=-1,
            random_state=42
        )

        self.rsf_model.fit(X, y)

        print("✅ Random Survival Forest trained successfully!")

        # 4. TRAIN KAPLAN-MEIER ESTIMATOR
        print("📈 Fitting Kaplan-Meier estimator...")
        self.km_model = KaplanMeierFitter()
        self.km_model.fit(
            durations=cox_data['months_to_default'],
            event_observed=cox_data['event']
        )

        print("✅ Kaplan-Meier estimator fitted successfully!")

        # 5. CHUẨN BỊ KẾT QUẢ
        # Hazard ratios (top 5 quan trọng nhất)
        hazard_ratios_sorted = sorted(
            self.hazard_ratios.items(),
            key=lambda x: abs(np.log(x[1])),  # Sắp theo log(HR) để thấy ảnh hưởng
            reverse=True
        )[:5]

        hazard_ratios_list = []
        for feature, hr in hazard_ratios_sorted:
            hazard_ratios_list.append({
                'feature_code': feature,
                'feature_name': self.indicator_names[feature],
                'hazard_ratio': round(hr, 4),
                'log_hr': round(np.log(hr), 4),
                'interpretation': self._interpret_hazard_ratio(hr)
            })

        # Concordance index (C-index) từ Cox model
        c_index = self.cox_model.concordance_index_

        return {
            'num_samples': len(df_prepared),
            'num_events': df_prepared['default'].sum(),
            'num_censored': len(df_prepared) - df_prepared['default'].sum(),
            'c_index': round(c_index, 4),
            'top_hazard_ratios': hazard_ratios_list,
            'median_survival_time': self._calculate_median_survival_all()
        }

    def _interpret_hazard_ratio(self, hr: float) -> str:
        """
        Giải thích hazard ratio

        Args:
            hr: Hazard ratio

        Returns:
            Giải thích văn xuôi
        """
        if hr > 1.2:
            return f"Tăng {round((hr - 1) * 100, 1)}% nguy cơ vỡ nợ"
        elif hr < 0.8:
            return f"Giảm {round((1 - hr) * 100, 1)}% nguy cơ vỡ nợ"
        else:
            return "Ảnh hưởng không đáng kể"

    def _calculate_median_survival_all(self) -> Optional[float]:
        """
        Tính median survival time cho toàn bộ dữ liệu (Kaplan-Meier)

        Returns:
            Median survival time (tháng)
        """
        if self.km_model is None:
            return None

        try:
            median_time = self.km_model.median_survival_time_
            return round(median_time, 2) if not np.isnan(median_time) else None
        except:
            return None

    def predict_survival_curve(self, indicators: Dict[str, float], model_type: str = 'cox') -> Dict[str, Any]:
        """
        Dự báo survival curve cho DN mới

        Args:
            indicators: Dict chứa 14 chỉ số (X_1 → X_14)
            model_type: 'cox' hoặc 'rsf'

        Returns:
            Dict chứa:
            - survival_curve: List of {time, survival_prob}
            - median_time_to_default: Median time (tháng)
            - survival_at_6m, survival_at_12m, survival_at_24m
            - risk_level: 'Thấp', 'Trung bình', 'Cao'
        """
        if model_type == 'cox' and self.cox_model is None:
            raise ValueError("Cox model chưa được train.")
        if model_type == 'rsf' and self.rsf_model is None:
            raise ValueError("RSF model chưa được train.")

        # Chuẩn bị input
        X_new = pd.DataFrame([indicators])

        if model_type == 'cox':
            # Dự báo bằng Cox PH
            survival_func = self.cox_model.predict_survival_function(X_new)

            # Lấy survival curve
            times = survival_func.index.values
            survival_probs = survival_func.iloc[:, 0].values

        else:
            # Dự báo bằng RSF
            X_array = np.array([[indicators[f] for f in self.feature_names]])
            survival_funcs = self.rsf_model.predict_survival_function(X_array)

            # Lấy survival curve
            times = survival_funcs[0].x
            survival_probs = survival_funcs[0].y

        # Tạo survival curve data
        survival_curve = []
        for t, prob in zip(times, survival_probs):
            survival_curve.append({
                'time': round(float(t), 2),
                'survival_prob': round(float(prob), 4)
            })

        # Tính median time-to-default
        median_time = self._calculate_median_time(times, survival_probs)

        # Tính survival probability tại 6/12/24 tháng
        survival_at_6m = self._interpolate_survival(times, survival_probs, 6)
        survival_at_12m = self._interpolate_survival(times, survival_probs, 12)
        survival_at_24m = self._interpolate_survival(times, survival_probs, 24)

        # Phân loại risk level
        risk_level, risk_level_color, risk_level_icon = self._classify_risk_level(median_time)

        return {
            'survival_curve': survival_curve,
            'median_time_to_default': median_time,
            'survival_at_6m': survival_at_6m,
            'survival_at_12m': survival_at_12m,
            'survival_at_24m': survival_at_24m,
            'risk_level': risk_level,
            'risk_level_color': risk_level_color,
            'risk_level_icon': risk_level_icon,
            'model_type': model_type
        }

    def _calculate_median_time(self, times: np.ndarray, survival_probs: np.ndarray) -> Optional[float]:
        """
        Tính median time-to-default từ survival curve

        Args:
            times: Mảng thời gian
            survival_probs: Mảng survival probability

        Returns:
            Median time (tháng)
        """
        # Tìm thời điểm survival prob = 0.5
        try:
            idx = np.where(survival_probs <= 0.5)[0]
            if len(idx) > 0:
                return round(float(times[idx[0]]), 2)
            else:
                # Nếu survival prob luôn > 0.5 → median > max time
                return None
        except:
            return None

    def _interpolate_survival(self, times: np.ndarray, survival_probs: np.ndarray, target_time: float) -> float:
        """
        Interpolate survival probability tại target_time

        Args:
            times: Mảng thời gian
            survival_probs: Mảng survival probability
            target_time: Thời điểm cần tính (tháng)

        Returns:
            Survival probability tại target_time
        """
        try:
            return round(float(np.interp(target_time, times, survival_probs)), 4)
        except:
            return 0.0

    def _classify_risk_level(self, median_time: Optional[float]) -> tuple:
        """
        Phân loại risk level dựa vào median time

        Args:
            median_time: Median time-to-default (tháng)

        Returns:
            (risk_level, risk_level_color, risk_level_icon)
        """
        if median_time is None:
            return ("Rủi ro Thấp", "#10B981", "🟢")

        if median_time < 12:
            return ("Rủi ro Rất Cao", "#EF4444", "🔴")
        elif median_time < 18:
            return ("Rủi ro Cao", "#F59E0B", "🟠")
        elif median_time < 24:
            return ("Rủi ro Trung bình", "#FCD34D", "🟡")
        else:
            return ("Rủi ro Thấp", "#10B981", "🟢")

    def compare_survival_curves(self, indicators_list: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        So sánh survival curves của nhiều DN

        Args:
            indicators_list: List of Dict chứa 14 chỉ số

        Returns:
            Dict chứa danh sách survival curves để vẽ chart
        """
        if self.cox_model is None:
            raise ValueError("Cox model chưa được train.")

        comparison_data = []

        for i, indicators in enumerate(indicators_list):
            result = self.predict_survival_curve(indicators, model_type='cox')
            comparison_data.append({
                'name': f'DN #{i+1}',
                'survival_curve': result['survival_curve'],
                'median_time': result['median_time_to_default'],
                'risk_level': result['risk_level']
            })

        return {
            'comparison_data': comparison_data
        }

    def get_hazard_ratios(self) -> List[Dict[str, Any]]:
        """
        Lấy hazard ratios của tất cả 14 chỉ số

        Returns:
            List of Dict chứa hazard ratios
        """
        if self.cox_model is None:
            raise ValueError("Cox model chưa được train.")

        hazard_ratios_list = []
        for feature in self.feature_names:
            hr = self.hazard_ratios.get(feature, 1.0)
            hazard_ratios_list.append({
                'feature_code': feature,
                'feature_name': self.indicator_names[feature],
                'hazard_ratio': round(hr, 4),
                'log_hr': round(np.log(hr), 4),
                'interpretation': self._interpret_hazard_ratio(hr)
            })

        # Sắp xếp theo |log(HR)|
        hazard_ratios_list.sort(key=lambda x: abs(x['log_hr']), reverse=True)

        return hazard_ratios_list

    def generate_gemini_analysis(
        self,
        indicators: Dict[str, float],
        survival_result: Dict[str, Any],
        gemini_api_key: str
    ) -> str:
        """
        Tạo phân tích bằng Gemini AI

        Args:
            indicators: Dict chứa 14 chỉ số
            survival_result: Kết quả dự báo survival
            gemini_api_key: Gemini API key

        Returns:
            analysis: Phân tích văn xuôi (tiếng Việt)
        """
        try:
            import google.generativeai as genai

            # Cấu hình Gemini API
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')

            median_time = survival_result.get('median_time_to_default')
            median_str = f"{median_time} tháng" if median_time else "Trên 36 tháng"

            # Tạo prompt chi tiết
            prompt = f"""
Bạn là chuyên gia phân tích rủi ro tín dụng của Agribank, chuyên về Survival Analysis (Phân tích Sống Sót). Hãy phân tích kết quả dưới đây.

**THÔNG TIN DOANH NGHIỆP:**

**14 CHỈ SỐ TÀI CHÍNH:**
"""

            # Thêm 14 chỉ số
            for feature in self.feature_names:
                prompt += f"- {self.indicator_names[feature]} ({feature}): {indicators[feature]:.4f}\n"

            prompt += f"""

**KẾT QUẢ PHÂN TÍCH SỐNG SÓT:**

**Median Time-to-Default:** {median_str}
**Xác suất Sống sót tại 6 tháng:** {survival_result.get('survival_at_6m', 0) * 100:.2f}%
**Xác suất Sống sót tại 12 tháng:** {survival_result.get('survival_at_12m', 0) * 100:.2f}%
**Xác suất Sống sót tại 24 tháng:** {survival_result.get('survival_at_24m', 0) * 100:.2f}%
**Mức rủi ro:** {survival_result.get('risk_level')}

**YÊU CẦU PHÂN TÍCH:**

Hãy viết báo cáo phân tích chi tiết (300-400 từ, tiếng Việt, Markdown) với cấu trúc sau:

## 📊 TỔNG QUAN SURVIVAL ANALYSIS

(2-3 câu mô tả kết quả phân tích sống sót của doanh nghiệp)

## ⏱️ PHÂN TÍCH TIME-TO-DEFAULT

### Median Time-to-Default
(Phân tích ý nghĩa của median time: {median_str})

### Survival Probability theo Thời gian
(Phân tích xác suất sống sót tại 6/12/24 tháng)

## 📈 ĐÁNH GIÁ CÁC CHỈ SỐ QUAN TRỌNG

(Phân tích 3-4 chỉ số tài chính quan trọng nhất ảnh hưởng đến time-to-default)

## 💡 KHUYẾN NGHỊ

### Đối với Ngân hàng
(2-3 khuyến nghị cụ thể về quyết định tín dụng, hạn mức, kỳ hạn vay)

### Đối với Doanh nghiệp
(2-3 khuyến nghị giúp cải thiện survival probability)

## ⚠️ CẢNH BÁO

(Nếu median time < 12 tháng, đưa ra cảnh báo rủi ro cao và các biện pháp khẩn cấp)

---
**Lưu ý:** Viết ngắn gọn, chuyên nghiệp, dễ hiểu. Tập trung vào insights và actionable recommendations.
"""

            # Gọi Gemini API
            response = model.generate_content(prompt)
            analysis = response.text

            return analysis

        except Exception as e:
            return f"Lỗi khi gọi Gemini API: {str(e)}"

    def save_models(self, filepath_prefix: str = "survival_models"):
        """
        Lưu models vào file

        Args:
            filepath_prefix: Prefix cho tên file
        """
        # Lưu Cox model
        with open(f"{filepath_prefix}_cox.pkl", 'wb') as f:
            pickle.dump(self.cox_model, f)

        # Lưu RSF model
        with open(f"{filepath_prefix}_rsf.pkl", 'wb') as f:
            pickle.dump(self.rsf_model, f)

        # Lưu KM model
        with open(f"{filepath_prefix}_km.pkl", 'wb') as f:
            pickle.dump(self.km_model, f)

        # Lưu hazard ratios
        with open(f"{filepath_prefix}_hazards.pkl", 'wb') as f:
            pickle.dump(self.hazard_ratios, f)

        print(f"✅ Models saved to {filepath_prefix}_*.pkl")

    def load_models(self, filepath_prefix: str = "survival_models"):
        """
        Load models từ file

        Args:
            filepath_prefix: Prefix cho tên file
        """
        # Load Cox model
        with open(f"{filepath_prefix}_cox.pkl", 'rb') as f:
            self.cox_model = pickle.load(f)

        # Load RSF model
        with open(f"{filepath_prefix}_rsf.pkl", 'rb') as f:
            self.rsf_model = pickle.load(f)

        # Load KM model
        with open(f"{filepath_prefix}_km.pkl", 'rb') as f:
            self.km_model = pickle.load(f)

        # Load hazard ratios
        with open(f"{filepath_prefix}_hazards.pkl", 'rb') as f:
            self.hazard_ratios = pickle.load(f)

        print(f"✅ Models loaded from {filepath_prefix}_*.pkl")


# Khởi tạo singleton instance
survival_system = SurvivalAnalysisSystem()
