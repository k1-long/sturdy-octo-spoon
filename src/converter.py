"""Markdown 转 Word 文档的核心转换模块"""

from io import BytesIO

from docx import Document
from docx.shared import Pt, Inches
import markdown


def markdown_to_html(md_text: str) -> str:
    """将 Markdown 文本转换为 HTML"""
    return markdown.markdown(md_text, extensions=["extra", "codehilite", "tables"])


def markdown_to_docx(md_text: str) -> BytesIO:
    """将 Markdown 文本转换为 Word 文档（返回文件流）

    调用方负责关闭返回的 BytesIO。
    """
    html = markdown_to_html(md_text)
    doc = Document()

    # 设置默认字体
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Arial"
    font.size = Pt(11)

    # 将 HTML 内容按段落拆分写入
    paragraphs = html.split("\n")
    for para_text in paragraphs:
        para_text = para_text.strip()
        if para_text:
            doc.add_paragraph(para_text)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def validate_markdown(md_text: str) -> list[str]:
    """验证 Markdown 文本，返回问题列表（空列表表示无问题）"""
    issues = []
    if not isinstance(md_text, str):
        issues.append("输入必须是字符串类型")
        return issues
    if not md_text.strip():
        issues.append("输入内容为空")
    return issues
