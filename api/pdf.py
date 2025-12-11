"""
PDF 工具 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path

from core.file_handler import file_handler, TEMP_DIR
from core.task_queue import task_queue
from services.pdf_service import pdf_service

router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])

ALLOWED_PDF_TYPES = ["application/pdf"]
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"]


# ============ 请求模型 ============

class CompressRequest(BaseModel):
    file_id: str


class MergeRequest(BaseModel):
    file_ids: list[str]
    order: Optional[list[int]] = None


class SplitRequest(BaseModel):
    file_id: str
    page_ranges: list[tuple[int, int]]


# ============ 响应模型 ============

class UploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    error_message: Optional[str] = None


class ProcessResponse(BaseModel):
    success: bool
    download_url: Optional[str] = None
    error_message: Optional[str] = None


class SplitResponse(BaseModel):
    success: bool
    download_urls: list[str] = []
    error_message: Optional[str] = None


# ============ API 端点 ============

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """上传 PDF"""
    result = await file_handler.validate_file(file, ALLOWED_PDF_TYPES)
    if not result.valid:
        return UploadResponse(success=False, error_message=result.error_message)
    
    temp_file = await file_handler.save_temp_file(file)
    return UploadResponse(success=True, file_id=temp_file.id)


@router.post("/upload-image", response_model=UploadResponse)
async def upload_image_for_pdf(file: UploadFile = File(...)):
    """上传图片（用于转 PDF）"""
    result = await file_handler.validate_file(file, ALLOWED_IMAGE_TYPES)
    if not result.valid:
        return UploadResponse(success=False, error_message=result.error_message)
    
    temp_file = await file_handler.save_temp_file(file)
    return UploadResponse(success=True, file_id=temp_file.id)


@router.post("/compress", response_model=ProcessResponse)
async def compress_pdf(request: CompressRequest):
    """压缩 PDF"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return pdf_service.compress(input_path)
    
    try:
        output_path = await task_queue.submit(process)
        return ProcessResponse(
            success=True,
            download_url=f"/api/v1/pdf/download/{output_path.name}"
        )
    except Exception as e:
        return ProcessResponse(success=False, error_message=str(e))


@router.post("/to-word", response_model=ProcessResponse)
async def pdf_to_word(file_id: str):
    """PDF 转 Word"""
    input_path = file_handler.get_temp_file(file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return pdf_service.to_word(input_path)
    
    try:
        output_path = await task_queue.submit(process)
        return ProcessResponse(
            success=True,
            download_url=f"/api/v1/pdf/download/{output_path.name}"
        )
    except Exception as e:
        return ProcessResponse(success=False, error_message=str(e))


@router.post("/merge", response_model=ProcessResponse)
async def merge_pdfs(request: MergeRequest):
    """合并 PDF"""
    input_paths = []
    for file_id in request.file_ids:
        path = file_handler.get_temp_file(file_id)
        if not path:
            return ProcessResponse(success=False, error_message=f"File {file_id} not found")
        input_paths.append(path)
    
    async def process():
        return pdf_service.merge(input_paths, request.order)
    
    try:
        output_path = await task_queue.submit(process)
        return ProcessResponse(
            success=True,
            download_url=f"/api/v1/pdf/download/{output_path.name}"
        )
    except Exception as e:
        return ProcessResponse(success=False, error_message=str(e))


@router.post("/split", response_model=SplitResponse)
async def split_pdf(request: SplitRequest):
    """拆分 PDF"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return SplitResponse(success=False, error_message="File not found")
    
    async def process():
        return pdf_service.split(input_path, request.page_ranges)
    
    try:
        output_paths = await task_queue.submit(process)
        download_urls = [f"/api/v1/pdf/download/{p.name}" for p in output_paths]
        return SplitResponse(success=True, download_urls=download_urls)
    except Exception as e:
        return SplitResponse(success=False, error_message=str(e))


@router.post("/from-images", response_model=ProcessResponse)
async def images_to_pdf(file_ids: list[str]):
    """图片转 PDF"""
    input_paths = []
    for file_id in file_ids:
        path = file_handler.get_temp_file(file_id)
        if not path:
            return ProcessResponse(success=False, error_message=f"File {file_id} not found")
        input_paths.append(path)
    
    async def process():
        return pdf_service.from_images(input_paths)
    
    try:
        output_path = await task_queue.submit(process)
        return ProcessResponse(
            success=True,
            download_url=f"/api/v1/pdf/download/{output_path.name}"
        )
    except Exception as e:
        return ProcessResponse(success=False, error_message=str(e))


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载处理后的文件"""
    file_path = TEMP_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
