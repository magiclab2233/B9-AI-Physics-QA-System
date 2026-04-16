# 向量搜索服务

这是一个基于 FastAPI 和 FAISS 的向量搜索服务，支持多个知识库的向量化存储和相似度搜索。

## 功能特点

- 支持多个独立知识库
- 使用多语言预训练模型进行文本向量化
- 基于 FAISS 的高效向量相似度搜索
- RESTful API 接口
- 支持 Docker 部署
- 知识库的创建、删除和列表管理

## 环境准备

1. 安装必要的系统依赖：
```bash
# 在macOS上：
brew install python@3.8  # 推荐使用Python 3.8-3.11

# 在Ubuntu/Debian上：
sudo apt-get update
sudo apt-get install python3.8 python3.8-venv python3-distutils python3-dev  # 或对应版本的python3.9/3.10/3.11
```

2. 创建并激活虚拟环境：
```bash
# 删除旧的虚拟环境（如果存在）
deactivate
rm -rf venv

# 使用Python 3.8-3.11创建新的虚拟环境
python3.8 -m venv venv  # 或使用python3.9/3.10/3.11

# 激活虚拟环境
# 在Windows上：
venv\Scripts\activate
# 在macOS/Linux上：
source venv/bin/activate

# 验证Python版本
python --version  # 应该显示Python 3.8.x - 3.11.x
```

3. 安装依赖：
```bash
# 首先确保pip是最新版本
python -m pip install --upgrade pip

# 然后安装项目依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 准备知识库

将知识库文件放在 `data` 目录下，命名格式为：`{知识库名称}_knowledge_base.json`

知识库文件格式示例：
```json
[
    {
        "id": "1",
        "text": "文档内容1",
        "source": "来源1"
    },
    {
        "id": "2",
        "text": "文档内容2",
        "source": "来源2"
    }
]
```

### 2. 构建向量索引

为指定知识库构建向量索引：

```bash
python src/build_index.py --kb_name 知识库名称
```

### 3. 启动服务

```bash
python src/api.py
```

服务将在 http://localhost:8000 启动。

### 4. 使用API进行查询

```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "查询文本", "kb_name": "知识库名称", "top_k": 5}'
```

响应示例：
```json
{
    "results": [
        {
            "id": "1",
            "text": "匹配的文本内容",
            "source": "来源"
        }
    ],
    "scores": [0.123]
}
```

## 完整使用示例

```bash
# 1. 克隆项目
git clone <项目地址>
cd vecsearch

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python src/api.py

# 5. 创建知识库
curl -X POST "http://localhost:8000/knowledge-base" \
     -H "Content-Type: application/json" \
     -d '{
         "name": "tech",
         "documents": [
             {
                 "id": "1",
                 "text": "Python是一种高级编程语言",
                 "source": "编程百科"
             }
         ]
     }'

# 6. 获取知识库列表
curl "http://localhost:8000/knowledge-base"

# 7. 搜索
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "什么是Python", "kb_name": "tech", "top_k": 3}'

# 8. 删除知识库
curl -X DELETE "http://localhost:8000/knowledge-base/tech"
```

## API接口说明

### 知识库管理

#### POST /knowledge-base
创建新的知识库

请求体：
```json
{
    "name": "知识库名称",
    "documents": [
        {
            "id": "1",
            "text": "文档内容1",
            "source": "来源1"
        },
        {
            "id": "2",
            "text": "文档内容2",
            "source": "来源2"
        }
    ]
}
```

响应体：
```json
{
    "name": "知识库名称",
    "document_count": 2
}
```

#### DELETE /knowledge-base/{kb_name}
删除指定的知识库

响应体：
```json
{
    "message": "知识库 {kb_name} 已成功删除"
}
```

#### GET /knowledge-base
获取所有知识库列表

响应体：
```json
[
    {
        "name": "知识库1",
        "document_count": 10
    },
    {
        "name": "知识库2",
        "document_count": 5
    }
]
```

### 搜索接口

#### POST /search

请求体：
```json
{
    "query": "查询文本",
    "kb_name": "知识库名称",
    "top_k": 5
}
```

响应体：
```json
{
    "results": [
        {
            "id": "1",
            "text": "匹配的文本内容",
            "source": "来源"
        }
    ],
    "scores": [0.123]
}
```

## 项目结构

```
.
├── README.md
├── requirements.txt
├── venv/                # 虚拟环境目录
├── data/
│   ├── tech_knowledge_base.json
│   ├── tech_index.faiss
│   ├── medical_knowledge_base.json
│   └── medical_index.faiss
└── src/
    ├── api.py
    ├── build_index.py
    └── vector_store.py
```

## 注意事项

1. 推荐使用Python 3.8-3.11版本，这些版本与项目依赖包有最好的兼容性
2. 确保在虚拟环境中运行所有命令
3. 如果遇到权限问题，可能需要使用管理员权限运行命令
4. 在Windows系统上，如果遇到curl命令不可用，可以使用Postman或其他API测试工具
5. 知识库文件必须按照 `{知识库名称}_knowledge_base.json` 的格式命名
6. 每个知识库都需要单独构建索引
7. 首次运行时会下载预训练模型，可能需要一些时间

## Docker部署

1. 构建Docker镜像：
```bash
docker build -t vecsearch .
```

2. 运行Docker容器：
```bash
docker run -d -p 8000:8000 --name vecsearch vecsearch
```

3. 测试API：
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "查询文本", "kb_name": "tech", "top_k": 5}'
``` 