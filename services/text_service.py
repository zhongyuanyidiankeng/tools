"""
文本工具服务模块
提供 JSON 格式化、Base64 编解码、正则测试、Markdown 转换等功能
"""
import json
import base64
import re
import html
from typing import Optional
from dataclasses import dataclass

# 尝试导入 markdown，如果不存在则使用简单实现
try:
    import markdown as md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


@dataclass
class FormatResult:
    """格式化结果"""
    success: bool
    formatted: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class RegexMatch:
    """正则匹配项"""
    start: int
    end: int
    text: str
    groups: list[str]


@dataclass
class RegexResult:
    """正则测试结果"""
    success: bool
    matches: list[RegexMatch]
    match_count: int
    error_message: Optional[str] = None


class TextService:
    """文本工具服务"""
    
    def format_json(self, json_str: str, indent: int = 2) -> FormatResult:
        """
        格式化 JSON 字符串
        - 验证 JSON 语法
        - 返回格式化后的字符串或错误位置
        """
        try:
            parsed = json.loads(json_str)
            formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)
            return FormatResult(success=True, formatted=formatted)
        except json.JSONDecodeError as e:
            return FormatResult(
                success=False,
                error_line=e.lineno,
                error_column=e.colno,
                error_message=str(e.msg)
            )
    
    def base64_encode(self, text: str) -> str:
        """Base64 编码"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def base64_decode(self, encoded: str) -> str:
        """Base64 解码"""
        return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
    
    def test_regex(self, pattern: str, test_string: str, 
                   flags_str: Optional[str] = None) -> RegexResult:
        """
        正则表达式测试
        - 返回所有匹配项及其分组
        """
        try:
            # 解析标志
            flags = 0
            if flags_str:
                flag_map = {
                    'i': re.IGNORECASE,
                    'm': re.MULTILINE,
                    's': re.DOTALL,
                    'x': re.VERBOSE,
                }
                for char in flags_str.lower():
                    if char in flag_map:
                        flags |= flag_map[char]
            
            # 编译正则表达式
            regex = re.compile(pattern, flags)
            
            # 查找所有匹配
            matches = []
            for match in regex.finditer(test_string):
                groups = list(match.groups()) if match.groups() else []
                matches.append(RegexMatch(
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    groups=groups
                ))
            
            return RegexResult(
                success=True,
                matches=matches,
                match_count=len(matches)
            )
        except re.error as e:
            return RegexResult(
                success=False,
                matches=[],
                match_count=0,
                error_message=str(e)
            )
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Markdown 转 HTML
        - 支持常见 Markdown 语法
        """
        if HAS_MARKDOWN:
            return md_lib.markdown(
                markdown_text,
                extensions=['tables', 'fenced_code']
            )
        
        # 简单的 Markdown 转换实现
        result = html.escape(markdown_text)
        
        # 标题
        result = re.sub(r'^### (.+)$', r'<h3>\1</h3>', result, flags=re.MULTILINE)
        result = re.sub(r'^## (.+)$', r'<h2>\1</h2>', result, flags=re.MULTILINE)
        result = re.sub(r'^# (.+)$', r'<h1>\1</h1>', result, flags=re.MULTILINE)
        
        # 粗体和斜体
        result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
        result = re.sub(r'\*(.+?)\*', r'<em>\1</em>', result)
        
        # 链接
        result = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', result)
        
        # 代码
        result = re.sub(r'`(.+?)`', r'<code>\1</code>', result)
        
        # 列表项
        result = re.sub(r'^- (.+)$', r'<li>\1</li>', result, flags=re.MULTILINE)
        
        # 段落（简单处理）
        lines = result.split('\n')
        processed = []
        for line in lines:
            if line.strip() and not line.startswith('<'):
                processed.append(f'<p>{line}</p>')
            else:
                processed.append(line)
        
        return '\n'.join(processed)


# 全局服务实例
text_service = TextService()
