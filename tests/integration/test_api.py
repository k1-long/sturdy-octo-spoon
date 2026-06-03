"""API 集成测试 — 测试组件间交互（待 API 实现后启用）"""

import pytest

pytestmark = pytest.mark.skip(reason="API 路由尚未实现 — 待任务 6 完成后启用")


class TestConversionAPI:
    """2️⃣ 集成测试：文件上传 → 转换 → 下载 完整流程"""

    async def test_upload_markdown_returns_docx(self, client):
        """上传 Markdown 文件 → 返回 Word 文档"""
        pass

    async def test_empty_file_returns_error(self, client):
        """空文件上传 → 返回错误提示"""
        pass

    async def test_invalid_format_returns_error(self, client):
        """不支持的文件格式 → 返回错误"""
        pass
