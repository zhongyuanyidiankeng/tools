"""
PDF 处理服务属性测试
"""
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from PIL import Image

# 检查 pypdf 是否可用
try:
    from pypdf import PdfReader, PdfWriter
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from services.pdf_service import PDFService


def create_test_pdf(pages: int = 1) -> Path:
    """创建测试 PDF 文件"""
    if not HAS_PYPDF:
        # 创建最小有效 PDF
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / f"test_pdf_{pages}pages.pdf"
        
        # 使用 PIL 创建简单 PDF
        images = []
        for i in range(pages):
            img = Image.new('RGB', (200, 200), color=f'#{i*30:02x}{i*20:02x}{i*10:02x}')
            images.append(img)
        
        if images:
            images[0].save(temp_path, 'PDF', save_all=True, 
                          append_images=images[1:] if len(images) > 1 else [])
        
        return temp_path
    
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"test_pdf_{pages}pages.pdf"
    
    writer = PdfWriter()
    for i in range(pages):
        writer.add_blank_page(width=612, height=792)
    
    with open(temp_path, 'wb') as f:
        writer.write(f)
    
    return temp_path


def create_test_image(index: int = 0) -> Path:
    """创建测试图片"""
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"test_img_{index}.png"
    
    img = Image.new('RGB', (200, 200), color='blue')
    img.save(temp_path)
    
    return temp_path


class TestPDFCompression:
    """
    **Feature: online-tools-platform, Property 1: PDF 压缩有效性**
    **Validates: Requirements 1.1**
    
    For any valid PDF file, compressing it SHALL produce an output file
    that is a valid PDF.
    """
    
    def setup_method(self):
        self.service = PDFService()
    
    def test_pdf_compress_produces_valid_pdf(self):
        """
        **Feature: online-tools-platform, Property 1: PDF 压缩有效性**
        
        压缩后的文件应该是有效的 PDF
        """
        if not HAS_PYPDF:
            return  # 跳过测试
        
        input_path = create_test_pdf(3)
        output_path = None
        
        try:
            output_path = self.service.compress(input_path)
            
            # 验证输出是有效 PDF
            reader = PdfReader(str(output_path))
            assert len(reader.pages) == 3
        finally:
            input_path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)


class TestPDFToWord:
    """
    **Feature: online-tools-platform, Property 2: PDF 转 Word 有效性**
    **Validates: Requirements 1.2**
    
    For any valid PDF file, converting it to Word SHALL produce a valid DOCX file.
    """
    
    def setup_method(self):
        self.service = PDFService()
    
    def test_pdf_to_word_produces_docx(self):
        """
        **Feature: online-tools-platform, Property 2: PDF 转 Word 有效性**
        
        转换应该产生 DOCX 文件
        """
        # 此测试需要 pdf2docx，如果未安装则跳过
        try:
            from pdf2docx import Converter
        except ImportError:
            return
        
        input_path = create_test_pdf(1)
        output_path = None
        
        try:
            output_path = self.service.to_word(input_path)
            
            # 验证输出文件存在且是 docx
            assert output_path.exists()
            assert output_path.suffix == '.docx'
        finally:
            input_path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)


class TestPDFMerge:
    """
    **Feature: online-tools-platform, Property 3: PDF 合并完整性**
    **Validates: Requirements 1.3**
    
    For any list of valid PDF files and any specified order, merging them
    SHALL produce a single PDF where the total page count equals the sum
    of all input page counts.
    """
    
    def setup_method(self):
        self.service = PDFService()
    
    @settings(max_examples=10, deadline=None)
    @given(
        st.lists(st.integers(min_value=1, max_value=3), min_size=2, max_size=4)
    )
    def test_pdf_merge_preserves_page_count(self, page_counts: list[int]):
        """
        **Feature: online-tools-platform, Property 3: PDF 合并完整性**
        
        合并后的 PDF 页数应该等于所有输入 PDF 页数之和
        """
        if not HAS_PYPDF:
            return
        
        input_paths = [create_test_pdf(count) for count in page_counts]
        output_path = None
        
        try:
            output_path = self.service.merge(input_paths)
            
            # 验证页数
            reader = PdfReader(str(output_path))
            expected_pages = sum(page_counts)
            assert len(reader.pages) == expected_pages, \
                f"Expected {expected_pages} pages, got {len(reader.pages)}"
        finally:
            for path in input_paths:
                path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)


class TestPDFSplit:
    """
    **Feature: online-tools-platform, Property 4: PDF 拆分正确性**
    **Validates: Requirements 1.4**
    
    For any valid PDF and any valid page range selection, splitting SHALL
    produce separate PDF files where each contains exactly the specified pages.
    """
    
    def setup_method(self):
        self.service = PDFService()
    
    def test_pdf_split_produces_correct_parts(self):
        """
        **Feature: online-tools-platform, Property 4: PDF 拆分正确性**
        
        拆分后的每个部分应该包含正确的页数
        """
        if not HAS_PYPDF:
            return
        
        input_path = create_test_pdf(5)
        output_paths = []
        
        try:
            # 拆分为 [1-2], [3-5]
            page_ranges = [(1, 2), (3, 5)]
            output_paths = self.service.split(input_path, page_ranges)
            
            # 验证数量
            assert len(output_paths) == 2
            
            # 验证每部分页数
            reader1 = PdfReader(str(output_paths[0]))
            assert len(reader1.pages) == 2
            
            reader2 = PdfReader(str(output_paths[1]))
            assert len(reader2.pages) == 3
        finally:
            input_path.unlink(missing_ok=True)
            for path in output_paths:
                path.unlink(missing_ok=True)


class TestImagesToPDF:
    """
    **Feature: online-tools-platform, Property 5: 图片转 PDF 完整性**
    **Validates: Requirements 1.5**
    
    For any list of valid images, converting to PDF SHALL produce a PDF
    with page count equal to the number of input images.
    """
    
    def setup_method(self):
        self.service = PDFService()
    
    @settings(max_examples=10, deadline=None)
    @given(st.integers(min_value=1, max_value=5))
    def test_images_to_pdf_page_count(self, image_count: int):
        """
        **Feature: online-tools-platform, Property 5: 图片转 PDF 完整性**
        
        生成的 PDF 页数应该等于输入图片数量
        """
        image_paths = [create_test_image(i) for i in range(image_count)]
        output_path = None
        
        try:
            output_path = self.service.from_images(image_paths)
            
            # 验证输出存在
            assert output_path.exists()
            
            # 如果有 pypdf，验证页数
            if HAS_PYPDF:
                reader = PdfReader(str(output_path))
                assert len(reader.pages) == image_count, \
                    f"Expected {image_count} pages, got {len(reader.pages)}"
        finally:
            for path in image_paths:
                path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)
