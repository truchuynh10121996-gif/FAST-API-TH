"""
Gemini API Module - Tích hợp Google Gemini để phân tích kết quả dự báo PD
"""

import os
from typing import Dict, Any
import google.generativeai as genai


class GeminiAnalyzer:
    """Class để tích hợp Gemini API phân tích kết quả dự báo rủi ro tín dụng"""

    def __init__(self, api_key: str = None):
        """
        Khởi tạo Gemini API

        Args:
            api_key: API key của Google Gemini. Nếu không truyền, sẽ lấy từ biến môi trường GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Không tìm thấy GEMINI_API_KEY. Vui lòng cung cấp API key hoặc set biến môi trường.")

        # Cấu hình Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def analyze_credit_risk(self, prediction_data: Dict[str, Any]) -> str:
        """
        Phân tích kết quả dự báo rủi ro tín dụng bằng Gemini

        Args:
            prediction_data: Dict chứa thông tin dự báo (PD, chỉ số tài chính, v.v.)

        Returns:
            Kết quả phân tích dạng text từ Gemini
        """
        # Tạo prompt chi tiết
        prompt = self._create_analysis_prompt(prediction_data)

        try:
            # Gọi Gemini API
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Lỗi khi gọi Gemini API: {str(e)}"

    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """
        Tạo prompt chi tiết để gửi tới Gemini

        Args:
            data: Dữ liệu dự báo bao gồm PD và 14 chỉ số tài chính

        Returns:
            Prompt string
        """
        # Lấy thông tin PD
        prediction = data.get('prediction', {})
        pd_stacking = prediction.get('pd_stacking', 0) * 100
        pd_logistic = prediction.get('pd_logistic', 0) * 100
        pd_rf = prediction.get('pd_random_forest', 0) * 100
        pd_xgboost = prediction.get('pd_xgboost', 0) * 100
        prediction_label = prediction.get('prediction_label', 'N/A')

        # Lấy 14 chỉ số
        indicators_dict = data.get('indicators_dict', {})

        # Phân loại rủi ro theo 5 cấp độ
        if pd_stacking < 2:
            risk_level = "RỦI RO RẤT THẤP 🟢 (AAA-AA)"
            risk_desc = "doanh nghiệp xuất sắc, tình hình tài chính rất tốt"
            rating = "AAA-AA"
        elif pd_stacking < 5:
            risk_level = "RỦI RO THẤP 🟢 (A-BBB)"
            risk_desc = "doanh nghiệp tốt, tình hình tài chính ổn định"
            rating = "A-BBB"
        elif pd_stacking < 10:
            risk_level = "RỦI RO TRUNG BÌNH 🟡 (BB)"
            risk_desc = "doanh nghiệp cần theo dõi thêm"
            rating = "BB"
        elif pd_stacking < 20:
            risk_level = "RỦI RO CAO 🟠 (B)"
            risk_desc = "doanh nghiệp có rủi ro đáng kể, cần thận trọng"
            rating = "B"
        else:
            risk_level = "RỦI RO RẤT CAO 🔴 (CCC-D)"
            risk_desc = "doanh nghiệp có nguy cơ vỡ nợ rất cao"
            rating = "CCC-D"

        # Tạo chuỗi hiển thị 14 chỉ số
        indicators_str = f"""
X_1 (Hệ số biên lợi nhuận gộp): {indicators_dict.get('X_1', 0):.4f}
X_2 (Hệ số biên lợi nhuận trước thuế): {indicators_dict.get('X_2', 0):.4f}
X_3 (ROA): {indicators_dict.get('X_3', 0):.4f}
X_4 (ROE): {indicators_dict.get('X_4', 0):.4f}
X_5 (Hệ số nợ trên tài sản): {indicators_dict.get('X_5', 0):.4f}
X_6 (Hệ số nợ trên vốn CSH): {indicators_dict.get('X_6', 0):.4f}
X_7 (Khả năng thanh toán hiện hành): {indicators_dict.get('X_7', 0):.4f}
X_8 (Khả năng thanh toán nhanh): {indicators_dict.get('X_8', 0):.4f}
X_9 (Hệ số khả năng trả lãi): {indicators_dict.get('X_9', 0):.4f}
X_10 (Hệ số khả năng trả nợ gốc): {indicators_dict.get('X_10', 0):.4f}
X_11 (Khả năng tạo tiền/Vốn CSH): {indicators_dict.get('X_11', 0):.4f}
X_12 (Vòng quay hàng tồn kho): {indicators_dict.get('X_12', 0):.4f}
X_13 (Kỳ thu tiền bình quân - ngày): {indicators_dict.get('X_13', 0):.2f}
X_14 (Hiệu suất sử dụng tài sản): {indicators_dict.get('X_14', 0):.4f}
"""

        prompt = f"""
