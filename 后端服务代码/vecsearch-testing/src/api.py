from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from src.vector_store import VectorStore
import json
import os

app = FastAPI(title="向量搜索API")

# 初始化向量存储
vector_store = VectorStore()

class SearchRequest(BaseModel):
    query: str
    kb_name: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, str]]
    scores: List[float]

class KnowledgeBaseCreate(BaseModel):
    name: str
    documents: List[Dict[str, str]]

class KnowledgeBaseResponse(BaseModel):
    name: str
    document_count: int

@app.on_event("startup")
async def startup_event():
    """服务启动时加载知识库和向量索引"""
    try:
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        
        # 遍历data目录下的所有知识库
        for kb_file in os.listdir("data"):
            if kb_file.endswith("_knowledge_base.json"):
                kb_name = kb_file.replace("_knowledge_base.json", "")
                kb_path = os.path.join("data", kb_file)
                index_path = os.path.join("data", f"{kb_name}_index.faiss")
                
                # 加载知识库
                with open(kb_path, "r", encoding="utf-8") as f:
                    documents = json.load(f)
                
                # 加载向量索引
                try:
                    vector_store.load_index(index_path, documents, kb_name)
                    print(f"已加载知识库: {kb_name}")
                except FileNotFoundError:
                    # 如果索引文件不存在，重新构建
                    vector_store.build_index(documents, kb_name)
                    vector_store.save_index(index_path, kb_name)
                    print(f"已重建知识库索引: {kb_name}")
    except Exception as e:
        print(f"启动时加载数据失败: {str(e)}")
        raise

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """在指定知识库中搜索相似文档"""
    try:
        results = vector_store.search(request.query, request.kb_name, request.top_k)
        return SearchResponse(
            results=[doc for doc, _ in results],
            scores=[score for _, score in results]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.post("/knowledge-base", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """创建新的知识库"""
    try:
        kb_name = request.name
        kb_path = os.path.join("data", f"{kb_name}_knowledge_base.json")
        index_path = os.path.join("data", f"{kb_name}_index.faiss")
        
        # 检查知识库是否已存在
        if os.path.exists(kb_path):
            raise HTTPException(status_code=400, detail=f"知识库 {kb_name} 已存在")
        
        try:
            # 保存知识库文档
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(request.documents, f, ensure_ascii=False, indent=2)
            
            # 构建向量索引
            vector_store.build_index(request.documents, kb_name)
            vector_store.save_index(index_path, kb_name)
            
            return KnowledgeBaseResponse(
                name=kb_name,
                document_count=len(request.documents)
            )
        except Exception as e:
            # 如果创建过程中出错，清理已创建的文件
            if os.path.exists(kb_path):
                os.remove(kb_path)
            if os.path.exists(index_path):
                os.remove(index_path)
            raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识库失败: {str(e)}")

@app.delete("/knowledge-base/{kb_name}")
async def delete_knowledge_base(kb_name: str):
    """删除指定的知识库"""
    try:
        kb_path = os.path.join("data", f"{kb_name}_knowledge_base.json")
        index_path = os.path.join("data", f"{kb_name}_index.faiss")
        
        # 检查知识库是否存在
        if not os.path.exists(kb_path):
            raise HTTPException(status_code=404, detail=f"知识库 {kb_name} 不存在")
        
        try:
            # 删除文件
            os.remove(kb_path)
            if os.path.exists(index_path):
                os.remove(index_path)
            
            # 从内存中移除
            if kb_name in vector_store.knowledge_bases:
                del vector_store.knowledge_bases[kb_name]
            
            return {"message": f"知识库 {kb_name} 已成功删除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除知识库文件失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")

@app.get("/knowledge-base", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """获取所有知识库列表"""
    try:
        knowledge_bases = []
        for kb_file in os.listdir("data"):
            if kb_file.endswith("_knowledge_base.json"):
                kb_name = kb_file.replace("_knowledge_base.json", "")
                kb_path = os.path.join("data", kb_file)
                
                with open(kb_path, "r", encoding="utf-8") as f:
                    documents = json.load(f)
                
                knowledge_bases.append(KnowledgeBaseResponse(
                    name=kb_name,
                    document_count=len(documents)
                ))
        
        return knowledge_bases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 