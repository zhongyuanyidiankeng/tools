"""
文本工具 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.text_service import text_service

router = APIRouter(prefix="/api/v1/text", tags=["text"])


# ============ 请求/响应模型 ============

class JSONFormatRequest(BaseModel):
    json_str: str
    indent: int = 2


class JSONFormatResponse(BaseModel):
    success: bool
    formatted: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_message: Optional[str] = None


class Base64Request(BaseModel):
    text: str
    action: str  # "encode" or "decode"


class Base64Response(BaseModel):
    success: bool
    result: Optional[str] = None
    error_message: Optional[str] = None


class RegexTestRequest(BaseModel):
    pattern: str
    test_string: str
    flags: Optional[str] = None


class RegexMatchItem(BaseModel):
    start: int
    end: int
    text: str
    groups: list[str]


class RegexTestResponse(BaseModel):
    success: bool
    matches: list[RegexMatchItem] = []
    match_count: int = 0
    error_message: Optional[str] = None


class MarkdownRequest(BaseModel):
    markdown: str


class MarkdownResponse(BaseModel):
    success: bool
    html: Optional[str] = None
    error_message: Optional[str] = None


# ============ API 端点 ============

@router.post("/json-format", response_model=JSONFormatResponse)
async def format_json(request: JSONFormatRequest):
    """JSON 格式化"""
    result = text_service.format_json(request.json_str, request.indent)
    return JSONFormatResponse(
        success=result.success,
        formatted=result.formatted,
        error_line=result.error_line,
        error_column=result.error_column,
        error_message=result.error_message
    )


@router.post("/base64", response_model=Base64Response)
async def base64_convert(request: Base64Request):
    """Base64 编解码"""
    try:
        if request.action == "encode":
            result = text_service.base64_encode(request.text)
        elif request.action == "decode":
            result = text_service.base64_decode(request.text)
        else:
            return Base64Response(
                success=False,
                error_message="Invalid action. Use 'encode' or 'decode'."
            )
        return Base64Response(success=True, result=result)
    except Exception as e:
        return Base64Response(success=False, error_message=str(e))


@router.post("/regex-test", response_model=RegexTestResponse)
async def test_regex(request: RegexTestRequest):
    """正则表达式测试"""
    result = text_service.test_regex(
        request.pattern, 
        request.test_string, 
        request.flags
    )
    
    matches = [
        RegexMatchItem(
            start=m.start,
            end=m.end,
            text=m.text,
            groups=m.groups
        )
        for m in result.matches
    ]
    
    return RegexTestResponse(
        success=result.success,
        matches=matches,
        match_count=result.match_count,
        error_message=result.error_message
    )


@router.post("/markdown", response_model=MarkdownResponse)
async def convert_markdown(request: MarkdownRequest):
    """Markdown 转 HTML"""
    try:
        html = text_service.markdown_to_html(request.markdown)
        return MarkdownResponse(success=True, html=html)
    except Exception as e:
        return MarkdownResponse(success=False, error_message=str(e))
