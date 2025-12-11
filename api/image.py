"""
图像工具 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path

from core.file_handler import file_handler
from core.task_queue import task_queue
from services.image_service import image_service

router = APIRouter(prefix="/api/v1/image", tags=["image"])

ALLOWED_IMAGE_TYPES = [
    "image/jpeg", "image/png", "image/webp", 
    "image/gif", "image/bmp"
]


# ============ 请求模型 ============

class CompressRequest(BaseModel):
    file_id: str
    quality: int = Field(default=80, ge=1, le=100)


class CompressToSizeRequest(BaseModel):
    file_id: str
    target_size_kb: int = Field(ge=1)


class ConvertRequest(BaseModel):
    file_id: str
    target_format: str


class CropRequest(BaseModel):
    file_id: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class GridSplitRequest(BaseModel):
    file_id: str
    rows: int = Field(ge=1, le=10)
    cols: int = Field(ge=1, le=10)
    row_positions: Optional[list[float]] = None
    col_positions: Optional[list[float]] = None


class SplitCompressRequest(BaseModel):
    file_id: str
    rows: int = Field(ge=1, le=10)
    cols: int = Field(ge=1, le=10)
    row_positions: Optional[list[float]] = None
    col_positions: Optional[list[float]] = None
    target_size_kb: int = Field(ge=1)


class CompressToDimensionsRequest(BaseModel):
    file_id: str
    max_width: Optional[int] = Field(default=None, ge=1)
    max_height: Optional[int] = Field(default=None, ge=1)
    quality: int = Field(default=85, ge=1, le=100)


class ResizeExactRequest(BaseModel):
    file_id: str
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    keep_aspect: bool = True
    quality: int = Field(default=85, ge=1, le=100)


class SplitByDimensionsRequest(BaseModel):
    file_id: str
    piece_width: int = Field(ge=1)
    piece_height: int = Field(ge=1)
    quality: int = Field(default=85, ge=1, le=100)


class SplitCompressByDimensionsRequest(BaseModel):
    file_id: str
    piece_width: int = Field(ge=1)
    piece_height: int = Field(ge=1)
    target_size_kb: Optional[int] = Field(default=None, ge=1)
    max_width: Optional[int] = Field(default=None, ge=1)
    max_height: Optional[int] = Field(default=None, ge=1)
    quality: int = Field(default=85, ge=1, le=100)


# ============ 响应模型 ============

class UploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    error_message: Optional[str] = None


class ProcessResponse(BaseModel):
    success: bool
    download_url: Optional[str] = None
    error_message: Optional[str] = None


class GridSplitResponse(BaseModel):
    success: bool
    download_urls: list[str] = []
    error_message: Optional[str] = None


# ============ API 端点 ============

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    # 验证文件类型
    result = await file_handler.validate_file(file, ALLOWED_IMAGE_TYPES)
    if not result.valid:
        return UploadResponse(success=False, error_message=result.error_message)
    
    # 保存文件
    temp_file = await file_handler.save_temp_file(file)
    return UploadResponse(success=True, file_id=temp_file.id)


@router.post("/compress", response_model=ProcessResponse)
async def compress_image(request: CompressRequest):
    """压缩图片"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.compress(input_path, request.quality)
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/compress-to-size", response_model=ProcessResponse)
async def compress_to_size(request: CompressToSizeRequest):
    """压缩到指定大小"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.compress_to_size(input_path, request.target_size_kb)
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/convert", response_model=ProcessResponse)
async def convert_image(request: ConvertRequest):
    """格式转换"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.convert(input_path, request.target_format)
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/crop", response_model=ProcessResponse)
async def crop_image(request: CropRequest):
    """裁剪图片"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.crop(
            input_path, request.x, request.y, 
            request.width, request.height
        )
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/grid-split", response_model=GridSplitResponse)
async def grid_split(request: GridSplitRequest):
    """网格切割"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return GridSplitResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.grid_split(
            input_path, request.rows, request.cols,
            request.row_positions, request.col_positions
        )
    
    output_paths = await task_queue.submit(process)
    download_urls = [f"/api/v1/image/download/{p.name}" for p in output_paths]
    return GridSplitResponse(success=True, download_urls=download_urls)


@router.post("/split-compress", response_model=GridSplitResponse)
async def split_and_compress(request: SplitCompressRequest):
    """切割并压缩"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return GridSplitResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.split_and_compress(
            input_path, request.rows, request.cols,
            request.row_positions, request.col_positions,
            request.target_size_kb
        )
    
    output_paths = await task_queue.submit(process)
    download_urls = [f"/api/v1/image/download/{p.name}" for p in output_paths]
    return GridSplitResponse(success=True, download_urls=download_urls)


@router.post("/to-ico", response_model=ProcessResponse)
async def to_ico(file_id: str):
    """生成 ICO"""
    input_path = file_handler.get_temp_file(file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.to_ico(input_path)
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/compress-to-dimensions", response_model=ProcessResponse)
async def compress_to_dimensions(request: CompressToDimensionsRequest):
    """按宽高压缩（保持宽高比缩放到指定尺寸内）"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    if not request.max_width and not request.max_height:
        return ProcessResponse(success=False, error_message="请指定最大宽度或最大高度")
    
    async def process():
        return image_service.compress_to_dimensions(
            input_path, request.max_width, request.max_height, request.quality
        )
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/resize-exact", response_model=ProcessResponse)
async def resize_exact(request: ResizeExactRequest):
    """调整到精确尺寸"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return ProcessResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.resize_exact(
            input_path, request.width, request.height, 
            request.keep_aspect, request.quality
        )
    
    output_path = await task_queue.submit(process)
    return ProcessResponse(
        success=True,
        download_url=f"/api/v1/image/download/{output_path.name}"
    )


@router.post("/split-by-dimensions", response_model=GridSplitResponse)
async def split_by_dimensions(request: SplitByDimensionsRequest):
    """按指定宽高切割图片"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return GridSplitResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.split_by_dimensions(
            input_path, request.piece_width, request.piece_height, request.quality
        )
    
    output_paths = await task_queue.submit(process)
    download_urls = [f"/api/v1/image/download/{p.name}" for p in output_paths]
    return GridSplitResponse(success=True, download_urls=download_urls)


@router.post("/split-compress-by-dimensions", response_model=GridSplitResponse)
async def split_compress_by_dimensions(request: SplitCompressByDimensionsRequest):
    """按指定宽高切割并压缩"""
    input_path = file_handler.get_temp_file(request.file_id)
    if not input_path:
        return GridSplitResponse(success=False, error_message="File not found")
    
    async def process():
        return image_service.split_and_compress_by_dimensions(
            input_path, request.piece_width, request.piece_height,
            request.target_size_kb, request.max_width, request.max_height,
            request.quality
        )
    
    output_paths = await task_queue.submit(process)
    download_urls = [f"/api/v1/image/download/{p.name}" for p in output_paths]
    return GridSplitResponse(success=True, download_urls=download_urls)


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载处理后的文件"""
    from core.file_handler import TEMP_DIR
    file_path = TEMP_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
