"""converter.py 单元测试 — 测试单个组件的转换功能"""

import pytest
from src.converter import markdown_to_html, markdown_to_docx, validate_markdown


class TestMarkdownToHtml:
    """1️⃣ 单元测试：HTML 转换"""

    def test_basic_conversion(self):
        """测试基本 Markdown 转 HTML"""
        result = markdown_to_html("# Hello\n\nWorld")
        assert "<h1>Hello</h1>" in result
        assert "<p>World</p>" in result

    def test_code_block(self):
        """测试代码块转换"""
        md = "```python\ndef hello():\n    pass\n```"
        result = markdown_to_html(md)
        assert "<code>" in result

    def test_table(self):
        """测试表格转换"""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = markdown_to_html(md)
        assert "<table>" in result


class TestMarkdownToDocx:
    """1️⃣ 单元测试：Word 文档转换"""

    def test_basic_conversion(self):
        """基本转换生成有效 docx"""
        buffer = markdown_to_docx("# Test\n\nHello World")
        content = buffer.read()
        assert len(content) > 0
        buffer.close()

    def test_unicode_content(self):
        """3️⃣ 边界条件：Unicode 和表情符号"""
        buffer = markdown_to_docx("# Unicode 测试 🎉\n\n中文内容")
        content = buffer.read()
        assert len(content) > 0
        buffer.close()

    def test_large_content(self):
        """3️⃣ 边界条件：超长文本"""
        long_text = "# Test\n\n" + "Hello " * 1000
        buffer = markdown_to_docx(long_text)
        content = buffer.read()
        assert len(content) > 0
        buffer.close()


class TestValidateMarkdown:
    """验证函数测试"""

    def test_valid_input(self):
        """正常输入无问题"""
        issues = validate_markdown("# Valid markdown")
        assert issues == []

    def test_empty_input(self):
        """3️⃣ 边界条件：空输入"""
        issues = validate_markdown("")
        assert len(issues) == 1
        assert "为空" in issues[0]

    def test_whitespace_only(self):
        """3️⃣ 边界条件：仅空白字符"""
        issues = validate_markdown("   \n  \t  ")
        assert len(issues) == 1

    def test_non_string_input(self):
        """4️⃣ 错误恢复：非字符串类型输入"""
        issues = validate_markdown(123)
        assert len(issues) == 1
        assert "字符串" in issues[0]

    def test_none_input(self):
        """4️⃣ 错误恢复：None 输入"""
        issues = validate_markdown(None)
        assert len(issues) >= 1
