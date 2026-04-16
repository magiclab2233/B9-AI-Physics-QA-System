import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os

class VectorStore:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        self.knowledge_bases = {}  # 存储不同知识库的索引和文档
        self.dimension = 384  # 默认维度，根据模型可能不同
        
    def build_index(self, documents: List[Dict[str, str]], kb_name: str):
        """构建指定知识库的向量索引"""
        texts = [doc["text"] for doc in documents]
        
        # 生成向量
        embeddings = self.model.encode(texts)
        
        # 创建FAISS索引
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # 存储知识库信息
        self.knowledge_bases[kb_name] = {
            'index': index,
            'documents': documents
        }
        
    def search(self, query: str, kb_name: str, k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        """在指定知识库中搜索相似文档"""
        if kb_name not in self.knowledge_bases:
            raise ValueError(f"知识库 {kb_name} 不存在")
            
        kb = self.knowledge_bases[kb_name]
        index = kb['index']
        documents = kb['documents']
        
        # 生成查询向量
        query_embedding = self.model.encode([query])
        
        # 搜索
        distances, indices = index.search(query_embedding.astype('float32'), k)
        
        # 返回结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # FAISS可能返回-1作为无效索引
                results.append((documents[idx], float(distances[0][i])))
                
        return results
    
    def save_index(self, path: str, kb_name: str):
        """保存指定知识库的索引到文件"""
        if kb_name not in self.knowledge_bases:
            raise ValueError(f"知识库 {kb_name} 不存在")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.knowledge_bases[kb_name]['index'], path)
        
    def load_index(self, path: str, documents: List[Dict[str, str]], kb_name: str):
        """加载指定知识库的索引"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"索引文件 {path} 不存在")
            
        index = faiss.read_index(path)
        self.knowledge_bases[kb_name] = {
            'index': index,
            'documents': documents
        } 