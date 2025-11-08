"""
FastAPI Backend - Hệ thống Đánh giá Rủi ro Tín dụng
Endpoints: /train, /predict, /predict-from-xlsx, /analyze, /export-report
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()  # Tải các biến môi trường từ file .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import pandas as pd
import os
import tempfile
from datetime import datetime
from model import credit_model
from gemini_api import get_gemini_analyzer
from excel_processor import excel_processor
from report_generator import ReportGenerator

# Khởi tạo FastAPI app
app = FastAPI(
    title="Credit Risk Assessment API",
    description="API đánh giá rủi ro tín dụng sử dụng Stacking Classifier",
    version="1.0.0"
)

# Cấu hình CORS để frontend Vue có thể gọi API
# Development: cho phép localhost:3000 (frontend Vue)
# Production: thay đổi origins theo domain thật
origins = [
    "http://localhost:3000",      # Vue dev server
    "http://localhost:5173",      # Vite alternative port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:3005",
    "http://127.0.0.1:3005",
    # Thêm domain production khi deploy:
    # "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ================================================================================================
# PYDANTIC MODELS
# ================================================================================================

class PredictionInput(BaseModel):
    """Model cho input dự báo (14 chỉ số X1-X14)"""
    X_1: float
    X_2: float
    X_3: float
    X_4: float
    X_5: float
    X_6: float
    X_7: float
    X_8: float
    X_9: float
    X_10: float
    X_11: float
    X_12: float
    X_13: float
    X_14: float


class GeminiAPIKeyRequest(BaseModel):
    """Model cho request set Gemini API key"""
    api_key: str


# ================================================================================================
# ENDPOINTS
# ================================================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Credit Risk Assessment API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/train")
async def train_model(file: UploadFile = File(...)):
    """
    Endpoint huấn luyện mô hình từ file CSV

    Args:
        file: File CSV chứa dữ liệu huấn luyện (phải có cột X_1 đến X_14 và cột 'default')

    Returns:
        Dict chứa thông tin huấn luyện và metrics
    """
    try:
        # Kiểm tra file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File phải có định dạng CSV")

        # Lưu file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Huấn luyện mô hình
        result = credit_model.train(tmp_file_path)

        # Lưu mô hình
        credit_model.save_model("model_stacking.pkl")

        # Xóa file tạm
        os.unlink(tmp_file_path)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi huấn luyện mô hình: {str(e)}")


@app.post("/predict")
async def predict(input_data: PredictionInput):
    """
    Endpoint dự báo PD từ 14 chỉ số tài chính

    Args:
        input_data: Dict chứa 14 chỉ số X_1 đến X_14

    Returns:
        Dict chứa PD từ 4 models và kết quả dự đoán
    """
    try:
        # Kiểm tra mô hình đã được train chưa
        if credit_model.model is None:
            # Thử load model từ file
            if os.path.exists("model_stacking.pkl"):
                credit_model.load_model("model_stacking.pkl")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Mô hình chưa được huấn luyện. Vui lòng upload file CSV để huấn luyện trước."
                )

        # Chuyển input thành DataFrame
        input_dict = input_data.dict()
        X_new = pd.DataFrame([input_dict])

        # Dự báo
        result = credit_model.predict(X_new)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự báo: {str(e)}")


@app.post("/predict-from-xlsx")
async def predict_from_xlsx(file: UploadFile = File(...)):
    """
    Endpoint dự báo PD từ file XLSX (3 sheets: CDKT, BCTN, LCTT)
    Tự động tính 14 chỉ số và chạy mô hình dự báo

    Args:
        file: File XLSX chứa 3 sheets (CDKT, BCTN, LCTT)

    Returns:
        Dict chứa 14 chỉ số và kết quả dự báo PD
    """
    try:
        # Kiểm tra file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File phải có định dạng XLSX hoặc XLS")

        # Kiểm tra mô hình đã được train chưa
        if credit_model.model is None:
            if os.path.exists("model_stacking.pkl"):
                credit_model.load_model("model_stacking.pkl")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Mô hình chưa được huấn luyện. Vui lòng upload file CSV để huấn luyện trước."
                )

        # Lưu file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Đọc file XLSX
            excel_processor.read_excel(tmp_file_path)

            # Tính 14 chỉ số
            indicators = excel_processor.calculate_14_indicators()
            indicators_with_names = excel_processor.get_indicators_with_names()

            # Chuyển thành DataFrame để dự báo
            X_new = pd.DataFrame([indicators])

            # Dự báo PD
            prediction_result = credit_model.predict(X_new)

            # Trả về kết quả
            return {
                "status": "success",
                "indicators": indicators_with_names,
                "indicators_dict": indicators,
                "prediction": prediction_result
            }
        finally:
            # Xóa file tạm trong finally block để đảm bảo file luôn được xóa
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass  # Bỏ qua lỗi khi xóa file

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file XLSX: {str(e)}")


@app.post("/analyze")
async def analyze_with_gemini(request_data: Dict[str, Any]):
    """
    Endpoint phân tích kết quả dự báo bằng Gemini API

    Args:
        request_data: Dict chứa kết quả dự báo và 14 chỉ số

    Returns:
        Dict chứa kết quả phân tích từ Gemini và khuyến nghị
    """
    try:
        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Phân tích
        analysis = analyzer.analyze_credit_risk(request_data)

        return {
            "status": "success",
            "analysis": analysis
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích bằng Gemini: {str(e)}")


@app.post("/analyze-industry")
async def analyze_industry(request_data: Dict[str, Any]):
    """
    Endpoint phân tích ngành nghề bằng Gemini API

    Args:
        request_data: Dict chứa industry code và industry_name

    Returns:
        Dict chứa kết quả phân tích ngành và dữ liệu charts
    """
    try:
        industry = request_data.get('industry', '')
        industry_name = request_data.get('industry_name', '')

        if not industry or not industry_name:
            raise HTTPException(
                status_code=400,
                detail="Thiếu thông tin industry hoặc industry_name"
            )

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Phân tích ngành
        result = analyzer.analyze_industry(industry, industry_name)

        return {
            "status": "success",
            "analysis": result["analysis"],
            "charts": result.get("charts", [])
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích ngành: {str(e)}")


@app.post("/set-gemini-key")
async def set_gemini_key(request: GeminiAPIKeyRequest):
    """
    Endpoint để set Gemini API key

    Args:
        request: Dict chứa api_key

    Returns:
        Dict xác nhận
    """
    try:
        os.environ["GEMINI_API_KEY"] = request.api_key

        # Khởi tạo lại Gemini analyzer - cập nhật global instance
        from gemini_api import GeminiAnalyzer
        import gemini_api
        gemini_api.gemini_analyzer = GeminiAnalyzer(request.api_key)

        return {
            "status": "success",
            "message": "Gemini API key đã được set thành công"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi set Gemini API key: {str(e)}")


@app.post("/export-report")
async def export_report(report_data: Dict[str, Any]):
    """
    Endpoint xuất báo cáo Word

    Args:
        report_data: Dict chứa prediction, indicators, và analysis

    Returns:
        File Word báo cáo
    """
    try:
        # Tạo báo cáo
        report_gen = ReportGenerator()
        output_path = f"bao_cao_tin_dung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

        report_path = report_gen.generate_report(report_data, output_path)

        # Trả về file
        return FileResponse(
            path=report_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=output_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xuất báo cáo: {str(e)}")


@app.post("/fetch-industry-data")
async def fetch_industry_data(request_data: Dict[str, Any]):
    """
    Endpoint để AI lấy dữ liệu ngành nghề tự động

    Args:
        request_data: Dict chứa industry code và industry_name

    Returns:
        Dict chứa dữ liệu ngành nghề
    """
    try:
        industry = request_data.get('industry', '')
        industry_name = request_data.get('industry_name', '')

        if not industry or not industry_name:
            raise HTTPException(
                status_code=400,
                detail="Thiếu thông tin industry hoặc industry_name"
            )

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Lấy dữ liệu
        result = analyzer.fetch_industry_data(industry, industry_name)

        return {
            "status": "success",
            "data": result.get("data", {})
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu ngành: {str(e)}")


@app.post("/generate-charts")
async def generate_charts(request_data: Dict[str, Any]):
    """
    Endpoint tạo biểu đồ ECharts và phân tích sơ bộ

    Args:
        request_data: Dict chứa industry, industry_name, và data

    Returns:
        Dict chứa charts_data và brief_analysis
    """
    try:
        industry = request_data.get('industry', '')
        industry_name = request_data.get('industry_name', '')
        data = request_data.get('data', {})

        if not industry or not industry_name or not data:
            raise HTTPException(
                status_code=400,
                detail="Thiếu thông tin industry, industry_name hoặc data"
            )

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Tạo biểu đồ và phân tích
        result = analyzer.generate_charts_data(industry, industry_name, data)

        return {
            "status": "success",
            "charts_data": result.get("charts_data", []),
            "brief_analysis": result.get("brief_analysis", "")
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo biểu đồ: {str(e)}")


@app.post("/deep-analyze-industry")
async def deep_analyze_industry_endpoint(request_data: Dict[str, Any]):
    """
    Endpoint phân tích sâu ảnh hưởng của ngành đến quyết định cho vay

    Args:
        request_data: Dict chứa industry, industry_name, data, và brief_analysis

    Returns:
        Dict chứa deep_analysis
    """
    try:
        industry = request_data.get('industry', '')
        industry_name = request_data.get('industry_name', '')
        data = request_data.get('data', {})
        brief_analysis = request_data.get('brief_analysis', '')

        if not industry or not industry_name or not data:
            raise HTTPException(
                status_code=400,
                detail="Thiếu thông tin industry, industry_name hoặc data"
            )

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Phân tích sâu
        deep_analysis = analyzer.deep_analyze_industry(industry, industry_name, data, brief_analysis)

        return {
            "status": "success",
            "deep_analysis": deep_analysis
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích sâu: {str(e)}")


@app.post("/analyze-pd-with-industry")
async def analyze_pd_with_industry(request_data: Dict[str, Any]):
    """
    Endpoint phân tích PD kết hợp với ngành nghề

    Args:
        request_data: Dict chứa indicators_dict, industry, và industry_name

    Returns:
        Dict chứa phân tích chuyên sâu và charts_data
    """
    try:
        indicators_dict = request_data.get('indicators_dict', {})
        industry = request_data.get('industry', '')
        industry_name = request_data.get('industry_name', '')

        if not indicators_dict or not industry or not industry_name:
            raise HTTPException(
                status_code=400,
                detail="Thiếu thông tin indicators_dict, industry hoặc industry_name"
            )

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Phân tích PD kết hợp
        analysis = analyzer.analyze_pd_with_industry(indicators_dict, industry, industry_name)

        # Tạo biểu đồ từ 14 chỉ số
        charts_data = []

        # Biểu đồ 1: Radar chart cho 4 nhóm chỉ số chính
        charts_data.append({
            "title": {"text": "Tổng quan 14 Chỉ số Tài chính", "left": "center"},
            "tooltip": {},
            "radar": {
                "indicator": [
                    {"name": "Sinh lời (X1-X4)", "max": 1},
                    {"name": "Đòn bẩy (X5-X6)", "max": 5},
                    {"name": "Thanh toán (X7-X8)", "max": 5},
                    {"name": "Hiệu quả (X9-X14)", "max": 10}
                ]
            },
            "series": [{
                "type": "radar",
                "data": [{
                    "value": [
                        (indicators_dict.get('X_1', 0) + indicators_dict.get('X_2', 0) +
                         indicators_dict.get('X_3', 0) + indicators_dict.get('X_4', 0)) / 4,
                        (indicators_dict.get('X_5', 0) + indicators_dict.get('X_6', 0)) / 2,
                        (indicators_dict.get('X_7', 0) + indicators_dict.get('X_8', 0)) / 2,
                        (indicators_dict.get('X_9', 0) + indicators_dict.get('X_10', 0) +
                         indicators_dict.get('X_11', 0) + indicators_dict.get('X_12', 0) +
                         indicators_dict.get('X_14', 0)) / 5
                    ],
                    "name": "Chỉ số doanh nghiệp",
                    "areaStyle": {"color": "rgba(255, 107, 157, 0.3)"}
                }]
            }]
        })

        # Biểu đồ 2: Bar chart so sánh chỉ số sinh lời
        charts_data.append({
            "title": {"text": "Chỉ số Sinh lời (X1-X4)", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": ["Biên LN gộp (X1)", "Biên LN trước thuế (X2)", "ROA (X3)", "ROE (X4)"]
            },
            "yAxis": {"type": "value"},
            "series": [{
                "data": [
                    indicators_dict.get('X_1', 0),
                    indicators_dict.get('X_2', 0),
                    indicators_dict.get('X_3', 0),
                    indicators_dict.get('X_4', 0)
                ],
                "type": "bar",
                "itemStyle": {"color": "#10B981"},
                "label": {"show": True, "position": "top", "formatter": "{c}"}
            }]
        })

        # Biểu đồ 3: Bar chart chỉ số thanh toán & đòn bẩy
        charts_data.append({
            "title": {"text": "Thanh toán & Đòn bẩy (X5-X8)", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": ["Nợ/TS (X5)", "Nợ/VCSH (X6)", "TT hiện hành (X7)", "TT nhanh (X8)"]
            },
            "yAxis": {"type": "value"},
            "series": [{
                "data": [
                    indicators_dict.get('X_5', 0),
                    indicators_dict.get('X_6', 0),
                    indicators_dict.get('X_7', 0),
                    indicators_dict.get('X_8', 0)
                ],
                "type": "bar",
                "itemStyle": {"color": "#3B82F6"},
                "label": {"show": True, "position": "top", "formatter": "{c}"}
            }]
        })

        # Biểu đồ 4: Bar chart hiệu quả hoạt động
        charts_data.append({
            "title": {"text": "Hiệu quả Hoạt động (X9-X14)", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": ["Trả lãi (X9)", "Trả nợ gốc (X10)", "Tạo tiền (X11)",
                         "Vòng quay HTK (X12)", "Kỳ thu tiền (X13)", "Hiệu suất TS (X14)"]
            },
            "yAxis": {"type": "value"},
            "series": [{
                "data": [
                    indicators_dict.get('X_9', 0),
                    indicators_dict.get('X_10', 0),
                    indicators_dict.get('X_11', 0),
                    indicators_dict.get('X_12', 0),
                    indicators_dict.get('X_13', 0),
                    indicators_dict.get('X_14', 0)
                ],
                "type": "bar",
                "itemStyle": {"color": "#9C27B0"},
                "label": {"show": True, "position": "top", "formatter": "{c}"}
            }]
        })

        return {
            "status": "success",
            "analysis": analysis,
            "charts_data": charts_data
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích PD kết hợp: {str(e)}")


@app.get("/model-info")
async def get_model_info():
    """
    Endpoint lấy thông tin mô hình hiện tại

    Returns:
        Dict chứa thông tin mô hình
    """
    try:
        if credit_model.model is None:
            # Thử load model từ file
            if os.path.exists("model_stacking.pkl"):
                credit_model.load_model("model_stacking.pkl")
            else:
                return {
                    "status": "not_trained",
                    "message": "Mô hình chưa được huấn luyện"
                }

        return {
            "status": "trained",
            "message": "Mô hình đã sẵn sàng",
            "metrics_train": credit_model.metrics_in,
            "metrics_test": credit_model.metrics_out
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin mô hình: {str(e)}")


@app.post("/chat-assistant")
async def chat_assistant(data: Dict[str, Any]):
    """
    Endpoint chatbot - Trợ lý ảo trả lời câu hỏi về phân tích

    Args:
        data: Dict chứa question, context, indicators, prediction

    Returns:
        Dict chứa answer từ Gemini
    """
    try:
        question = data.get('question', '')
        context = data.get('context', '')
        indicators = data.get('indicators', {})
        prediction = data.get('prediction', {})

        if not question:
            raise HTTPException(status_code=400, detail="Thiếu câu hỏi (question)")

        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Tạo prompt cho chatbot
        prompt = f"""
