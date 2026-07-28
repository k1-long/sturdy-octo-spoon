"""API 集成测试 — 测试组件间交互"""

import io

import pytest
from docx import Document
from src.main import app


class TestHealthCheck:
    """健康检查端点"""

    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestIndexPage:
    """首页渲染"""

    async def test_index_returns_html(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert "<title>Markdown → Word" in response.text or "Markdown" in response.text


class TestConversionAPI:
    """2️⃣ 集成测试：文件上传 → 转换 → 下载 完整流程"""

    async def _check_docx_contains(self, response, expected_text):
        """验证 docx 响应中包含指定文本"""
        from io import BytesIO
        doc = Document(BytesIO(response.read()))
        texts = [p.text for p in doc.paragraphs]
        assert any(expected_text in t for t in texts), f"Expected '{expected_text}' in {texts}"
        return doc

    async def test_upload_markdown_file_returns_docx(self, client):
        """上传 Markdown 文件 → 返回 Word 文档"""
        md_content = b"# Test\n\nHello **bold** world"
        files = {"file": ("test.md", io.BytesIO(md_content), "text/markdown")}
        response = await client.post("/convert", files=files)
        assert response.status_code == 200
        assert response.headers["content-type"] == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert "attachment" in response.headers["content-disposition"]
        await self._check_docx_contains(response, "Hello")

    async def test_upload_markdown_uses_correct_filename(self, client):
        """上传文件后返回的 .docx 保留原文件名"""
        md_content = b"# Hello"
        files = {"file": ("readme.md", io.BytesIO(md_content), "text/markdown")}
        response = await client.post("/convert", files=files)
        assert response.status_code == 200
        assert 'filename="readme.docx"' in response.headers["content-disposition"]

    async def test_paste_text_returns_docx(self, client):
        """粘贴 Markdown 文本 → 返回 Word 文档"""
        data = {"markdown_text": "# Pasted\n\nContent here"}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        await self._check_docx_contains(response, "Pasted")

    async def test_no_input_returns_error(self, client):
        """无文件也无文本 → 返回 400 错误"""
        response = await client.post("/convert")
        assert response.status_code == 400

    async def test_empty_markdown_returns_error(self, client):
        """空文本内容 → 返回错误"""
        data = {"markdown_text": ""}
        response = await client.post("/convert", data=data)
        assert response.status_code == 400

    async def test_whitespace_only_returns_error(self, client):
        """仅空白字符 → 返回错误"""
        data = {"markdown_text": "   \n  "}
        response = await client.post("/convert", data=data)
        assert response.status_code == 400

    async def test_unicode_content(self, client):
        """3️⃣ 边界条件：Unicode 和中文内容"""
        md_text = "# 中文测试\n\n你好世界 🎉"
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200
        await self._check_docx_contains(response, "你好世界")

    async def test_large_content(self, client):
        """3️⃣ 边界条件：超长文本不崩溃"""
        md_text = "# Large\n\n" + "Hello " * 5000
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200
        content = response.read()
        assert len(content) > 0

    async def test_table_conversion(self, client):
        """表格 Markdown → docx"""
        md_text = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200

    async def test_code_block_conversion(self, client):
        """代码块 Markdown → docx"""
        md_text = "```python\ndef hello():\n    print('hi')\n```"
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200

    async def test_non_utf8_file_returns_error(self, client):
        """非 UTF-8 编码文件 → 返回 400"""
        files = {"file": ("test.md", b"\xff\xfe\x00\x48", "text/markdown")}
        response = await client.post("/convert", files=files)
        assert response.status_code == 400

    async def test_huge_file_returns_error(self, client):
        """超大文件（超过 10MB） → 返回 413"""
        files = {"file": ("big.md", b"x" * (11 * 1024 * 1024), "text/markdown")}
        response = await client.post("/convert", files=files)
        assert response.status_code == 413

    async def test_bold_in_table(self, client):
        """表格中的粗体格式"""
        md_text = "| A | B |\n|---|---|\n| **1** | 2 |"
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200

    async def test_nested_format(self, client):
        """嵌套内联格式：粗体中的斜体"""
        md_text = "**bold *and italic* end**"
        data = {"markdown_text": md_text}
        response = await client.post("/convert", data=data)
        assert response.status_code == 200
        await self._check_docx_contains(response, "bold")
        await self._check_docx_contains(response, "italic")
