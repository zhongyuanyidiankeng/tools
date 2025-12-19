"""
开发者工具服务模块
提供 JWT 解码、Cron 生成、UUID 生成、IP 查询等功能
"""
import uuid
import json
import base64
import re
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

# 尝试导入 croniter，如果不存在则使用简单实现
try:
    from croniter import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False

# 尝试导入 httpx 用于 IP 查询
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class JWTResult:
    """JWT 解码结果"""
    success: bool
    header: Optional[dict] = None
    payload: Optional[dict] = None
    signature_valid: Optional[bool] = None
    expired: bool = False
    error_message: Optional[str] = None


@dataclass
class CronResult:
    """Cron 生成结果"""
    success: bool
    expression: Optional[str] = None
    description: Optional[str] = None
    next_runs: list = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.next_runs is None:
            self.next_runs = []


@dataclass
class IPInfo:
    """IP 信息"""
    success: bool
    ip: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    timezone: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PanSearchResult:
    """网盘搜索结果"""
    success: bool
    data: list = None
    total_pages: int = 1
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = []


class DevService:
    """开发者工具服务"""
    
    def decode_jwt(self, token: str) -> JWTResult:
        """
        解码 JWT token
        - 提取 header 和 payload
        - 检查是否过期
        - 注意：不验证签名（需要密钥）
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return JWTResult(
                    success=False,
                    error_message="Invalid JWT format: expected 3 parts"
                )
            
            # 解码 header
            header_b64 = parts[0]
            # 添加 padding
            header_b64 += '=' * (4 - len(header_b64) % 4) if len(header_b64) % 4 else ''
            header = json.loads(base64.urlsafe_b64decode(header_b64))
            
            # 解码 payload
            payload_b64 = parts[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ''
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            
            # 检查是否过期
            expired = False
            if 'exp' in payload:
                exp_time = datetime.fromtimestamp(payload['exp'])
                expired = exp_time < datetime.now()
            
            return JWTResult(
                success=True,
                header=header,
                payload=payload,
                signature_valid=None,  # 无法验证签名
                expired=expired
            )
        except Exception as e:
            return JWTResult(success=False, error_message=str(e))
    
    def generate_cron(self, minute: str = "*", hour: str = "*", 
                      day: str = "*", month: str = "*", 
                      weekday: str = "*") -> CronResult:
        """
        生成 Cron 表达式
        - 验证表达式有效性
        - 计算下次执行时间
        """
        expression = f"{minute} {hour} {day} {month} {weekday}"
        
        # 验证格式
        cron_pattern = r'^[\d\*,\-/]+\s+[\d\*,\-/]+\s+[\d\*,\-/]+\s+[\d\*,\-/]+\s+[\d\*,\-/]+$'
        if not re.match(cron_pattern, expression):
            return CronResult(
                success=False,
                error_message="Invalid cron expression format"
            )
        
        # 生成描述
        description = self._describe_cron(minute, hour, day, month, weekday)
        
        # 计算下次执行时间
        next_runs = []
        if HAS_CRONITER:
            try:
                cron = croniter(expression, datetime.now())
                for _ in range(5):
                    next_runs.append(cron.get_next(datetime))
            except Exception:
                pass
        else:
            # 简单实现：只返回表达式，不计算下次执行时间
            pass
        
        return CronResult(
            success=True,
            expression=expression,
            description=description,
            next_runs=next_runs
        )
    
    def _describe_cron(self, minute: str, hour: str, day: str, 
                       month: str, weekday: str) -> str:
        """生成 Cron 表达式的人类可读描述"""
        parts = []
        
        if minute == "*" and hour == "*":
            parts.append("Every minute")
        elif minute == "0" and hour == "*":
            parts.append("Every hour")
        elif minute == "0" and hour != "*":
            parts.append(f"At {hour}:00")
        elif minute != "*" and hour != "*":
            parts.append(f"At {hour}:{minute.zfill(2)}")
        else:
            parts.append(f"At minute {minute}")
        
        if day != "*":
            parts.append(f"on day {day}")
        
        if month != "*":
            parts.append(f"in month {month}")
        
        if weekday != "*":
            weekday_names = {
                "0": "Sunday", "1": "Monday", "2": "Tuesday",
                "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday"
            }
            parts.append(f"on {weekday_names.get(weekday, f'weekday {weekday}')}")
        
        return " ".join(parts)
    
    def generate_uuid(self) -> str:
        """生成 UUID v4"""
        return str(uuid.uuid4())
    
    async def lookup_ip(self, ip: str) -> IPInfo:
        """
        查询 IP 地理位置信息
        使用免费的 ip-api.com 服务
        """
        if not HAS_HTTPX:
            return IPInfo(
                success=False,
                error_message="httpx not installed, cannot perform IP lookup"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    timeout=10.0
                )
                data = response.json()
                
                if data.get("status") == "success":
                    return IPInfo(
                        success=True,
                        ip=data.get("query"),
                        country=data.get("country"),
                        region=data.get("regionName"),
                        city=data.get("city"),
                        isp=data.get("isp"),
                        timezone=data.get("timezone")
                    )
                else:
                    return IPInfo(
                        success=False,
                        error_message=data.get("message", "IP lookup failed")
                    )
        except Exception as e:
            return IPInfo(success=False, error_message=str(e))
    
    async def search_pan(self, keyword: str, page: int = 1, pan_type: str = "") -> PanSearchResult:
        """
        搜索网盘资源
        参考 pansou 项目的 API 接口
        """
        if not HAS_HTTPX:
            return PanSearchResult(
                success=False,
                error_message="httpx not installed"
            )
        
        try:
            # 使用 pansou API (无需 token 版本)
            url = "http://localhost:8888/api/search"
            params = {
                "keyword": keyword,
                "page": page,
                "pan": pan_type  # 空字符串表示全部
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    timeout=15.0,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code != 200:
                    return PanSearchResult(
                        success=False,
                        error_message=f"API 请求失败: {response.status_code}"
                    )
                
                data = response.json()
                
                # 解析返回数据
                if data.get("code") == 200 or data.get("success"):
                    items = data.get("data", {}).get("list", []) or data.get("list", [])
                    total = data.get("data", {}).get("total", 0) or data.get("total", 0)
                    page_size = 20
                    total_pages = max(1, (total + page_size - 1) // page_size)
                    
                    results = []
                    for item in items:
                        results.append({
                            "title": item.get("title", item.get("name", "")),
                            "url": item.get("url", item.get("link", "")),
                            "pan_type": item.get("pan", item.get("source", "")),
                            "size": item.get("size", ""),
                            "time": item.get("time", item.get("date", ""))
                        })
                    
                    return PanSearchResult(
                        success=True,
                        data=results,
                        total_pages=total_pages
                    )
                else:
                    return PanSearchResult(
                        success=False,
                        error_message=data.get("msg", "搜索失败")
                    )
                    
        except Exception as e:
            return PanSearchResult(success=False, error_message=str(e))


# 全局服务实例
dev_service = DevService()
