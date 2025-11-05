"""
FastAPI Backend - Hệ thống Đánh giá Rủi ro Tín dụng
Endpoints: /train, /predict, /predict-from-xlsx, /analyze, /export-report
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
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

        # Đọc file XLSX
        excel_processor.read_excel(tmp_file_path)

        # Tính 14 chỉ số
        indicators = excel_processor.calculate_14_indicators()
        indicators_with_names = excel_processor.get_indicators_with_names()

        # Chuyển thành DataFrame để dự báo
        X_new = pd.DataFrame([indicators])

        # Dự báo PD
        prediction_result = credit_model.predict(X_new)

        # Xóa file tạm
        os.unlink(tmp_file_path)

        # Trả về kết quả
        return {
            "status": "success",
            "indicators": indicators_with_names,
            "indicators_dict": indicators,
            "prediction": prediction_result
        }

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

        # Khởi tạo lại Gemini analyzer
        global gemini_analyzer
        from gemini_api import GeminiAnalyzer
        gemini_analyzer = GeminiAnalyzer(request.api_key)

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


# ================================================================================================
# MAIN
# ================================================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
