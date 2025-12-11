"""
文件处理器核心模块
负责文件上传验证、临时存储和清理
"""
import os
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import magic
from fastapi import UploadFile

# 临时文件目录
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# 文件过期时间（分钟）
FILE_EXPIRY_MINUTES = 10

# 支持的文件类型映射 (MIME type -> 扩展名列表)
SUPPORTED_TYPES = {
    "application/pdf": [".pdf"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
    "image/gif": [".gif"],
    "image/bmp": [".bmp"],
    "image/x-icon": [".ico"],
}

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class ValidationResult:
    """文件验证结果"""
    def __init__(self, valid: bool, detected_type: Optional[str] = None, 
                 error_message: Optional[str] = None):
        self.valid = valid
        self.detected_type = detected_type
        self.error_message = error_message


class TempFile:
    """临时文件信息"""
    def __init__(self, file_id: str, original_name: str, path: Path,
                 size: int, mime_type: str):
        self.id = file_id
        self.original_name = original_name
        self.path = path
        self.size = size
        self.mime_type = mime_type
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=FILE_EXPIRY_MINUTES)


class FileHandler:
    """文件上传、验证和临时存储管理"""
    
    def __init__(self):
        self._files: dict[str, TempFile] = {}
    
    def detect_file_type(self, content: bytes) -> Optional[str]:
        """通过 magic bytes 检测文件真实类型"""
        try:
            mime = magic.from_buffer(content, mime=True)
            return mime
        except Exception:
            return None
    
    async def validate_file(self, file: UploadFile, allowed_types: list[str], 
                           max_size: int = MAX_FILE_SIZE) -> ValidationResult:
        """
        验证文件类型和大小
        - 通过文件内容检测真实类型（而非扩展名）
        - 检查文件大小限制
        """
        # 读取文件内容
        content = await file.read()
        await file.seek(0)  # 重置文件指针
        
        # 检查文件大小
        if len(content) > max_size:
            return ValidationResult(
                valid=False,
                error_message=f"文件大小超过限制 ({max_size // (1024*1024)}MB)"
            )
        
        # 检测真实文件类型
        detected_type = self.detect_file_type(content)
        if not detected_type:
            return ValidationResult(
                valid=False,
                error_message="无法检测文件类型"
            )
        
        # 检查是否为允许的类型
        if detected_type not in allowed_types:
            return ValidationResult(
                valid=False,
                detected_type=detected_type,
                error_message=f"不支持的文件类型: {detected_type}"
            )
        
        return ValidationResult(valid=True, detected_type=detected_type)
    
    async def save_temp_file(self, file: UploadFile) -> TempFile:
        """保存文件到临时目录，返回文件信息"""
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        
        # 读取内容并检测类型
        content = await file.read()
        mime_type = self.detect_file_type(content) or "application/octet-stream"
        
        # 保留原始扩展名
        original_name = file.filename or "unknown"
        ext = Path(original_name).suffix or ""
        
        # 保存文件
        file_path = TEMP_DIR / f"{file_id}{ext}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 创建临时文件记录
        temp_file = TempFile(
            file_id=file_id,
            original_name=original_name,
            path=file_path,
            size=len(content),
            mime_type=mime_type
        )
        self._files[file_id] = temp_file
        
        return temp_file
    
    def get_temp_file(self, file_id: str) -> Optional[Path]:
        """获取临时文件路径"""
        temp_file = self._files.get(file_id)
        if temp_file and temp_file.path.exists():
            return temp_file.path
        return None
    
    def get_temp_file_info(self, file_id: str) -> Optional[TempFile]:
        """获取临时文件信息"""
        return self._files.get(file_id)
    
    def delete_temp_file(self, file_id: str) -> bool:
        """删除临时文件"""
        temp_file = self._files.pop(file_id, None)
        if temp_file and temp_file.path.exists():
            temp_file.path.unlink()
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """清理过期的临时文件，返回清理数量"""
        now = datetime.now()
        expired_ids = [
            fid for fid, tf in self._files.items()
            if tf.expires_at < now
        ]
        
        for file_id in expired_ids:
            self.delete_temp_file(file_id)
        
        # 同时清理目录中可能遗留的文件
        for file_path in TEMP_DIR.iterdir():
            if file_path.is_file():
                # 检查文件修改时间
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if now - mtime > timedelta(minutes=FILE_EXPIRY_MINUTES):
                    file_path.unlink()
        
        return len(expired_ids)


# 全局文件处理器实例
file_handler = FileHandler()


async def cleanup_task():
    """定时清理任务"""
    while True:
        await asyncio.sleep(60)  # 每分钟检查一次
        file_handler.cleanup_expired()
