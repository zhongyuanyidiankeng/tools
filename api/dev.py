"""
开发者工具 API 路由
"""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.dev_service import dev_service

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])


# ============ 请求/响应模型 ============

class JWTDecodeRequest(BaseModel):
    token: str


class JWTDecodeResponse(BaseModel):
    success: bool
    header: Optional[dict] = None
    payload: Optional[dict] = None
    signature_valid: Optional[bool] = None
    expired: bool = False
    error_message: Optional[str] = None


class CronGenerateRequest(BaseModel):
    minute: str = "*"
    hour: str = "*"
    day: str = "*"
    month: str = "*"
    weekday: str = "*"


class CronGenerateResponse(BaseModel):
    success: bool
    expression: Optional[str] = None
    description: Optional[str] = None
    next_runs: list[str] = []
    error_message: Optional[str] = None


class UUIDResponse(BaseModel):
    uuid: str


class IPLookupRequest(BaseModel):
    ip: str


class IPLookupResponse(BaseModel):
    success: bool
    ip: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    timezone: Optional[str] = None
    error_message: Optional[str] = None


class PanSearchRequest(BaseModel):
    keyword: str
    page: int = 1
    pan_type: str = ""


class PanSearchResponse(BaseModel):
    success: bool
    data: list = []
    total_pages: int = 1
    error_message: Optional[str] = None


# ============ API 端点 ============

@router.post("/jwt-decode", response_model=JWTDecodeResponse)
async def decode_jwt(request: JWTDecodeRequest):
    """JWT 解码"""
    result = dev_service.decode_jwt(request.token)
    return JWTDecodeResponse(
        success=result.success,
        header=result.header,
        payload=result.payload,
        signature_valid=result.signature_valid,
        expired=result.expired,
        error_message=result.error_message
    )


@router.post("/cron-generate", response_model=CronGenerateResponse)
async def generate_cron(request: CronGenerateRequest):
    """Cron 表达式生成"""
    result = dev_service.generate_cron(
        request.minute,
        request.hour,
        request.day,
        request.month,
        request.weekday
    )
    
    # 将 datetime 转换为字符串
    next_runs_str = [dt.isoformat() for dt in result.next_runs] if result.next_runs else []
    
    return CronGenerateResponse(
        success=result.success,
        expression=result.expression,
        description=result.description,
        next_runs=next_runs_str,
        error_message=result.error_message
    )


@router.get("/uuid", response_model=UUIDResponse)
async def generate_uuid():
    """UUID 生成"""
    return UUIDResponse(uuid=dev_service.generate_uuid())


@router.post("/ip-lookup", response_model=IPLookupResponse)
async def lookup_ip(request: IPLookupRequest):
    """IP 地理位置查询"""
    result = await dev_service.lookup_ip(request.ip)
    return IPLookupResponse(
        success=result.success,
        ip=result.ip,
        country=result.country,
        region=result.region,
        city=result.city,
        isp=result.isp,
        timezone=result.timezone,
        error_message=result.error_message
    )


@router.post("/pan-search", response_model=PanSearchResponse)
async def search_pan(request: PanSearchRequest):
    """网盘资源搜索"""
    result = await dev_service.search_pan(
        keyword=request.keyword,
        page=request.page,
        pan_type=request.pan_type
    )
    return PanSearchResponse(
        success=result.success,
        data=result.data,
        total_pages=result.total_pages,
        error_message=result.error_message
    )
