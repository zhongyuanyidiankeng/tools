"""
图像处理服务属性测试
"""
import io
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from PIL import Image
from services.image_service import ImageService


def create_test_image(width: int = 200, height: int = 200, 
                      color: str = 'red', format: str = 'PNG') -> Path:
    """创建测试图片并保存到临时文件"""
    img = Image.new('RGB', (width, height), color=color)
    
    temp_dir = Path(tempfile.gettempdir())
    ext = '.png' if format == 'PNG' else '.jpg'
    temp_path = temp_dir / f"test_image_{width}x{height}{ext}"
    
    img.save(temp_path, format)
    return temp_path


class TestCompressToSize:
    """
    **Feature: online-tools-platform, Property 6: 指定大小压缩**
    **Validates: Requirements 2.2**
    
    For any valid image and any target size in KB, compressing to that size
    SHALL produce an output file with size less than or equal to the target.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=20, deadline=None)
    @given(
        st.integers(min_value=100, max_value=500),
        st.integers(min_value=100, max_value=500),
        st.integers(min_value=50, max_value=200)
    )
    def test_compress_to_size_respects_limit(self, width: int, height: int, 
                                              target_kb: int):
        """
        **Feature: online-tools-platform, Property 6: 指定大小压缩**
        
        压缩后的文件大小应该不超过目标大小
        """
        # 创建测试图片
        input_path = create_test_image(width, height)
        
        try:
            # 压缩到指定大小
            output_path = self.service.compress_to_size(input_path, target_kb)
            
            # 验证输出文件大小
            output_size_kb = output_path.stat().st_size / 1024
            assert output_size_kb <= target_kb, \
                f"Output size {output_size_kb:.1f}KB exceeds target {target_kb}KB"
            
            # 清理
            output_path.unlink(missing_ok=True)
        finally:
            input_path.unlink(missing_ok=True)


class TestFormatConversion:
    """
    **Feature: online-tools-platform, Property 7: 格式转换有效性**
    **Validates: Requirements 2.3**
    
    For any valid WebP image, converting to JPG SHALL produce a valid JPG file.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=20, deadline=None)
    @given(
        st.integers(min_value=50, max_value=300),
        st.integers(min_value=50, max_value=300),
        st.sampled_from(['jpg', 'png', 'bmp'])
    )
    def test_format_conversion_produces_valid_file(self, width: int, height: int,
                                                    target_format: str):
        """
        **Feature: online-tools-platform, Property 7: 格式转换有效性**
        
        格式转换应该产生有效的目标格式文件
        """
        input_path = create_test_image(width, height)
        output_path = None
        
        try:
            output_path = self.service.convert(input_path, target_format)
            
            # 验证输出文件可以被 PIL 打开
            with Image.open(output_path) as img:
                # 验证格式
                format_map = {'jpg': 'JPEG', 'png': 'PNG', 'bmp': 'BMP'}
                expected_format = format_map.get(target_format)
                assert img.format == expected_format, \
                    f"Expected {expected_format}, got {img.format}"
        finally:
            input_path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)


