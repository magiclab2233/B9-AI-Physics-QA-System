import pytest
from fastapi.testclient import TestClient
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from src.api import app

client = TestClient(app)

def setup_module(module):
    """测试模块初始化"""
    # 确保测试数据目录存在
    os.makedirs("data", exist_ok=True)

def teardown_module(module):
    """测试模块清理"""
    # 清理测试数据
    for kb_file in os.listdir("data"):
        if kb_file.endswith("_knowledge_base.json") or kb_file.endswith("_index.faiss"):
            os.remove(os.path.join("data", kb_file))

def test_create_knowledge_base():
    """测试创建知识库"""
    # 准备测试数据
    test_documents = [
        {
            "id": "1",
            "text": "Python是一种高级编程语言",
            "source": "编程百科"
        },
        {
            "id": "2",
            "text": "Java也是一种编程语言",
            "source": "编程百科"
        }
    ]
    
    # 发送创建请求
    response = client.post(
        "/knowledge-base",
        json={
            "name": "test_kb",
            "documents": test_documents
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_kb"
    assert data["document_count"] == 2
    
    # 验证文件是否创建
    assert os.path.exists("data/test_kb_knowledge_base.json")
    assert os.path.exists("data/test_kb_index.faiss")

def test_create_duplicate_knowledge_base():
    """测试创建重复的知识库"""
    # 准备测试数据
    test_documents = [
        {
            "id": "1",
            "text": "测试文档",
            "source": "测试"
        }
    ]
    
    # 第一次创建
    client.post(
        "/knowledge-base",
        json={
            "name": "duplicate_kb",
            "documents": test_documents
        }
    )
    
    # 尝试重复创建
    response = client.post(
        "/knowledge-base",
        json={
            "name": "duplicate_kb",
            "documents": test_documents
        }
    )
    
    # 验证响应
    assert response.status_code == 400
    assert "已存在" in response.json()["detail"]

def test_list_knowledge_bases():
    """测试获取知识库列表"""
    # 准备测试数据
    test_documents = [
        {
            "id": "1",
            "text": "测试文档1",
            "source": "测试"
        }
    ]
    
    # 创建测试知识库
    client.post(
        "/knowledge-base",
        json={
            "name": "list_test_kb",
            "documents": test_documents
        }
    )
    
    # 获取列表
    response = client.get("/knowledge-base")
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(kb["name"] == "list_test_kb" for kb in data)

def test_delete_knowledge_base():
    """测试删除知识库"""
    # 准备测试数据
    test_documents = [
        {
            "id": "1",
            "text": "测试文档",
            "source": "测试"
        }
    ]
    
    # 创建测试知识库
    client.post(
        "/knowledge-base",
        json={
            "name": "delete_test_kb",
            "documents": test_documents
        }
    )
    
    # 删除知识库
    response = client.delete("/knowledge-base/delete_test_kb")
    
    # 验证响应
    assert response.status_code == 200
    assert "已成功删除" in response.json()["message"]
    
    # 验证文件是否删除
    assert not os.path.exists("data/delete_test_kb_knowledge_base.json")
    assert not os.path.exists("data/delete_test_kb_index.faiss")

def test_delete_nonexistent_knowledge_base():
    """测试删除不存在的知识库"""
    response = client.delete("/knowledge-base/nonexistent_kb")
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]

def test_search():
    """测试搜索功能"""
    # 准备测试数据
    test_documents = [
        {
            "id": "1",
            "text": "Python是一种高级编程语言",
            "source": "编程百科"
        },
        {
            "id": "2",
            "text": "Java也是一种编程语言",
            "source": "编程百科"
        }
    ]
    
    # 创建测试知识库
    client.post(
        "/knowledge-base",
        json={
            "name": "search_test_kb",
            "documents": test_documents
        }
    )
    
    # 执行搜索
    response = client.post(
        "/search",
        json={
            "query": "什么是Python",
            "kb_name": "search_test_kb",
            "top_k": 1
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert len(data["scores"]) == 1
    assert "Python" in data["results"][0]["text"]

def test_search_nonexistent_knowledge_base():
    """测试在不存在的知识库中搜索"""
    response = client.post(
        "/search",
        json={
            "query": "测试查询",
            "kb_name": "nonexistent_kb",
            "top_k": 5
        }
    )
    assert response.status_code == 400
    assert "不存在" in response.json()["detail"] 