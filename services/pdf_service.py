"""
PDF 处理服务模块
提供 PDF 压缩、转换、合并、拆分等功能
"""
import io
from pathlib import Path
from typing import Optional

# 尝试导入 PDF 处理库
try:
    from pypdf import PdfReader, PdfWriter
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from pdf2docx import Converter
    HAS_PDF2DOCX = True
except ImportError:
    HAS_PDF2DOCX = False

try:
    import img2pdf
    HAS_IMG2PDF = True
except ImportError:
    HAS_IMG2PDF = False

from PIL import Image


class PDFService:
    """PDF 处理服务"""
    
    def compress(self, input_path: Path, quality: int = 70) -> Path:
        """
        压缩 PDF
        - 目标压缩率 30%+
        """
        if not HAS_PYPDF:
            raise RuntimeError("pypdf not installed")
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for page in reader.pages:
            # 压缩页面内容
            page.compress_content_streams()
            writer.add_page(page)
        
        output_path = input_path.parent / f"{input_path.stem}_compressed.pdf"
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def to_word(self, input_path: Path) -> Path:
        """
        PDF 转 Word (DOCX)
        """
        if not HAS_PDF2DOCX:
            raise RuntimeError("pdf2docx not installed")
        
        output_path = input_path.parent / f"{input_path.stem}.docx"
        
        cv = Converter(str(input_path))
        cv.convert(str(output_path))
        cv.close()
        
        return output_path
    
    def merge(self, input_paths: list[Path], order: Optional[list[int]] = None) -> Path:
        """
        合并多个 PDF
        """
        if not HAS_PYPDF:
            raise RuntimeError("pypdf not installed")
        
        # 按指定顺序排列
        if order:
            sorted_paths = [input_paths[i] for i in order if i < len(input_paths)]
        else:
            sorted_paths = input_paths
        
        writer = PdfWriter()
        
        for path in sorted_paths:
            reader = PdfReader(str(path))
            for page in reader.pages:
                writer.add_page(page)
        
        output_path = sorted_paths[0].parent / "merged.pdf"
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path
    
    def split(self, input_path: Path, 
              page_ranges: list[tuple[int, int]]) -> list[Path]:
        """
        按页码范围拆分 PDF
        - page_ranges: [(start, end), ...] 页码从 1 开始
        """
        if not HAS_PYPDF:
            raise RuntimeError("pypdf not installed")
        
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)
        output_paths = []
        
        for i, (start, end) in enumerate(page_ranges):
            writer = PdfWriter()
            
            # 转换为 0-based 索引
            start_idx = max(0, start - 1)
            end_idx = min(total_pages, end)
            
            for page_num in range(start_idx, end_idx):
                writer.add_page(reader.pages[page_num])
            
            output_path = input_path.parent / f"{input_path.stem}_part{i+1}.pdf"
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_paths.append(output_path)
        
        return output_paths
    
    def from_images(self, image_paths: list[Path]) -> Path:
        """
        图片转 PDF
        """
        if not image_paths:
            raise ValueError("No images provided")
        
        output_path = image_paths[0].parent / "images_to_pdf.pdf"
        
        if HAS_IMG2PDF:
            # 使用 img2pdf（更好的质量）
            image_bytes = []
            for path in image_paths:
                with open(path, 'rb') as f:
                    image_bytes.append(f.read())
            
            pdf_bytes = img2pdf.convert(image_bytes)
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        else:
            # 使用 PIL 作为后备方案
            images = []
            for path in image_paths:
                img = Image.open(path)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                images.append(img)
            
            if images:
                images[0].save(
                    output_path, 'PDF', 
                    save_all=True, 
                    append_images=images[1:] if len(images) > 1 else []
                )
        
        return output_path
    
    def get_page_count(self, input_path: Path) -> int:
        """获取 PDF 页数"""
        if not HAS_PYPDF:
            raise RuntimeError("pypdf not installed")
        
        reader = PdfReader(str(input_path))
        return len(reader.pages)


# 全局服务实例
pdf_service = PDFService()