class TestCropDimensions:
    """
    **Feature: online-tools-platform, Property 8: 裁剪尺寸正确性**
    **Validates: Requirements 2.4**
    
    For any valid image and valid crop dimensions, cropping SHALL produce
    an image with exactly the specified width and height.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=20, deadline=None)
    @given(
        st.integers(min_value=200, max_value=500),
        st.integers(min_value=200, max_value=500),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=50, max_value=150),
        st.integers(min_value=50, max_value=150)
    )
    def test_crop_produces_correct_dimensions(self, img_width: int, img_height: int,
                                               x: int, y: int, 
                                               crop_width: int, crop_height: int):
        """
        **Feature: online-tools-platform, Property 8: 裁剪尺寸正确性**
        
        裁剪后的图片应该具有指定的尺寸
        """
        input_path = create_test_image(img_width, img_height)
        output_path = None
        
        try:
            output_path = self.service.crop(input_path, x, y, crop_width, crop_height)
            
            # 验证输出尺寸
            with Image.open(output_path) as img:
                actual_width, actual_height = img.size
                
                # 计算预期尺寸（考虑边界）
                expected_width = min(crop_width, img_width - x)
                expected_height = min(crop_height, img_height - y)
                
                assert actual_width == expected_width, \
                    f"Width mismatch: {actual_width} != {expected_width}"
                assert actual_height == expected_height, \
                    f"Height mismatch: {actual_height} != {expected_height}"
        finally:
            input_path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)


class TestGridSplitCount:
    """
    **Feature: online-tools-platform, Property 9: 网格切割数量正确性**
    **Validates: Requirements 2.7**
    
    For any valid image and grid configuration of R rows and C columns,
    grid splitting SHALL produce exactly R × C separate image files.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=20, deadline=None)
    @given(
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5)
    )
    def test_grid_split_produces_correct_count(self, rows: int, cols: int):
        """
        **Feature: online-tools-platform, Property 9: 网格切割数量正确性**
        
        网格切割应该产生 rows × cols 个文件
        """
        input_path = create_test_image(300, 300)
        output_paths = []
        
        try:
            output_paths = self.service.grid_split(input_path, rows, cols)
            
            expected_count = rows * cols
            assert len(output_paths) == expected_count, \
                f"Expected {expected_count} files, got {len(output_paths)}"
            
            # 验证每个文件都存在且可读
            for path in output_paths:
                assert path.exists(), f"Output file {path} does not exist"
                with Image.open(path) as img:
                    assert img is not None
        finally:
            input_path.unlink(missing_ok=True)
            for path in output_paths:
                path.unlink(missing_ok=True)


class TestSplitAndCompress:
    """
    **Feature: online-tools-platform, Property 10: 切割并压缩组合正确性**
    **Validates: Requirements 2.8**
    
    For any valid image, grid configuration, and target size,
    split-and-compress SHALL produce R × C images where each image's
    file size is at or below the target size.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=10, deadline=None)
    @given(
        st.integers(min_value=1, max_value=3),
        st.integers(min_value=1, max_value=3),
        st.integers(min_value=50, max_value=100)
    )
    def test_split_and_compress_respects_size(self, rows: int, cols: int,
                                               target_kb: int):
        """
        **Feature: online-tools-platform, Property 10: 切割并压缩组合正确性**
        
        切割并压缩后的每个区块都应该不超过目标大小
        """
        input_path = create_test_image(400, 400)
        
        try:
            output_paths = self.service.split_and_compress(
                input_path, rows, cols, None, None, target_kb
            )
            
            # 验证数量
            expected_count = rows * cols
            assert len(output_paths) == expected_count
            
            # 验证每个文件大小
            for path in output_paths:
                size_kb = path.stat().st_size / 1024
                assert size_kb <= target_kb, \
                    f"File {path} size {size_kb:.1f}KB exceeds target {target_kb}KB"
                path.unlink(missing_ok=True)
        finally:
            input_path.unlink(missing_ok=True)


class TestICOGeneration:
    """
    **Feature: online-tools-platform, Property 11: ICO 生成有效性**
    **Validates: Requirements 2.9**
    
    For any valid image input, ICO generation SHALL produce a valid ICO file.
    """
    
    def setup_method(self):
        self.service = ImageService()
    
    @settings(max_examples=10, deadline=None)
    @given(
        st.integers(min_value=100, max_value=300),
        st.integers(min_value=100, max_value=300)
    )
    def test_ico_generation_produces_valid_file(self, width: int, height: int):
        """
        **Feature: online-tools-platform, Property 11: ICO 生成有效性**
        
        ICO 生成应该产生有效的 ICO 文件
        """
        input_path = create_test_image(width, height)
        output_path = None
        
        try:
            output_path = self.service.to_ico(input_path)
            
            # 验证文件存在
            assert output_path.exists()
            assert output_path.suffix == '.ico'
            
            # 验证可以被 PIL 打开
            with Image.open(output_path) as img:
                assert img.format == 'ICO'
        finally:
            input_path.unlink(missing_ok=True)
            if output_path:
                output_path.unlink(missing_ok=True)
