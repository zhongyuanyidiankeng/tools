"""
在线工具平台 - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.text import router as text_router
from api.dev import router as dev_router
from api.image import router as image_router
from api.pdf import router as pdf_router
from core.middleware import RateLimitMiddleware

app = FastAPI(
    title="在线工具平台",
    description="PDF、图像、文本和开发者工具集合",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求限流 (60 requests/minute)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# 注册路由
app.include_router(text_router)
app.include_router(dev_router)
app.include_router(image_router)
app.include_router(pdf_router)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    import asyncio
    from core.file_handler import cleanup_task
    # 启动文件清理后台任务
    asyncio.create_task(cleanup_task())
