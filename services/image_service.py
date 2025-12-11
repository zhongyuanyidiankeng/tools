"""
图像处理服务模块
提供图片压缩、格式转换、裁剪、网格切割、ICO 生成等功能
"""
import io
from pathlib import Path
from typing import Optional
from PIL import Image


class ImageService:
    """图像处理服务"""
    
    def compress(self, input_path: Path, quality: int = 80) -> Path:
        """
        压缩图片
        - 保持 80%+ 视觉质量
        """
        img = Image.open(input_path)
        
        # 转换为 RGB（如果是 RGBA）
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        output_path = input_path.parent / f"{input_path.stem}_compressed.jpg"
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    
    def compress_to_size(self, input_path: Path, target_size_kb: int) -> Path:
        """
        压缩到指定文件大小
        - 使用二分法调整质量
        """
        img = Image.open(input_path)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        target_bytes = target_size_kb * 1024
        
        # 二分法查找合适的质量
        min_quality = 1
        max_quality = 95
        best_quality = max_quality
        
        while min_quality <= max_quality:
            mid_quality = (min_quality + max_quality) // 2
            
            buffer = io.BytesIO()
            img.save(buffer, 'JPEG', quality=mid_quality, optimize=True)
            size = buffer.tell()
            
            if size <= target_bytes:
                best_quality = mid_quality
                min_quality = mid_quality + 1
            else:
                max_quality = mid_quality - 1
        
        # 使用找到的最佳质量保存
        output_path = input_path.parent / f"{input_path.stem}_sized.jpg"
        img.save(output_path, 'JPEG', quality=best_quality, optimize=True)
        
        return output_path
    
    def compress_to_dimensions(self, input_path: Path, 
                                max_width: Optional[int] = None,
                                max_height: Optional[int] = None,
                                quality: int = 85) -> Path:
        """
        按宽高压缩图片
        - 保持宽高比缩放到指定尺寸内
        """
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        # 计算缩放比例
        scale = 1.0
        if max_width and original_width > max_width:
            scale = min(scale, max_width / original_width)
        if max_height and original_height > max_height:
            scale = min(scale, max_height / original_height)
        
        # 如果需要缩放
        if scale < 1.0:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        output_path = input_path.parent / f"{input_path.stem}_resized.jpg"
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    
    def resize_exact(self, input_path: Path, 
                     width: int, height: int,
                     keep_aspect: bool = True,
                     quality: int = 85) -> Path:
        """
        调整到精确尺寸
        - keep_aspect=True: 保持宽高比，可能有留白
        - keep_aspect=False: 强制拉伸到指定尺寸
        """
        img = Image.open(input_path)
        
        if keep_aspect:
            # 保持宽高比，计算适合的尺寸
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            # 强制拉伸
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        output_path = input_path.parent / f"{input_path.stem}_exact.jpg"
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    
    def convert(self, input_path: Path, target_format: str) -> Path:
        """
        格式转换
        - 支持 jpg, png, webp, gif, bmp
        """
        img = Image.open(input_path)
        
        format_map = {
            'jpg': ('JPEG', '.jpg'),
            'jpeg': ('JPEG', '.jpg'),
            'png': ('PNG', '.png'),
            'webp': ('WEBP', '.webp'),
            'gif': ('GIF', '.gif'),
            'bmp': ('BMP', '.bmp'),
        }
        
        pil_format, ext = format_map.get(target_format.lower(), ('JPEG', '.jpg'))
        
        # JPEG 不支持透明度
        if pil_format == 'JPEG' and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        output_path = input_path.parent / f"{input_path.stem}_converted{ext}"
        img.save(output_path, pil_format)
        
        return output_path
    
    def crop(self, input_path: Path, x: int, y: int, 
             width: int, height: int) -> Path:
        """
        裁剪图片
        """
        img = Image.open(input_path)
        
        # 确保裁剪区域在图片范围内
        img_width, img_height = img.size
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        right = min(x + width, img_width)
        bottom = min(y + height, img_height)
        
        cropped = img.crop((x, y, right, bottom))
        
        output_path = input_path.parent / f"{input_path.stem}_cropped{input_path.suffix}"
        cropped.save(output_path)
        
        return output_path
    
    def grid_split(self, input_path: Path, rows: int, cols: int,
                   row_positions: Optional[list[float]] = None,
                   col_positions: Optional[list[float]] = None) -> list[Path]:
        """
        按行列切割图片
        - positions 为 0-1 的相对位置
        - 返回切割后的图片路径列表
        """
        img = Image.open(input_path)
        img_width, img_height = img.size
        
        # 计算切割位置
        if row_positions and len(row_positions) == rows - 1:
            y_positions = [0] + [int(p * img_height) for p in row_positions] + [img_height]
        else:
            y_positions = [int(i * img_height / rows) for i in range(rows + 1)]
        
        if col_positions and len(col_positions) == cols - 1:
            x_positions = [0] + [int(p * img_width) for p in col_positions] + [img_width]
        else:
            x_positions = [int(i * img_width / cols) for i in range(cols + 1)]
        
        # 切割图片
        output_paths = []
        for row in range(rows):
            for col in range(cols):
                left = x_positions[col]
                upper = y_positions[row]
                right = x_positions[col + 1]
                lower = y_positions[row + 1]
                
                piece = img.crop((left, upper, right, lower))
                
                output_path = input_path.parent / f"{input_path.stem}_r{row}_c{col}{input_path.suffix}"
                piece.save(output_path)
                output_paths.append(output_path)
        
        return output_paths
    
    def split_and_compress(self, input_path: Path, rows: int, cols: int,
                           row_positions: Optional[list[float]],
                           col_positions: Optional[list[float]],
                           target_size_kb: int) -> list[Path]:
        """
        切割并压缩每个区块（按文件大小）
        """
        # 先切割
        split_paths = self.grid_split(input_path, rows, cols, 
                                       row_positions, col_positions)
        
        # 压缩每个区块
        compressed_paths = []
        for path in split_paths:
            compressed = self.compress_to_size(path, target_size_kb)
            compressed_paths.append(compressed)
            # 删除未压缩的切割文件
            if path != compressed:
                path.unlink(missing_ok=True)
        
        return compressed_paths
    
    def split_by_dimensions(self, input_path: Path, 
                            piece_width: int, piece_height: int,
                            quality: int = 85) -> list[Path]:
        """
        按指定宽高切割图片
        - 从左上角开始，按指定尺寸切割
        - 边缘不足的部分保留原尺寸
        """
        img = Image.open(input_path)
        img_width, img_height = img.size
        
        # 计算行列数
        cols = (img_width + piece_width - 1) // piece_width
        rows = (img_height + piece_height - 1) // piece_height
        
        output_paths = []
        for row in range(rows):
            for col in range(cols):
                left = col * piece_width
                upper = row * piece_height
                right = min(left + piece_width, img_width)
                lower = min(upper + piece_height, img_height)
                
                piece = img.crop((left, upper, right, lower))
                
                # 保存切割后的图片
                if piece.mode == 'RGBA':
                    piece = piece.convert('RGB')
                
                output_path = input_path.parent / f"{input_path.stem}_r{row}_c{col}.jpg"
                piece.save(output_path, 'JPEG', quality=quality, optimize=True)
                output_paths.append(output_path)
        
        return output_paths
    
    def split_and_compress_by_dimensions(self, input_path: Path,
                                          piece_width: int, piece_height: int,
                                          target_size_kb: Optional[int] = None,
                                          max_width: Optional[int] = None,
                                          max_height: Optional[int] = None,
                                          quality: int = 85) -> list[Path]:
        """
        按指定宽高切割并压缩
        - piece_width/piece_height: 切割尺寸
        - target_size_kb: 目标文件大小（可选）
        - max_width/max_height: 每块最大宽高（可选）
        """
        # 先按尺寸切割
        split_paths = self.split_by_dimensions(input_path, piece_width, piece_height, quality)
        
        # 如果不需要进一步压缩，直接返回
        if not target_size_kb and not max_width and not max_height:
            return split_paths
        
        # 压缩每个区块
        compressed_paths = []
        for path in split_paths:
            if target_size_kb:
                # 按文件大小压缩
                compressed = self.compress_to_size(path, target_size_kb)
            elif max_width or max_height:
                # 按宽高压缩
                compressed = self.compress_to_dimensions(path, max_width, max_height, quality)
            else:
                compressed = path
            
            compressed_paths.append(compressed)
            # 删除中间文件
            if path != compressed:
                path.unlink(missing_ok=True)
        
        return compressed_paths
    
    def to_ico(self, input_path: Path, 
               sizes: Optional[list[int]] = None) -> Path:
        """
        生成 ICO 文件
        - 支持标准图标尺寸
        """
        if sizes is None:
            sizes = [16, 32, 48, 256]
        
        img = Image.open(input_path)
        
        # 确保是 RGBA 模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        output_path = input_path.parent / f"{input_path.stem}.ico"
        
        # 生成不同尺寸的图标
        img.save(output_path, format='ICO', sizes=[(s, s) for s in sizes])
        
        return output_path


# 全局服务实例
image_service = ImageService()
