# 测试共享 fixtures — 所有 test_*.py 文件中可直接使用
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    """FastAPI 测试客户端 — 用于集成测试"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