Bạn là Trợ lý ảo chuyên nghiệp của Agribank, chuyên trả lời các câu hỏi về phân tích rủi ro tín dụng.

**BỐI CẢNH PHÂN TÍCH TRƯỚC ĐÓ:**
{context}

**14 CHỈ SỐ TÀI CHÍNH:**
{str(indicators)}

**KẾT QUẢ DỰ BÁO PD:**
{str(prediction)}

**CÂU HỎI CỦA NGƯỜI DÙNG:**
{question}

**YÊU CẦU TRẢ LỜI:**
- Trả lời ngắn gọn, chính xác, dễ hiểu (100-200 từ)
- Dựa trên bối cảnh phân tích và dữ liệu đã có
- Nếu câu hỏi liên quan đến chỉ số tài chính, giải thích rõ ràng
- Nếu câu hỏi về khuyến nghị, đưa ra lời khuyên cụ thể
- Sử dụng tiếng Việt chuyên nghiệp

Hãy trả lời câu hỏi:
"""

        # Gọi Gemini API
        response = analyzer.model.generate_content(prompt)
        answer = response.text

        return {
            "status": "success",
            "answer": answer
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý câu hỏi: {str(e)}")


@app.post("/simulate-scenario")
async def simulate_scenario(
    file: Optional[UploadFile] = File(None),
    indicators_json: Optional[str] = None,
    scenario_type: str = "mild",
    custom_revenue: float = 0,
    custom_interest: float = 0,
    custom_roe: float = 0,
    custom_cr: float = 0
):
    """
    Endpoint mô phỏng kịch bản xấu - Tính toán PD trước và sau khi áp dụng kịch bản

    Args:
        file: File XLSX (nếu tải file mới) - Optional
        indicators_json: JSON string chứa 14 chỉ số (nếu dùng dữ liệu từ Tab Dự báo PD) - Optional
        scenario_type: Loại kịch bản ("mild", "moderate", "crisis", "custom")
        custom_revenue: % thay đổi doanh thu (chỉ dùng khi scenario_type="custom")
        custom_interest: % thay đổi chi phí lãi vay (chỉ dùng khi scenario_type="custom")
        custom_roe: % thay đổi ROE (chỉ dùng khi scenario_type="custom")
        custom_cr: % thay đổi CR (chỉ dùng khi scenario_type="custom")

    Returns:
        Dict chứa:
        - indicators_before: 14 chỉ số trước khi áp kịch bản
        - indicators_after: 14 chỉ số sau khi áp kịch bản
        - prediction_before: PD trước khi áp kịch bản
        - prediction_after: PD sau khi áp kịch bản
        - pd_change_pct: % thay đổi PD
        - scenario_info: Thông tin về kịch bản đã áp dụng
    """
    try:
        import json

        # Kiểm tra mô hình đã được train chưa
        if credit_model.model is None:
            if os.path.exists("model_stacking.pkl"):
                credit_model.load_model("model_stacking.pkl")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Mô hình chưa được huấn luyện. Vui lòng upload file CSV để huấn luyện trước."
                )

        # 1. LẤY 14 CHỈ SỐ BAN ĐẦU (indicators_before)
        indicators_before = {}

        if file:
            # Trường hợp 1: Tải file XLSX mới
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(status_code=400, detail="File phải có định dạng XLSX hoặc XLS")

            # Lưu file tạm
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name

            try:
                # Đọc file XLSX và tính 14 chỉ số
                excel_processor.read_excel(tmp_file_path)
                indicators_before = excel_processor.calculate_14_indicators()
            finally:
                try:
                    os.unlink(tmp_file_path)
                except Exception:
                    pass

        elif indicators_json:
            # Trường hợp 2: Sử dụng dữ liệu từ Tab Dự báo PD
            indicators_before = json.loads(indicators_json)
        else:
            raise HTTPException(
                status_code=400,
                detail="Vui lòng cung cấp file XLSX hoặc dữ liệu từ Tab Dự báo PD"
            )

        # 2. XÁC ĐỊNH % BIẾN ĐỘNG THEO KỊCH BẢN
        scenario_configs = {
            "mild": {
                "name": "🟠 Kinh tế giảm nhẹ",
                "revenue_change": -5,
                "interest_change": 5,
                "roe_change": -5,
                "cr_change": -5
            },
            "moderate": {
                "name": "🔴 Cú sốc kinh tế trung bình",
                "revenue_change": -10,
                "interest_change": 10,
                "roe_change": -10,
                "cr_change": -8
            },
            "crisis": {
                "name": "⚫ Khủng hoảng",
                "revenue_change": -20,
                "interest_change": 15,
                "roe_change": -20,
                "cr_change": -12
            },
            "custom": {
                "name": "🟡 Tùy chọn biến động",
                "revenue_change": custom_revenue,
                "interest_change": custom_interest,
                "roe_change": custom_roe,
                "cr_change": custom_cr
            }
        }

        if scenario_type not in scenario_configs:
            raise HTTPException(
                status_code=400,
                detail=f"Loại kịch bản không hợp lệ. Chọn: {', '.join(scenario_configs.keys())}"
            )

        scenario = scenario_configs[scenario_type]

        # 3. TÍNH 14 CHỈ SỐ SAU KHI ÁP KỊCH BẢN (indicators_after)
        indicators_after = excel_processor.simulate_scenario_indicators(
            original_indicators=indicators_before,
            revenue_change_pct=scenario["revenue_change"],
            interest_change_pct=scenario["interest_change"],
            roe_change_pct=scenario["roe_change"],
            cr_change_pct=scenario["cr_change"]
        )

        # 4. DỰ BÁO PD TRƯỚC VÀ SAU
        # Dự báo PD trước khi áp kịch bản
        X_before = pd.DataFrame([indicators_before])
        prediction_before = credit_model.predict(X_before)

        # Dự báo PD sau khi áp kịch bản
        X_after = pd.DataFrame([indicators_after])
        prediction_after = credit_model.predict(X_after)

        # 5. TÍNH % THAY ĐỔI PD
        pd_before = prediction_before["pd_stacking"]
        pd_after = prediction_after["pd_stacking"]
        pd_change_pct = ((pd_after - pd_before) / pd_before * 100) if pd_before != 0 else 0

        # 6. CHUẨN BỊ KẾT QUẢ TRẢ VỀ
        # Chuyển đổi indicators thành list có tên
        def indicators_to_list(indicators_dict):
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
            for key, value in indicators_dict.items():
                result.append({
                    'code': key,
                    'name': indicator_names[key],
                    'value': value
                })
            return result

        return {
            "status": "success",
            "scenario_info": {
                "type": scenario_type,
                "name": scenario["name"],
                "changes": {
                    "revenue": scenario["revenue_change"],
                    "interest": scenario["interest_change"],
                    "roe": scenario["roe_change"],
                    "cr": scenario["cr_change"]
                }
            },
            "indicators_before": indicators_to_list(indicators_before),
            "indicators_before_dict": indicators_before,
            "indicators_after": indicators_to_list(indicators_after),
            "indicators_after_dict": indicators_after,
            "prediction_before": prediction_before,
            "prediction_after": prediction_after,
            "pd_change": {
                "before": pd_before,
                "after": pd_after,
                "change_pct": round(pd_change_pct, 2),
                "change_absolute": round(pd_after - pd_before, 6)
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi mô phỏng kịch bản: {str(e)}")


@app.post("/analyze-scenario")
async def analyze_scenario(request_data: Dict[str, Any]):
    """
    Endpoint phân tích kết quả mô phỏng kịch bản bằng Gemini API

    Args:
        request_data: Dict chứa kết quả mô phỏng kịch bản

    Returns:
        Dict chứa kết quả phân tích từ Gemini
    """
    try:
        # Lấy Gemini analyzer
        analyzer = get_gemini_analyzer()

        # Phân tích kịch bản
        analysis = analyzer.analyze_scenario_simulation(request_data)

        return {
            "status": "success",
            "analysis": analysis
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy GEMINI_API_KEY. Vui lòng set biến môi trường. Chi tiết: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích kịch bản bằng Gemini: {str(e)}")


# ================================================================================================
# MAIN
# ================================================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
