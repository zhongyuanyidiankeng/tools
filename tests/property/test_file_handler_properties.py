"""
文件处理器属性测试
**Feature: online-tools-platform, Property 19: 文件类型检测准确性**
"""
import io
from hypothesis import given, strategies as st, settings
from PIL import Image
from core.file_handler import FileHandler


# 创建不同格式的测试图片
def create_test_image(format: str, size: tuple = (100, 100)) -> bytes:
    """创建指定格式的测试图片"""
    img = Image.new('RGB', size, color='red')
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


def create_test_pdf() -> bytes:
    """创建简单的测试 PDF"""
    # 最小有效 PDF
    return b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000052 00000 n 
0000000101 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
170
%%EOF"""


class TestFileTypeDetection:
    """
    **Feature: online-tools-platform, Property 19: 文件类型检测准确性**
    **Validates: Requirements 5.1**
    
    For any file with mismatched extension and actual content type,
    validation SHALL detect the true content type based on file magic bytes.
    """
    
    def setup_method(self):
        self.handler = FileHandler()
    
    @settings(max_examples=100, deadline=None)
    @given(st.sampled_from(['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']))
    def test_image_type_detection_ignores_extension(self, image_format: str):
        """
        **Feature: online-tools-platform, Property 19: 文件类型检测准确性**
        
        对于任何图片文件，无论扩展名如何，都应该通过 magic bytes 检测到真实类型
        """
        # 创建指定格式的图片
        content = create_test_image(image_format)
        
        # 检测类型
        detected = self.handler.detect_file_type(content)
        
        # 验证检测结果 (BMP 在不同系统上可能返回不同的 MIME 类型)
        expected_mimes = {
            'JPEG': ['image/jpeg'],
            'PNG': ['image/png'],
            'GIF': ['image/gif'],
            'BMP': ['image/bmp', 'image/x-ms-bmp'],
            'WEBP': ['image/webp'],
        }
        
        assert detected in expected_mimes[image_format], \
            f"Expected one of {expected_mimes[image_format]}, got {detected}"
    
    def test_pdf_type_detection(self):
        """
        **Feature: online-tools-platform, Property 19: 文件类型检测准确性**
        
        PDF 文件应该被正确检测为 application/pdf
        """
        content = create_test_pdf()
        detected = self.handler.detect_file_type(content)
        assert detected == 'application/pdf', f"Expected application/pdf, got {detected}"
    
    @settings(max_examples=100)
    @given(st.binary(min_size=10, max_size=100))
    def test_random_bytes_detection(self, random_bytes: bytes):
        """
        **Feature: online-tools-platform, Property 19: 文件类型检测准确性**
        
        对于任意字节序列，检测函数应该返回某种类型或 None，不应崩溃
        """
        detected = self.handler.detect_file_type(random_bytes)
        # 检测结果应该是字符串或 None
        assert detected is None or isinstance(detected, str)
    
    def test_mismatched_extension_detection(self):
        """
        **Feature: online-tools-platform, Property 19: 文件类型检测准确性**
        
        即使文件扩展名错误，也应该检测到真实类型
        """
        # 创建 PNG 图片但假装是 .jpg
        png_content = create_test_image('PNG')
        
        # 检测应该返回 PNG 类型，而不是 JPEG
        detected = self.handler.detect_file_type(png_content)
        assert detected == 'image/png', \
            f"Should detect PNG regardless of extension, got {detected}"
