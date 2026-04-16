import json
import os
from vector_store import VectorStore
import argparse

def build_vector_index(kb_name: str):
    """构建指定知识库的向量索引"""
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 构建知识库和索引文件路径
    kb_path = os.path.join("data", f"{kb_name}_knowledge_base.json")
    index_path = os.path.join("data", f"{kb_name}_index.faiss")
    
    # 检查知识库文件是否存在
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"知识库文件 {kb_path} 不存在")
    
    # 加载知识库
    with open(kb_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    # 初始化向量存储
    vector_store = VectorStore()
    
    # 构建索引
    vector_store.build_index(documents, kb_name)
    
    # 保存索引
    vector_store.save_index(index_path, kb_name)
    print(f"知识库 {kb_name} 的向量索引构建完成")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建向量索引")
    parser.add_argument("--kb_name", type=str, required=True, help="知识库名称")
    args = parser.parse_args()
    
    build_vector_index(args.kb_name) 