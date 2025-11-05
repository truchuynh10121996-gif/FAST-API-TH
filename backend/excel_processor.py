"""
Module xử lý file XLSX và tính toán 14 chỉ số tài chính
File XLSX phải có 3 sheets: CDKT (Cân đối kế toán), BCTN (Báo cáo thu nhập), LCTT (Lưu chuyển tiền tệ)
"""

import pandas as pd
from typing import Dict, Any
import numpy as np
import re


class ExcelProcessor:
    """Class xử lý file XLSX và tính toán 14 chỉ số tài chính"""

    def __init__(self):
        self.cdkt_df = None  # Cân đối kế toán
        self.bctn_df = None  # Báo cáo thu nhập
        self.lctt_df = None  # Lưu chuyển tiền tệ
        self.financial_indicators = {}

    def read_excel(self, file_path: str) -> bool:
        """
        Đọc file XLSX với 3 sheets

        Args:
            file_path: Đường dẫn file XLSX

        Returns:
            True nếu đọc thành công, False nếu thất bại
        """
        try:
            # Đọc 3 sheets với context manager để đảm bảo file được đóng
            with pd.ExcelFile(file_path) as excel_file:
                # Kiểm tra các sheet cần thiết
                required_sheets = ['CDKT', 'BCTN', 'LCTT']
                available_sheets = excel_file.sheet_names

                missing_sheets = [sheet for sheet in required_sheets if sheet not in available_sheets]
                if missing_sheets:
                    raise ValueError(f"Thiếu các sheet: {', '.join(missing_sheets)}. File phải có 3 sheets: CDKT, BCTN, LCTT")

                # Đọc dữ liệu từng sheet
                self.cdkt_df = excel_file.parse('CDKT')
                self.bctn_df = excel_file.parse('BCTN')
                self.lctt_df = excel_file.parse('LCTT')

            return True

        except Exception as e:
            raise ValueError(f"Lỗi khi đọc file XLSX: {str(e)}")

    def get_value_from_sheet(self, df: pd.DataFrame, indicator_name: str) -> float:
        """
        Lấy giá trị từ sheet dựa trên tên chỉ tiêu
        Giả định: Cột đầu tiên là tên chỉ tiêu, cột CUỐI CÙNG là giá trị năm gần nhất (2024)

        Args:
            df: DataFrame chứa dữ liệu
            indicator_name: Tên chỉ tiêu cần tìm

        Returns:
            Giá trị của chỉ tiêu
        """
        try:
            # Tìm trong cột đầu tiên (chỉ tiêu)
            col_name = df.columns[0]
            # THAY ĐỔI: Lấy cột CUỐI CÙNG thay vì cột thứ 2 (năm 2024 thay vì 2022)
            value_col = df.columns[-1] if len(df.columns) > 1 else df.columns[0]

            # Chuẩn hóa indicator_name để tìm kiếm tốt hơn
            # Loại bỏ số thứ tự ở đầu (VD: "1. Tiền" -> "tiền")
            search_name = indicator_name.lower().strip()
            # Loại bỏ các ký tự số và dấu chấm ở đầu
            search_name = re.sub(r'^\d+\.\s*', '', search_name)

            # Tìm dòng có chứa indicator_name (case-insensitive, loại bỏ khoảng trắng)
            # Áp dụng cùng chuẩn hóa cho từng dòng trong DataFrame
            def normalize_text(text):
                text = str(text).strip().lower()
                # Loại bỏ số thứ tự ở đầu
                text = re.sub(r'^\d+\.\s*', '', text)
                return text

            mask = df[col_name].apply(normalize_text).str.contains(
                search_name, na=False, regex=False
            )

            if mask.any():
                value = df.loc[mask, value_col].iloc[0]
                # Xử lý giá trị
                if pd.isna(value):
                    return 0.0

                # Chuyển đổi giá trị sang float - xử lý nhiều định dạng
                try:
                    # Nếu đã là số thì return luôn
                    if isinstance(value, (int, float)):
                        return float(value)

                    # Chuyển sang string để xử lý
                    value_str = str(value).strip()

                    # Loại bỏ các ký tự không phải số (trừ dấu âm và dấu thập phân)
                    # Xử lý format: "1,000,000.50" hoặc "1.000.000,50" hoặc "(1000)" (số âm)

                    # Kiểm tra nếu có dấu ngoặc đơn (số âm)
                    is_negative = False
                    if value_str.startswith('(') and value_str.endswith(')'):
                        is_negative = True
                        value_str = value_str[1:-1]

                    # Kiểm tra nếu có dấu trừ
                    if value_str.startswith('-'):
                        is_negative = True
                        value_str = value_str[1:]

                    # Loại bỏ khoảng trắng, ký tự đặc biệt
                    value_str = value_str.replace(' ', '').replace('\xa0', '')

                    # Xác định dấu thập phân (dấu cuối cùng trong chuỗi)
                    # Nếu có cả dấu phẩy và dấu chấm, dấu nào xuất hiện sau là dấu thập phân
                    if ',' in value_str and '.' in value_str:
                        # Tìm vị trí cuối cùng của mỗi dấu
                        last_comma = value_str.rfind(',')
                        last_dot = value_str.rfind('.')

                        if last_comma > last_dot:
                            # Dấu phẩy là thập phân (định dạng châu Âu: 1.000,50)
                            value_str = value_str.replace('.', '').replace(',', '.')
                        else:
                            # Dấu chấm là thập phân (định dạng Mỹ: 1,000.50)
                            value_str = value_str.replace(',', '')
                    elif ',' in value_str:
                        # Chỉ có dấu phẩy
                        # Kiểm tra xem có phải phân cách hàng nghìn không
                        parts = value_str.split(',')
                        if len(parts) == 2 and len(parts[1]) <= 2:
                            # Có thể là thập phân (VD: 1000,50)
                            value_str = value_str.replace(',', '.')
                        else:
                            # Là phân cách hàng nghìn (VD: 1,000,000)
                            value_str = value_str.replace(',', '')

                    # Chuyển sang float
                    float_value = float(value_str)

                    # Áp dụng dấu âm nếu cần
                    if is_negative:
                        float_value = -float_value

                    print(f"✅ Tìm thấy '{indicator_name}': {float_value}")
                    return float_value

                except (ValueError, AttributeError) as e:
                    print(f"⚠️ Không thể chuyển đổi giá trị '{value}' cho '{indicator_name}': {str(e)}")
                    return 0.0
            else:
                print(f"⚠️ Không tìm thấy chỉ tiêu '{indicator_name}' trong sheet")
                return 0.0

        except Exception as e:
            print(f"❌ Lỗi khi lấy giá trị {indicator_name}: {str(e)}")
            return 0.0

    def calculate_14_indicators(self) -> Dict[str, float]:
        """
        Tính toán 14 chỉ số tài chính từ 3 sheets

        Returns:
            Dict chứa 14 chỉ số X_1 đến X_14
        """
        if self.cdkt_df is None or self.bctn_df is None or self.lctt_df is None:
            raise ValueError("Chưa đọc dữ liệu từ file XLSX. Vui lòng gọi read_excel() trước.")

        # Lấy các chỉ tiêu từ BCTN (Báo cáo thu nhập)
        doanh_thu_thuan = self.get_value_from_sheet(self.bctn_df, "doanh thu thuần")
        if doanh_thu_thuan == 0:
            doanh_thu_thuan = self.get_value_from_sheet(self.bctn_df, "doanh thu bán")

        loi_nhuan_gop = self.get_value_from_sheet(self.bctn_df, "lợi nhuận gộp")
        loi_nhuan_truoc_thue = self.get_value_from_sheet(self.bctn_df, "lợi nhuận trước thuế")
        gia_von_hang_ban = self.get_value_from_sheet(self.bctn_df, "giá vốn")

        # Lấy các chỉ tiêu từ CDKT (Cân đối kế toán)
        # Lấy giá trị đầu kỳ và cuối kỳ nếu có, nếu không thì lấy giá trị hiện tại
        tong_tai_san = self.get_value_from_sheet(self.cdkt_df, "tổng tài sản")
        tai_san_dau_ky = self.get_value_from_sheet(self.cdkt_df, "tổng tài sản đầu")
        if tai_san_dau_ky == 0:
            tai_san_dau_ky = tong_tai_san * 0.9  # Giả định giảm 10% so với cuối kỳ
        binh_quan_tong_tai_san = (tong_tai_san + tai_san_dau_ky) / 2

        von_chu_so_huu = self.get_value_from_sheet(self.cdkt_df, "vốn chủ sở hữu")
        vcsh_dau_ky = self.get_value_from_sheet(self.cdkt_df, "vốn chủ sở hữu đầu")
        if vcsh_dau_ky == 0:
            vcsh_dau_ky = von_chu_so_huu * 0.9
        binh_quan_von_chu_so_huu = (von_chu_so_huu + vcsh_dau_ky) / 2

        no_phai_tra = self.get_value_from_sheet(self.cdkt_df, "nợ phải trả")
        if no_phai_tra == 0:
            no_phai_tra = self.get_value_from_sheet(self.cdkt_df, "tổng nợ")

        tai_san_ngan_han = self.get_value_from_sheet(self.cdkt_df, "tài sản ngắn hạn")
        no_ngan_han = self.get_value_from_sheet(self.cdkt_df, "nợ ngắn hạn")
        hang_ton_kho = self.get_value_from_sheet(self.cdkt_df, "hàng tồn kho")

        htk_dau_ky = self.get_value_from_sheet(self.cdkt_df, "hàng tồn kho đầu")
        if htk_dau_ky == 0:
            htk_dau_ky = hang_ton_kho * 0.9
        binh_quan_hang_ton_kho = (hang_ton_kho + htk_dau_ky) / 2

        lai_vay = self.get_value_from_sheet(self.bctn_df, "lãi vay")
        if lai_vay == 0:
            lai_vay = self.get_value_from_sheet(self.bctn_df, "chi phí lãi")

        no_dai_han_den_han = self.get_value_from_sheet(self.cdkt_df, "nợ dài hạn đến hạn")
        khau_hao = self.get_value_from_sheet(self.bctn_df, "khấu hao")

        tien_va_tuong_duong = self.get_value_from_sheet(self.cdkt_df, "tiền")
        if tien_va_tuong_duong == 0:
            tien_va_tuong_duong = self.get_value_from_sheet(self.cdkt_df, "tiền và tương đương")

        khoan_phai_thu = self.get_value_from_sheet(self.cdkt_df, "phải thu")
        kpt_dau_ky = self.get_value_from_sheet(self.cdkt_df, "phải thu đầu")
        if kpt_dau_ky == 0:
            kpt_dau_ky = khoan_phai_thu * 0.9
        binh_quan_phai_thu = (khoan_phai_thu + kpt_dau_ky) / 2

        # Tính 14 chỉ số
        indicators = {}

        # X_1: Hệ số biên lợi nhuận gộp
        indicators['X_1'] = loi_nhuan_gop / doanh_thu_thuan if doanh_thu_thuan != 0 else 0

        # X_2: Hệ số biên lợi nhuận trước thuế
        indicators['X_2'] = loi_nhuan_truoc_thue / doanh_thu_thuan if doanh_thu_thuan != 0 else 0

        # X_3: Tỷ suất lợi nhuận trước thuế trên tổng tài sản (ROA)
        indicators['X_3'] = loi_nhuan_truoc_thue / binh_quan_tong_tai_san if binh_quan_tong_tai_san != 0 else 0

        # X_4: Tỷ suất lợi nhuận trước thuế trên vốn chủ sở hữu (ROE)
        indicators['X_4'] = loi_nhuan_truoc_thue / binh_quan_von_chu_so_huu if binh_quan_von_chu_so_huu != 0 else 0

        # X_5: Hệ số nợ trên tài sản
        indicators['X_5'] = no_phai_tra / tong_tai_san if tong_tai_san != 0 else 0

        # X_6: Hệ số nợ trên vốn chủ sở hữu
        indicators['X_6'] = no_phai_tra / von_chu_so_huu if von_chu_so_huu != 0 else 0

        # X_7: Khả năng thanh toán hiện hành
        indicators['X_7'] = tai_san_ngan_han / no_ngan_han if no_ngan_han != 0 else 0

        # X_8: Khả năng thanh toán nhanh
        indicators['X_8'] = (tai_san_ngan_han - hang_ton_kho) / no_ngan_han if no_ngan_han != 0 else 0

        # X_9: Hệ số khả năng trả lãi
        lntt_cong_lai_vay = loi_nhuan_truoc_thue + lai_vay
        indicators['X_9'] = lntt_cong_lai_vay / lai_vay if lai_vay != 0 else 0

        # X_10: Hệ số khả năng trả nợ gốc
        tu_so_x10 = lntt_cong_lai_vay + khau_hao
        mau_so_x10 = lai_vay + no_dai_han_den_han
        indicators['X_10'] = tu_so_x10 / mau_so_x10 if mau_so_x10 != 0 else 0

        # X_11: Hệ số khả năng tạo tiền trên vốn chủ sở hữu
        indicators['X_11'] = tien_va_tuong_duong / von_chu_so_huu if von_chu_so_huu != 0 else 0

        # X_12: Vòng quay hàng tồn kho
        indicators['X_12'] = gia_von_hang_ban / binh_quan_hang_ton_kho if binh_quan_hang_ton_kho != 0 else 0

        # X_13: Kỳ thu tiền bình quân
        indicators['X_13'] = 365 / (doanh_thu_thuan / binh_quan_phai_thu) if (doanh_thu_thuan != 0 and binh_quan_phai_thu != 0) else 0

        # X_14: Hiệu suất sử dụng tài sản
        indicators['X_14'] = doanh_thu_thuan / binh_quan_tong_tai_san if binh_quan_tong_tai_san != 0 else 0

        # Làm tròn kết quả
        for key in indicators:
            indicators[key] = round(indicators[key], 6)

        self.financial_indicators = indicators
        return indicators

    def get_indicators_with_names(self) -> Dict[str, Any]:
        """
        Lấy 14 chỉ số kèm tên đầy đủ

        Returns:
            Dict chứa thông tin chi tiết về 14 chỉ số
        """
        indicator_names = {
            'X_1': 'Hệ số biên lợi nhuận gộp',
            'X_2': 'Hệ số biên lợi nhuận trước thuế',
            'X_3': 'Tỷ suất lợi nhuận trước thuế trên tổng tài sản (ROA)',
            'X_4': 'Tỷ suất lợi nhuận trước thuế trên vốn chủ sở hữu (ROE)',
            'X_5': 'Hệ số nợ trên tài sản',
            'X_6': 'Hệ số nợ trên vốn chủ sở hữu',
            'X_7': 'Khả năng thanh toán hiện hành',
            'X_8': 'Khả năng thanh toán nhanh',
            'X_9': 'Hệ số khả năng trả lãi',
            'X_10': 'Hệ số khả năng trả nợ gốc',
            'X_11': 'Hệ số khả năng tạo tiền trên vốn chủ sở hữu',
            'X_12': 'Vòng quay hàng tồn kho',
            'X_13': 'Kỳ thu tiền bình quân',
            'X_14': 'Hiệu suất sử dụng tài sản'
        }

        result = []
        for key, value in self.financial_indicators.items():
            result.append({
                'code': key,
                'name': indicator_names[key],
                'value': value
            })

        return result


# Khởi tạo instance global
excel_processor = ExcelProcessor()
