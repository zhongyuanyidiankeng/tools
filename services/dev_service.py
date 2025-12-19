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
        """解码 JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return JWTResult(success=False, error_message="Invalid JWT format: expected 3 parts")
            
            # 解码 header
            header_b64 = parts[0]
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
            
            return JWTResult(success=True, header=header, payload=payload, signature_valid=None, expired=expired)
        except Exception as e:
            return JWTResult(success=False, error_message=str(e))
    
    def generate_cron(self, format: int = 5, second: str = "0", 
                      minute: str = "*", hour: str = "*", 
                      day: str = "*", month: str = "*", 
                      weekday: str = "*", year: str = "*") -> CronResult:
        """
        生成 Cron 表达式
        - 支持 5/6/7 字段格式
        - 验证表达式有效性
        - 计算下次执行时间
        """
        # 根据格式生成表达式
        if format == 5:
            expression = f"{minute} {hour} {day} {month} {weekday}"
            cron_for_iter = expression
        elif format == 6:
            expression = f"{second} {minute} {hour} {day} {month} {weekday}"
            cron_for_iter = f"{minute} {hour} {day} {month} {weekday}"
        else:  # 7 字段
            expression = f"{second} {minute} {hour} {day} {month} {weekday} {year}"
            cron_for_iter = f"{minute} {hour} {day} {month} {weekday}"
        
        # 验证格式
        cron_field_pattern = r'^[\d\*,\-/]+$'
        fields = expression.split()
        for field in fields:
            if not re.match(cron_field_pattern, field):
                return CronResult(success=False, error_message=f"Invalid cron field: {field}")
        
        # 生成描述
        description = self._describe_cron(format, second, minute, hour, day, month, weekday, year)
        
        # 计算下次执行时间
        next_runs = []
        if HAS_CRONITER:
            try:
                cron = croniter(cron_for_iter, datetime.now())
                for _ in range(5):
                    next_runs.append(cron.get_next(datetime))
            except Exception:
                pass
        
        return CronResult(success=True, expression=expression, description=description, next_runs=next_runs)
    
    def _describe_cron(self, format: int, second: str, minute: str, hour: str, 
                       day: str, month: str, weekday: str, year: str) -> str:
        """生成 Cron 表达式的人类可读描述"""
        parts = []
        
        # 秒描述
        if format >= 6 and second != "*" and second != "0":
            if "/" in second:
                parts.append(f"每{second.split('/')[1]}秒")
            else:
                parts.append(f"在第{second}秒")
        
        # 分钟和小时描述
        if minute == "*" and hour == "*":
            parts.append("每分钟")
        elif minute == "0" and hour == "*":
            parts.append("每小时整点")
        elif minute == "0" and hour != "*":
            if "/" in hour:
                parts.append(f"每{hour.split('/')[1]}小时")
            else:
                parts.append(f"在{hour}:00")
        elif "/" in minute:
            parts.append(f"每{minute.split('/')[1]}分钟")
        elif minute != "*" and hour != "*":
            parts.append(f"在{hour}:{minute.zfill(2)}")
        else:
            parts.append(f"在第{minute}分钟")
        
        # 日期描述
        if day != "*":
            if "/" in day:
                parts.append(f"每{day.split('/')[1]}天")
            else:
                parts.append(f"每月{day}号")
        
        if month != "*":
            parts.append(f"在{month}月")
        
        if weekday != "*":
            weekday_names = {"0": "周日", "1": "周一", "2": "周二", "3": "周三", 
                           "4": "周四", "5": "周五", "6": "周六"}
            if "," in weekday:
                days = [weekday_names.get(d, d) for d in weekday.split(",")]
                parts.append(f"在{','.join(days)}")
            else:
                parts.append(f"在{weekday_names.get(weekday, f'星期{weekday}')}")
        
        # 年份描述
        if format == 7 and year != "*":
            parts.append(f"({year}年)")
        
        return " ".join(parts) if parts else "每分钟执行"
    
    def generate_uuid(self) -> str:
        """生成 UUID v4"""
        return str(uuid.uuid4())
    
    async def lookup_ip(self, ip: str) -> IPInfo:
        """查询 IP 地理位置信息"""
        if not HAS_HTTPX:
            return IPInfo(success=False, error_message="httpx not installed")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://ip-api.com/json/{ip}", timeout=10.0)
                data = response.json()
                
                if data.get("status") == "success":
                    return IPInfo(
                        success=True, ip=data.get("query"), country=data.get("country"),
                        region=data.get("regionName"), city=data.get("city"),
                        isp=data.get("isp"), timezone=data.get("timezone")
                    )
                else:
                    return IPInfo(success=False, error_message=data.get("message", "IP lookup failed"))
        except Exception as e:
            return IPInfo(success=False, error_message=str(e))

    async def search_pan(self, keyword: str, page: int = 1, pan_type: str = "") -> PanSearchResult:
        """
        搜索网盘资源
        参考 pansou 项目的 API 接口
        返回格式: { total, results, merged_by_type }
        """
        if not HAS_HTTPX:
            return PanSearchResult(success=False, error_message="httpx not installed")
        
        try:
            url = "http://127.0.0.1:8888/api/search"
            params = {"keyword": keyword, "page": page}
            if pan_type:
                params["pan"] = pan_type
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, timeout=15.0,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                
                if response.status_code != 200:
                    return PanSearchResult(success=False, error_message=f"API 请求失败: {response.status_code}")
                
                data = response.json()
                total = data.get("total", 0)
                results_list = data.get("results", [])
                merged_by_type = data.get("merged_by_type", {})
                
                results = []
                
                # 如果指定了网盘类型，从 merged_by_type 获取
                if pan_type and pan_type in merged_by_type:
                    for item in merged_by_type[pan_type]:
                        results.append({
                            "title": item.get("note", item.get("work_title", "")),
                            "url": item.get("url", ""),
                            "pan_type": pan_type,
                            "password": item.get("password", ""),
                            "time": item.get("datetime", ""),
                            "source": item.get("source", ""),
                            "images": item.get("images", [])
                        })
                else:
                    # 从 results 列表获取
                    for item in results_list:
                        title = item.get("title", item.get("content", ""))
                        links = item.get("links", [])
                        
                        if links:
                            for link in links:
                                results.append({
                                    "title": link.get("work_title", title),
                                    "url": link.get("url", ""),
                                    "pan_type": link.get("type", ""),
                                    "password": link.get("password", ""),
                                    "time": link.get("datetime", item.get("datetime", "")),
                                    "source": item.get("channel", ""),
                                    "images": item.get("images", [])
                                })
                        else:
                            results.append({
                                "title": title, "url": "", "pan_type": "",
                                "password": "", "time": item.get("datetime", ""),
                                "source": item.get("channel", ""), "images": item.get("images", [])
                            })
                
                page_size = 20
                total_pages = max(1, (total + page_size - 1) // page_size)
                
                return PanSearchResult(success=True, data=results, total_pages=total_pages)
                    
        except Exception as e:
            return PanSearchResult(success=False, error_message=str(e))


# 全局服务实例
dev_service = DevService()
