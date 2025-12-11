"""
通用数据模型定义
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ============ 文件相关模型 ============

class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str
    filename: str
    size: int
    mime_type: str
    expires_at: datetime


class ValidationResult(BaseModel):
    """文件验证结果"""
    valid: bool
    detected_type: Optional[str] = None
    error_message: Optional[str] = None


class ProcessingResult(BaseModel):
    """处理结果"""
    success: bool
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    processing_time_ms: int = 0


# ============ 图像处理模型 ============

class ImageCompressRequest(BaseModel):
    """图片压缩请求"""
    file_id: str
    quality: int = Field(default=80, ge=1, le=100)


class ImageCompressToSizeRequest(BaseModel):
    """指定大小压缩请求"""
    file_id: str
    target_size_kb: int = Field(ge=1)


class ImageConvertRequest(BaseModel):
    """图片格式转换请求"""
    file_id: str
    target_format: str = Field(pattern="^(jpg|jpeg|png|webp|gif|bmp)$")


class ImageCropRequest(BaseModel):
    """图片裁剪请求"""
    file_id: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class GridSplitRequest(BaseModel):
    """网格切割请求"""
    file_id: str
    rows: int = Field(ge=1, le=10)
    cols: int = Field(ge=1, le=10)
    row_positions: list[float] = Field(default_factory=list)
    col_positions: list[float] = Field(default_factory=list)


class SplitCompressRequest(BaseModel):
    """切割并压缩请求"""
    file_id: str
    rows: int = Field(ge=1, le=10)
    cols: int = Field(ge=1, le=10)
    row_positions: list[float] = Field(default_factory=list)
    col_positions: list[float] = Field(default_factory=list)
    target_size_kb: int = Field(ge=1)


class GridSplitResponse(BaseModel):
    """网格切割响应"""
    success: bool
    download_urls: list[str] = Field(default_factory=list)
    grid_info: list[dict] = Field(default_factory=list)
    error_message: Optional[str] = None


# ============ PDF 处理模型 ============

class PDFCompressRequest(BaseModel):
    """PDF 压缩请求"""
    file_id: str


class PDFMergeRequest(BaseModel):
    """PDF 合并请求"""
    file_ids: list[str]
    order: Optional[list[int]] = None


class PDFSplitRequest(BaseModel):
    """PDF 拆分请求"""
    file_id: str
    page_ranges: list[tuple[int, int]]


class PDFSplitResponse(BaseModel):
    """PDF 拆分响应"""
    success: bool
    download_urls: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None


# ============ 文本工具模型 ============

class JSONFormatRequest(BaseModel):
    """JSON 格式化请求"""
    json_str: str
    indent: int = Field(default=2, ge=0, le=8)


class FormatResult(BaseModel):
    """格式化结果"""
    success: bool
    formatted: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_message: Optional[str] = None


class Base64Request(BaseModel):
    """Base64 编解码请求"""
    text: str
    action: str = Field(pattern="^(encode|decode)$")


class RegexTestRequest(BaseModel):
    """正则测试请求"""
    pattern: str
    test_string: str
    flags: Optional[str] = None


class RegexMatch(BaseModel):
    """正则匹配项"""
    start: int
    end: int
    text: str
    groups: list[str] = Field(default_factory=list)


class RegexResult(BaseModel):
    """正则测试结果"""
    success: bool
    matches: list[RegexMatch] = Field(default_factory=list)
    match_count: int = 0
    error_message: Optional[str] = None


class MarkdownRequest(BaseModel):
    """Markdown 转换请求"""
    markdown: str


# ============ 开发者工具模型 ============

class JWTDecodeRequest(BaseModel):
    """JWT 解码请求"""
    token: str


class JWTResult(BaseModel):
    """JWT 解码结果"""
    success: bool
    header: Optional[dict] = None
    payload: Optional[dict] = None
    signature_valid: Optional[bool] = None
    expired: bool = False
    error_message: Optional[str] = None


class CronGenerateRequest(BaseModel):
    """Cron 表达式生成请求"""
    minute: str = "*"
    hour: str = "*"
    day: str = "*"
    month: str = "*"
    weekday: str = "*"


class CronResult(BaseModel):
    """Cron 生成结果"""
    success: bool
    expression: Optional[str] = None
    description: Optional[str] = None
    next_runs: list[datetime] = Field(default_factory=list)
    error_message: Optional[str] = None


class IPLookupRequest(BaseModel):
    """IP 查询请求"""
    ip: str


class IPInfo(BaseModel):
    """IP 信息"""
    success: bool
    ip: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    timezone: Optional[str] = None
    error_message: Optional[str] = None


# ============ 错误响应模型 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    details: Optional[Any] = None
