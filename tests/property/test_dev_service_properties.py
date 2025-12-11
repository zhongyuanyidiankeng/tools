"""
开发者工具服务属性测试
"""
import json
import base64
import re
import uuid as uuid_lib
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from services.dev_service import DevService


def create_jwt(header: dict, payload: dict) -> str:
    """创建测试用 JWT token"""
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip('=')
    
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip('=')
    
    # 假签名
    signature = base64.urlsafe_b64encode(b'fake_signature').decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{signature}"


class TestJWTDecodeCorrectness:
    """
    **Feature: online-tools-platform, Property 16: JWT 解码正确性**
    **Validates: Requirements 4.1**
    
    For any valid JWT token, decoding SHALL correctly extract the header
    and payload that match the original encoded values.
    """
    
    def setup_method(self):
        self.service = DevService()
    
    @settings(max_examples=100, deadline=None)
    @given(
        st.fixed_dictionaries({
            'alg': st.sampled_from(['HS256', 'RS256', 'ES256']),
            'typ': st.just('JWT')
        }),
        st.fixed_dictionaries({
            'sub': st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'),
            'name': st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz '),
            'iat': st.integers(min_value=1000000000, max_value=2000000000)
        })
    )
    def test_jwt_decode_roundtrip(self, header: dict, payload: dict):
        """
        **Feature: online-tools-platform, Property 16: JWT 解码正确性**
        
        对于任何有效的 JWT，解码应该正确提取 header 和 payload
        """
        # 创建 JWT
        token = create_jwt(header, payload)
        
        # 解码
        result = self.service.decode_jwt(token)
        
        # 验证
        assert result.success, f"Decode failed: {result.error_message}"
        assert result.header == header, f"Header mismatch: {result.header} != {header}"
        assert result.payload == payload, f"Payload mismatch: {result.payload} != {payload}"
    
    def test_jwt_expiry_detection(self):
        """
        **Feature: online-tools-platform, Property 16: JWT 解码正确性**
        
        JWT 过期检测应该正确工作
        """
        # 创建过期的 JWT
        expired_payload = {
            'sub': 'test',
            'exp': int((datetime.now() - timedelta(hours=1)).timestamp())
        }
        expired_token = create_jwt({'alg': 'HS256', 'typ': 'JWT'}, expired_payload)
        
        result = self.service.decode_jwt(expired_token)
        assert result.success
        assert result.expired, "Should detect expired token"
        
        # 创建未过期的 JWT
        valid_payload = {
            'sub': 'test',
            'exp': int((datetime.now() + timedelta(hours=1)).timestamp())
        }
        valid_token = create_jwt({'alg': 'HS256', 'typ': 'JWT'}, valid_payload)
        
        result = self.service.decode_jwt(valid_token)
        assert result.success
        assert not result.expired, "Should not detect as expired"


class TestCronExpressionValidity:
    """
    **Feature: online-tools-platform, Property 17: Cron 表达式有效性**
    **Validates: Requirements 4.2**
    
    For any valid cron parameters, the generated expression SHALL be parseable
    and the next run times SHALL be chronologically ordered.
    """
    
    def setup_method(self):
        self.service = DevService()
    
    @settings(max_examples=100, deadline=None)
    @given(
        st.sampled_from(['*', '0', '15', '30', '45']),
        st.sampled_from(['*', '0', '6', '12', '18']),
        st.sampled_from(['*', '1', '15', '28']),
        st.sampled_from(['*', '1', '6', '12']),
        st.sampled_from(['*', '0', '1', '5'])
    )
    def test_cron_generation_valid(self, minute: str, hour: str, 
                                    day: str, month: str, weekday: str):
        """
        **Feature: online-tools-platform, Property 17: Cron 表达式有效性**
        
        对于任何有效的 cron 参数，生成的表达式应该是有效的
        """
        result = self.service.generate_cron(minute, hour, day, month, weekday)
        
        assert result.success, f"Cron generation failed: {result.error_message}"
        assert result.expression == f"{minute} {hour} {day} {month} {weekday}"
        assert result.description is not None
    
    def test_cron_next_runs_ordered(self):
        """
        **Feature: online-tools-platform, Property 17: Cron 表达式有效性**
        
        下次执行时间应该按时间顺序排列
        """
        result = self.service.generate_cron("0", "*", "*", "*", "*")
        
        assert result.success
        
        # 如果有 next_runs，验证它们是有序的
        if result.next_runs:
            for i in range(len(result.next_runs) - 1):
                assert result.next_runs[i] < result.next_runs[i + 1], \
                    "Next runs should be chronologically ordered"


class TestUUIDFormatValidity:
    """
    **Feature: online-tools-platform, Property 18: UUID 格式有效性**
    **Validates: Requirements 4.3**
    
    For any generated UUID, it SHALL conform to UUID v4 format
    (8-4-4-4-12 hex digits with version 4 indicator).
    """
    
    def setup_method(self):
        self.service = DevService()
    
    @settings(max_examples=100, deadline=None)
    @given(st.integers())
    def test_uuid_format_valid(self, _):
        """
        **Feature: online-tools-platform, Property 18: UUID 格式有效性**
        
        生成的 UUID 应该符合 UUID v4 格式
        """
        generated = self.service.generate_uuid()
        
        # 验证格式 (8-4-4-4-12)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, generated, re.IGNORECASE), \
            f"Invalid UUID v4 format: {generated}"
        
        # 验证可以被 uuid 库解析
        parsed = uuid_lib.UUID(generated)
        assert parsed.version == 4, f"UUID version should be 4, got {parsed.version}"
    
    def test_uuid_uniqueness(self):
        """
        **Feature: online-tools-platform, Property 18: UUID 格式有效性**
        
        生成的 UUID 应该是唯一的
        """
        uuids = [self.service.generate_uuid() for _ in range(100)]
        assert len(set(uuids)) == 100, "Generated UUIDs should be unique"
