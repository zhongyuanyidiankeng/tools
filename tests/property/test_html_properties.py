"""
HTML 页面属性测试
"""
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings


def get_all_html_files() -> list[Path]:
    """获取所有 HTML 文件"""
    static_dir = Path("static")
    if not static_dir.exists():
        return []
    return list(static_dir.rglob("*.html"))


def parse_html_meta(content: str) -> dict:
    """解析 HTML 元数据"""
    result = {}
    
    # 提取 title
    title_match = re.search(r'<title>([^<]+)</title>', content)
    result['title'] = title_match.group(1) if title_match else None
    
    # 提取 meta description
    desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
    result['description'] = desc_match.group(1) if desc_match else None
    
    # 提取 canonical URL
    canonical_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', content)
    result['canonical'] = canonical_match.group(1) if canonical_match else None
    
    return result


def parse_html_headings(content: str) -> list[int]:
    """解析 HTML 标题层级"""
    headings = re.findall(r'<h(\d)[^>]*>', content)
    return [int(h) for h in headings]


class TestPageMetadataCompleteness:
    """
    **Feature: online-tools-platform, Property 20: 页面元数据完整性**
    **Validates: Requirements 7.1**
    
    For any tool page, the rendered HTML SHALL contain a unique meta title,
    meta description, and canonical URL that differ from other tool pages.
    """
    
    def test_all_pages_have_required_meta(self):
        """
        **Feature: online-tools-platform, Property 20: 页面元数据完整性**
        
        所有页面都应该包含 title、description 和 canonical URL
        """
        html_files = get_all_html_files()
        
        if not html_files:
            return  # 跳过如果没有 HTML 文件
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            meta = parse_html_meta(content)
            
            assert meta['title'], f"{html_file}: Missing title"
            assert meta['description'], f"{html_file}: Missing meta description"
            assert meta['canonical'], f"{html_file}: Missing canonical URL"
    
    def test_pages_have_unique_titles(self):
        """
        **Feature: online-tools-platform, Property 20: 页面元数据完整性**
        
        每个页面的 title 应该是唯一的
        """
        html_files = get_all_html_files()
        
        if len(html_files) < 2:
            return
        
        titles = []
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            meta = parse_html_meta(content)
            if meta['title']:
                titles.append((html_file, meta['title']))
        
        # 检查唯一性
        title_values = [t[1] for t in titles]
        duplicates = [t for t in title_values if title_values.count(t) > 1]
        
        assert not duplicates, f"Duplicate titles found: {set(duplicates)}"


class TestHTMLSemanticStructure:
    """
    **Feature: online-tools-platform, Property 21: HTML 语义结构正确性**
    **Validates: Requirements 7.2**
    
    For any tool page, the rendered HTML SHALL have exactly one h1 element
    and heading levels SHALL not skip.
    """
    
    def test_pages_have_single_h1(self):
        """
        **Feature: online-tools-platform, Property 21: HTML 语义结构正确性**
        
        每个页面应该只有一个 h1 标签
        """
        html_files = get_all_html_files()
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            h1_count = len(re.findall(r'<h1[^>]*>', content))
            
            assert h1_count == 1, f"{html_file}: Expected 1 h1, found {h1_count}"
    
    def test_heading_levels_dont_skip(self):
        """
        **Feature: online-tools-platform, Property 21: HTML 语义结构正确性**
        
        标题层级不应该跳跃（如 h1 后直接 h3）
        """
        html_files = get_all_html_files()
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            headings = parse_html_headings(content)
            
            if len(headings) < 2:
                continue
            
            for i in range(1, len(headings)):
                prev_level = headings[i - 1]
                curr_level = headings[i]
                
                # 允许同级或下降，但上升不能跳级
                if curr_level > prev_level:
                    assert curr_level <= prev_level + 1, \
                        f"{html_file}: Heading level skipped from h{prev_level} to h{curr_level}"
