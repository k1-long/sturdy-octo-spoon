# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Markdown → 富文本转换器。纯前端单 HTML 文件，无第三方依赖，自研 Markdown 解析器。

## 技术架构

- `index.html` — 全部代码（HTML + CSS + JavaScript），约 630 行
- Markdown 解析：自实现，非 marked.js 等第三方库
- 渲染模式：实时输入 → 预览，无后端
- 复制的板：原生 Clipboard API（`ClipboardItem`），同时写入 `text/html` 和 `text/plain`

## Markdown 解析器结构（index.html 内）

| 函数 | 职责 |
|------|------|
| `parseInline()` | 行内格式：加粗、斜体、链接、图片、代码、删除线 |
| `convert()` | 块级解析主入口：标题、表格、引用、列表、代码块、分割线、段落 |
| `buildTable()` / `parseTableCells()` | GFM 表格解析和渲染 |
| `buildCleanHTML()` | 复制时对 HTML 做清洗（去除主题色、保留结构样式） |
| `buildPlainText()` | 从 HTML 提取纯文本（表格转 tab 分隔、列表编号等） |

## 常见操作

```bash
# 本地预览（用任何静态服务器）
npx serve .
# 或者直接在浏览器打开 index.html（file:// 协议）
```

无需安装依赖、无需构建步骤。修改 `index.html` 后刷新即可看到效果。

## 约束

- 所有代码在 `index.html` 一个文件中
- 自研解析器，除非必要不引入第三方库
- 复制功能依赖 `navigator.clipboard.write()`，需要在 HTTPS 或 localhost 下使用
- `.claude/` 目录不进版本控制
