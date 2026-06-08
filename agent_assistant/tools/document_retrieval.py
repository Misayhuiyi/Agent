"""
文档检索工具
"""
from typing import List, Optional, Dict, Any
from .base import BaseTool, ToolResult, ToolParameter
import os
import json


class DocumentRetrievalTool(BaseTool):
    """文档检索工具，支持向量检索和关键词检索"""
    
    def __init__(self, documents_path: Optional[str] = None):
        super().__init__()
        self.documents_path = documents_path or "./data/documents"
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.embedding_model = None
        self._load_documents()
    
    def _get_name(self) -> str:
        return "document_retrieval"
    
    def _get_description(self) -> str:
        return "从文档库中检索相关信息。支持语义检索和关键词检索，返回与查询最相关的文档片段。"
    
    def _get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="检索查询文本",
                required=True
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="返回最相关的文档数量",
                required=False,
                default=3
            ),
            ToolParameter(
                name="search_type",
                type="string",
                description="检索类型：semantic（语义检索）或 keyword（关键词检索）",
                required=False,
                default="semantic",
                enum=["semantic", "keyword"]
            )
        ]
    
    def _load_documents(self):
        """加载文档"""
        # 示例文档
        self.documents = [
            {
                "id": 1,
                "title": "公司请假制度",
                "content": "员工年假为5-15天，根据工龄确定。工龄1-3年为5天，3-5年为7天，5-10年为10天，10年以上为15天。病假需提供医院证明，每年累计不超过30天。",
                "metadata": {"category": "人事制度", "update_time": "2024-01-01"}
            },
            {
                "id": 2,
                "title": "报销流程",
                "content": "员工报销需在费用发生后30天内提交。报销单据需包含发票、费用说明和审批人签字。差旅费报销需提前提交出差申请。报销金额超过5000元需部门经理审批。",
                "metadata": {"category": "财务制度", "update_time": "2024-02-15"}
            },
            {
                "id": 3,
                "title": "技术架构说明",
                "content": "系统采用微服务架构，使用Python和Go语言开发。前端使用React框架，后端使用FastAPI。数据库采用PostgreSQL和Redis。消息队列使用RabbitMQ。",
                "metadata": {"category": "技术文档", "update_time": "2024-03-10"}
            },
            {
                "id": 4,
                "title": "产品发布流程",
                "content": "产品发布需经过开发、测试、预发布、生产四个环境。每个环境部署前需通过自动化测试。生产环境发布需提前24小时提交发布申请，并获得技术负责人审批。",
                "metadata": {"category": "研发流程", "update_time": "2024-01-20"}
            },
            {
                "id": 5,
                "title": "绩效考核标准",
                "content": "绩效考核分为S、A、B、C四个等级。S级为卓越，A级为优秀，B级为良好，C级为待改进。考核维度包括工作质量、工作效率、团队协作、创新能力等。",
                "metadata": {"category": "人事制度", "update_time": "2024-02-01"}
            }
        ]
        
        # 尝试加载嵌入模型（可选）
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self._build_embeddings()
        except Exception as e:
            print(f"警告: 无法加载嵌入模型，将使用关键词检索: {e}")
            self.embedding_model = None
    
    def _build_embeddings(self):
        """构建文档嵌入"""
        if self.embedding_model:
            texts = [doc["content"] for doc in self.documents]
            self.embeddings = self.embedding_model.encode(texts).tolist()
    
    def execute(self, **kwargs) -> ToolResult:
        """执行文档检索"""
        query = kwargs.get("query", "").strip()
        top_k = kwargs.get("top_k", 3)
        search_type = kwargs.get("search_type", "semantic")
        
        if not query:
            return ToolResult(
                success=False,
                result=None,
                error="查询文本不能为空"
            )
        
        if not self.documents:
            return ToolResult(
                success=False,
                result=None,
                error="文档库为空"
            )
        
        try:
            if search_type == "semantic" and self.embedding_model:
                results = self._semantic_search(query, top_k)
            else:
                results = self._keyword_search(query, top_k)
            
            return ToolResult(
                success=True,
                result=results,
                metadata={
                    "query": query,
                    "search_type": search_type,
                    "total_found": len(results)
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"检索错误: {str(e)}"
            )
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict]:
        """语义检索"""
        import numpy as np
        
        # 计算查询向量
        query_embedding = self.embedding_model.encode([query])[0]
        
        # 计算相似度
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity))
        
        # 排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = []
        for i, score in similarities[:top_k]:
            doc = self.documents[i].copy()
            doc["score"] = float(score)
            results.append(doc)
        
        return results
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """关键词检索"""
        query_keywords = set(query.lower().split())
        
        results = []
        for doc in self.documents:
            # 计算关键词匹配度
            content_keywords = set(doc["content"].lower().split())
            title_keywords = set(doc["title"].lower().split())
            
            content_matches = len(query_keywords & content_keywords)
            title_matches = len(query_keywords & title_keywords)
            
            # 标题匹配权重更高
            score = content_matches + title_matches * 2
            
            if score > 0:
                doc_copy = doc.copy()
                doc_copy["score"] = score
                results.append(doc_copy)
        
        # 排序并返回top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]