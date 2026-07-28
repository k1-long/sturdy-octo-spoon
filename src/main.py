"""FastAPI 应用入口 — Markdown 转 Word 文件转换工具"""

from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.converter import markdown_to_docx, validate_markdown

app = FastAPI(title="Markdown 转 Word", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def sanitize_filename(name: str) -> str:
    """清理文件名，移除不安全字符"""
    import re

    name = Path(name).stem
    name = re.sub(r'[\\/:*?"<>|\r\n\t"]', "_", name)
    return name or "document"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 — 文件上传界面"""
    return templates.TemplateResponse(request, "index.html")


@app.post("/convert")
async def convert(file: UploadFile = File(None), markdown_text: str = Form("")):
    """转换端点 — 支持文件上传和直接粘贴文本"""
    # 获取输入内容
    if file and file.filename:
        raw = await file.read()
        if len(raw) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="文件大小超过 10MB 限制")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="文件编码不支持，请使用 UTF-8 编码")
    elif markdown_text.strip():
        content = markdown_text
    else:
        raise HTTPException(status_code=400, detail="请上传文件或粘贴 Markdown 内容")

    # 验证输入
    issues = validate_markdown(content)
    if issues:
        raise HTTPException(status_code=400, detail="; ".join(issues))

    # 转换并返回
    buffer = markdown_to_docx(content)

    # 生成下载文件名
    original_name = sanitize_filename(file.filename) if file and file.filename else "document"
    output_name = original_name + ".docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )


@app.get("/health")
async def health():
    """健康检查端点（CI/CD 验证用）"""
    return {"status": "ok", "version": app.version}
