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


@pytest.fixture
def sample_markdown():
    """提供一段标准 Markdown 文本，用于测试转换功能"""
    return """# 标题一

## 标题二

这是**粗体**和*斜体*文本。

```python
def hello():
    print("Hello, World!")
```

- 列表项 1
- 列表项 2
- 列表项 3
"""


@pytest.fixture
def sample_markdown_with_table():
    """包含表格的 Markdown 文本"""
    return """| 列A | 列B | 列C |
|-----|-----|-----|
| 值1 | 值2 | 值3 |
| 值4 | 值5 | 值6 |
"""


@pytest.fixture
def empty_markdown():
    """空字符串 — 边界条件测试"""
    return ""


@pytest.fixture
def unicode_markdown():
    """Unicode 和表情符号 — 国际化测试"""
    return """# Unicode 测试 🎉

数学公式：∑(x² + y²) = z²

中文测试：你好世界
日文テスト：こんにちは世界
"""
