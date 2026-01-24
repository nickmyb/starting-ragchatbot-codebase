# CLAUDE.md

Claude Code 项目级指南。

## 仓库说明

本项目是 `teaching-nick-llm` 下的独立子仓库（sub repo）。对 `claude_code` 的修改应提交到本仓库，而非父仓库。

## 项目概述

这是 [DeepLearning.AI Claude Code 课程](https://learn.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant) 中的实践项目。

可以根据课程视频配合 [课程代码仓库](https://github.com/https-deeplearning-ai/sc-claude-code-files) 中的 Prompt 从零开始复现整个项目。

项目是一个**课程材料 RAG（检索增强生成）系统**，允许用户通过自然语言查询课程内容，获得智能的上下文感知回答。

核心功能：
- 语义搜索课程材料
- Claude AI 生成智能回答
- 工具调用模式（Claude 按需搜索）
- 会话上下文管理
- 来源引用展示

## 技术栈

**后端：**
- FastAPI + Uvicorn（Web 框架）
- ChromaDB（向量数据库）
- Anthropic SDK（Claude API）
- Sentence Transformers（嵌入模型）

**前端：**
- 纯 HTML/CSS/JavaScript
- Marked.js（Markdown 渲染）
- 深色主题 UI

**依赖管理：**
- uv + pyproject.toml
- Python 3.13

## 项目结构

```
claude_code/
├── backend/
│   ├── app.py              # FastAPI 入口，API 路由
│   ├── config.py           # 配置管理
│   ├── rag_system.py       # RAG 编排器（核心逻辑）
│   ├── ai_generator.py     # Claude API 集成
│   ├── vector_store.py     # ChromaDB 封装
│   ├── document_processor.py # 文档解析与分块
│   ├── search_tools.py     # Claude 工具定义
│   ├── session_manager.py  # 会话管理
│   ├── models.py           # Pydantic 数据模型
│   └── chroma_db/          # 向量数据库存储
├── frontend/
│   ├── index.html          # 主页面
│   ├── script.js           # 前端逻辑
│   └── style.css           # 样式
├── docs/                   # 课程材料文档
├── .env                    # 环境变量（需自行创建）
├── .env.example            # 环境变量模板
├── pyproject.toml          # 项目依赖
├── uv.lock                 # 依赖锁定
└── run.sh                  # 启动脚本
```

## 常用命令

```bash
# 安装依赖
uv sync

# 启动服务（推荐）
./run.sh

# 手动启动
cd backend && uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 添加新依赖
uv add package_name
```

## 访问地址

- Web 界面：http://localhost:8000
- API 文档：http://localhost:8000/docs

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/query` | 提交查询，返回回答和来源 |
| GET | `/api/courses` | 获取课程列表和统计 |

## 环境配置

1. 复制 `.env.example` 为 `.env`
2. 设置 `ANTHROPIC_API_KEY`

## 架构要点

**工具调用模式：** Claude 根据需要决定是否搜索，而非每次预搜索，减少不必要的 API 调用。

**双集合设计：** ChromaDB 使用 `course_catalog`（元数据）和 `course_content`（内容）两个集合。

**会话管理：** 限制历史记录为 2 轮对话，平衡上下文和 token 消耗。

## 开发规范

**后端：**
- 新增 API 路由在 `app.py`
- 工具扩展在 `search_tools.py` 添加
- 数据模型定义在 `models.py`

**前端：**
- 保持深色主题风格
- 使用 CSS 变量定义颜色
- API 调用使用相对路径 `/api/`

**文档格式：** 课程文档遵循固定格式：
```
Course Title: [标题]
Course Link: [链接]
Course Instructor: [讲师]
Lesson 0: [课程标题]
Lesson Link: [链接]
[课程内容]
```
