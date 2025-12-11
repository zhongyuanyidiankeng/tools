"""
文本服务属性测试
"""
import json
import re
from hypothesis import given, strategies as st, settings, assume
from services.text_service import TextService


class TestJSONFormatRoundTrip:
    """
    **Feature: online-tools-platform, Property 12: JSON 格式化往返一致性**
    **Validates: Requirements 3.1**
    
    For any valid JSON string, formatting it and then parsing the result
    SHALL produce data equivalent to parsing the original string.
    """
    
    def setup_method(self):
        self.service = TextService()
    
    @settings(max_examples=100, deadline=None)
    @given(st.recursive(
        st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | st.text(),
        lambda children: st.lists(children) | st.dictionaries(st.text(), children),
        max_leaves=10
    ))
    def test_json_format_roundtrip(self, data):
        """
        **Feature: online-tools-platform, Property 12: JSON 格式化往返一致性**
        
        对于任何有效的 JSON 数据，格式化后解析应该得到等价的数据
        """
        # 将数据转为 JSON 字符串
        original_json = json.dumps(data, ensure_ascii=False)
        
        # 格式化
        result = self.service.format_json(original_json)
        
        # 验证格式化成功
        assert result.success, f"Format failed: {result.error_message}"
        
        # 解析格式化后的结果
        parsed = json.loads(result.formatted)
        
        # 验证数据等价
        assert parsed == data, f"Data mismatch: {parsed} != {data}"


class TestBase64RoundTrip:
    """
    **Feature: online-tools-platform, Property 13: Base64 编解码往返一致性**
    **Validates: Requirements 3.2, 3.3**
    
    For any text string, encoding to Base64 and then decoding
    SHALL return the original text exactly.
    """
    
    def setup_method(self):
        self.service = TextService()
    
    @settings(max_examples=100, deadline=None)
    @given(st.text())
    def test_base64_roundtrip(self, text: str):
        """
        **Feature: online-tools-platform, Property 13: Base64 编解码往返一致性**
        
        对于任何文本，编码后解码应该返回原始文本
        """
        encoded = self.service.base64_encode(text)
        decoded = self.service.base64_decode(encoded)
        assert decoded == text, f"Roundtrip failed: '{text}' -> '{encoded}' -> '{decoded}'"


class TestRegexCorrectness:
    """
    **Feature: online-tools-platform, Property 14: 正则匹配正确性**
    **Validates: Requirements 3.4**
    
    For any valid regex pattern and test string, the returned matches
    SHALL be identical to Python's re.findall() results.
    """
    
    def setup_method(self):
        self.service = TextService()
    
    @settings(max_examples=100, deadline=None)
    @given(
        st.sampled_from([r'\d+', r'\w+', r'[a-z]+', r'\s+', r'[A-Z][a-z]*']),
        st.text(min_size=0, max_size=100)
    )
    def test_regex_matches_python_re(self, pattern: str, test_string: str):
        """
        **Feature: online-tools-platform, Property 14: 正则匹配正确性**
        
        服务返回的匹配结果应该与 Python re 模块一致
        """
        # 使用服务测试
        result = self.service.test_regex(pattern, test_string)
        
        # 使用 Python re 模块验证
        expected_matches = re.findall(pattern, test_string)
        
        # 验证匹配数量一致
        assert result.match_count == len(expected_matches), \
            f"Match count mismatch: {result.match_count} != {len(expected_matches)}"
        
        # 验证匹配文本一致
        actual_texts = [m.text for m in result.matches]
        assert actual_texts == expected_matches, \
            f"Match texts mismatch: {actual_texts} != {expected_matches}"


class TestMarkdownValidity:
    """
    **Feature: online-tools-platform, Property 15: Markdown 转换有效性**
    **Validates: Requirements 3.5**
    
    For any Markdown text, converting to HTML SHALL produce valid, parseable HTML.
    """
    
    def setup_method(self):
        self.service = TextService()
    
    @settings(max_examples=100, deadline=None)
    @given(st.text(min_size=0, max_size=500))
    def test_markdown_produces_string(self, markdown_text: str):
        """
        **Feature: online-tools-platform, Property 15: Markdown 转换有效性**
        
        对于任何 Markdown 文本，转换应该产生字符串输出
        """
        html = self.service.markdown_to_html(markdown_text)
        assert isinstance(html, str), f"Expected string, got {type(html)}"
    
    def test_markdown_basic_elements(self):
        """
        **Feature: online-tools-platform, Property 15: Markdown 转换有效性**
        
        基本 Markdown 元素应该正确转换为 HTML
        """
        test_cases = [
            ("# Heading", "<h1>"),
            ("**bold**", "<strong>"),
            ("*italic*", "<em>"),
            ("[link](http://example.com)", "<a href="),
            ("- item", "<li>"),
        ]
        
        for md, expected_tag in test_cases:
            html = self.service.markdown_to_html(md)
            assert expected_tag in html, f"Expected {expected_tag} in HTML for '{md}', got: {html}"
