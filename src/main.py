"""FastAPI 应用入口 — Markdown 转 Word 文件转换工具"""

from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.converter import markdown_to_docx, validate_markdown

app = FastAPI(title="文件格式转换工具", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 — 文件上传界面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert")
async def convert(file: UploadFile = File(None), markdown_text: str = Form(None)):
    """转换端点 — 支持文件上传和直接粘贴文本"""
    # 获取输入内容
    if file and file.filename:
        content = (await file.read()).decode("utf-8")
    elif markdown_text:
        content = markdown_text
    else:
        return HTMLResponse("<p>请上传文件或粘贴 Markdown 内容</p>", status_code=400)

    # 验证输入
    issues = validate_markdown(content)
    if issues:
        return HTMLResponse(f"<p>输入无效：{'; '.join(issues)}</p>", status_code=400)

    # 转换并返回
    buffer = markdown_to_docx(content)

    # 生成下载文件名（基于原文件名或默认名）
    original_name = file.filename if file and file.filename else "document"
    output_name = Path(original_name).stem + ".docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )


@app.get("/health")
async def health():
    """健康检查端点（CI/CD 验证用）"""
    return {"status": "ok", "version": app.version}