Bạn là một chuyên gia phân tích rủi ro tín dụng của Agribank với hơn 20 năm kinh nghiệm.

Dựa trên kết quả dự báo xác suất vỡ nợ (PD) từ mô hình AI Stacking Classifier và 14 chỉ số tài chính của doanh nghiệp, hãy phân tích chi tiết và đưa ra khuyến nghị rõ ràng.

**HỆ THỐNG PHÂN LOẠI TÍN DỤNG (5 CẤP ĐỘ):**
- < 2%: Rất thấp (AAA-AA) - Doanh nghiệp xuất sắc
- 2-5%: Thấp (A-BBB) - Doanh nghiệp tốt
- 5-10%: Trung bình (BB) - Cần theo dõi
- 10-20%: Cao (B) - Rủi ro đáng kể
- > 20%: Rất cao (CCC-D) - Nguy cơ vỡ nợ cao

**KẾT QUẢ DỰ BÁO:**
- Xác suất Vỡ nợ (PD) - Stacking Model: {pd_stacking:.2f}%
- Xác suất Vỡ nợ (PD) - Logistic Regression: {pd_logistic:.2f}%
- Xác suất Vỡ nợ (PD) - Random Forest: {pd_rf:.2f}%
- Xác suất Vỡ nợ (PD) - XGBoost: {pd_xgboost:.2f}%
- Dự đoán: {prediction_label}
- Mức độ rủi ro: {risk_level}
- Credit Rating: {rating}

**14 CHỈ SỐ TÀI CHÍNH:**
{indicators_str}

**YÊU CẦU PHÂN TÍCH:**

Hãy phân tích theo cấu trúc sau (bằng tiếng Việt, chuyên nghiệp):

1. **Tổng quan rủi ro**: Đánh giá tổng thể về tình hình tài chính và khả năng trả nợ của doanh nghiệp

2. **Phân tích 14 chỉ số**:
   - Đánh giá các chỉ số khả năng sinh lời (X_1, X_2, X_3, X_4)
   - Phân tích khả năng thanh toán và đòn bẩy tài chính (X_5, X_6, X_7, X_8)
   - Đánh giá khả năng trả nợ và tạo tiền (X_9, X_10, X_11)
   - Phân tích hiệu quả hoạt động (X_12, X_13, X_14)
   - Chỉ ra những chỉ số TỐT và chỉ số CẦN CẢI THIỆN

3. **So sánh PD từ 4 models**:
   - Mức độ đồng thuận giữa các models
   - Giải thích sự khác biệt (nếu có)

4. **KHUYẾN NGHỊ CUỐI CÙNG** (QUAN TRỌNG):
   - Quyết định: **CHO VAY** hoặc **KHÔNG CHO VAY**
   - Giải thích lý do quyết định
   - Nếu cho vay: Đề xuất điều kiện và hạn mức phù hợp
   - Nếu không cho vay: Đề xuất doanh nghiệp cần cải thiện gì

5. **Lưu ý**: Các yếu tố cần theo dõi và giám sát

Hãy trình bày rõ ràng, dễ hiểu, có cấu trúc. Tối đa 500 từ.
"""

        return prompt


# Khởi tạo instance global
gemini_analyzer = None


def get_gemini_analyzer(api_key: str = None) -> GeminiAnalyzer:
    """
    Lấy instance của GeminiAnalyzer (singleton pattern)

    Args:
        api_key: API key của Gemini

    Returns:
        GeminiAnalyzer instance
    """
    global gemini_analyzer
    if gemini_analyzer is None:
        gemini_analyzer = GeminiAnalyzer(api_key)
    return gemini_analyzer
