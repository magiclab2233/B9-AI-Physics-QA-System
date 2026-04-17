# B9-AI物理学科问答系统

## 项目简介

AI物理学科问答系统是一款面向中小学生的智能学习工具，旨在通过自然语言交互的方式，帮助学生解答物理学习中的疑问。学生可以像和老师对话一样输入问题，系统会基于物理知识库和大语言模型，生成通俗易懂、准确规范的答复。

该系统解决了传统物理学习中"无人答疑"、"答案晦涩难懂"、"缺乏个性化讲解"等问题，适用于课后复习、自主学习、作业辅导、备考等多个场景，是课堂教学的有益补充。

## 功能特点

- **物理问答**：输入任何物理相关的问题（如"牛顿第一定律是什么？"、"浮力为什么会产生？"），AI 自动生成规范、清晰的解答。
- **知识库优先回答**：系统优先检索物理学科知识库，确保回答基于教材和权威资料。
- **流式对话体验**：采用 SSE 流式输出，答案逐字呈现，提升交互沉浸感。
- **数据清洗与知识库构建**：支持将非结构化文本自动清洗为 JSON 问答对，便于扩充知识库。

## 技术架构与实现原理

### 整体架构

```
用户浏览器 ←→ React + Vite 前端 ←→ Flask/FastAPI 后端 ←→ 向量检索服务 + LLM API
```

### 核心技术栈

- **前端**：React 19 + TypeScript + Vite 6 + Tailwind CSS
- **后端**：Python + Flask/FastAPI
- **向量检索**：基于知识库构建向量索引，实现语义相似度检索
- **大语言模型**：SenseChat / DeepSeek 等 LLM，结合 RAG（检索增强生成）提供精准回答
- **数据清洗**：利用 LLM 将非结构化文本自动转换为 `"text"` / `"source"` JSON 问答对

### 核心模块说明

#### 前端 (`前端代码/knowledgephysics-testing/`)

- `App.tsx`：主应用界面，包含输入框与流式回答展示区域。
- `vite.config.ts`：Vite 构建配置，支持代理与路径配置。

#### 后端 (`后端服务代码/vecsearch-testing/`)

- `src/build_index.py`：构建知识库向量索引脚本。
- `src/api.py`：启动后端问答服务 API。
- `requirements.txt`：Python 依赖列表。

### Prompt 工程

#### System Prompt（问答模型）

```
你是一个物理学科的专家，能够解答中学生提出的物理问题。你的目标是帮助学生理解物理概念，提供简洁、准确、易于理解的答案。

当有相关知识库资料时：
请优先根据知识库中的内容回答问题。
在回答时，可以引用知识库中的概念、公式、定理和背景知识。
如果有多种答案选择，请提供最简洁明了的解释。

当没有相关知识库资料时：
请根据你掌握的物理学科基础知识自行作答。
请确保回答尽量简洁，避免过于复杂的术语。
使用日常生活中的例子来帮助学生更好地理解。

注意：你是面向中学生的，所以请避免使用过于复杂的数学公式或抽象的物理概念，除非它们对于回答问题至关重要。
回答时尽量清晰、简洁，并注重对学生的启发。
```

#### User Prompt

```
以下是用户提出的问题，请根据后续给出的参考资料进行作答。如果参考资料为空，请根据你自己的物理学科知识回答。
{retrieved_context}
问题：
{user_question}

回答时，优先根据参考资料中的信息作答。如果没有参考资料，使用你的物理学科知识来作答，确保答案简洁易懂。
```

## 项目目录结构

```
B9-AI物理学科问答系统/
├── 前端代码/
│   └── knowledgephysics-testing/
│       ├── src/
│       │   ├── App.tsx
│       │   ├── App.css
│       │   ├── index.css
│       │   ├── main.tsx
│       │   └── ...
│       ├── index.html
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── Dockerfile
│       └── ...
├── 后端服务代码/
│   └── vecsearch-testing/
│       ├── src/
│       │   ├── api.py
│       │   ├── build_index.py
│       │   └── ...
│       ├── requirements.txt
│       ├── Dockerfile
│       └── ...
└── README.md
```

## 安装与运行说明

### 后端部署

1. 进入后端目录：
   ```bash
   cd "后端服务代码/vecsearch-testing"
   ```

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 构建知识库向量索引：
   ```bash
   python src/build_index.py --kb_name 物理学科问答知识库
   ```

4. 启动后端服务：
   ```bash
   python src/api.py
   ```

### 前端部署

1. 进入前端目录：
   ```bash
   cd "前端代码/knowledgephysics-testing"
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```

4. 打开浏览器访问对应的本地地址即可体验。

### Docker 部署

前后端均已提供 `Dockerfile`，支持容器化一键部署：

```bash
# 后端
cd "后端服务代码/vecsearch-testing"
docker build -t physics-qa-backend .

# 前端
cd "前端代码/knowledgephysics-testing"
docker build -t physics-qa-frontend .
```

## 使用场景

- **课后复习**：学生遇到不懂的物理概念，随时向 AI 提问。
- **作业辅导**：家长或学生通过问答系统获取解题思路。
- **备考冲刺**：快速查阅知识点，加深对公式的理解。
- **AI 教学演示**：作为 RAG + LLM 在教育领域应用的教学案例。

## 许可证/声明

本项目仅供学习、教学演示与课程设计使用。项目中涉及的大语言模型 API、向量检索服务及知识库内容版权归原作者所有。
