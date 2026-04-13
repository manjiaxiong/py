# ===========================================
# models.py — Docs Copilot 数据模型
# ===========================================
# 所有 Pydantic 模型集中管理
# ===========================================

from pydantic import BaseModel, Field
from typing import Optional


class IndexRequest(BaseModel):
    """索引文档请求"""
    text: str = Field(description="文档内容")
    source: str = Field(default="unknown", description="文档来源（文件名等）")
    chunk_size: int = Field(default=500, ge=50, le=2000, description="分块大小")


class IndexResponse(BaseModel):
    """索引文档响应"""
    message: str
    chunks_count: int
    source: str


class AskRequest(BaseModel):
    """提问请求"""
    question: str = Field(min_length=1, max_length=2000, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="检索结果数量")
    stream: bool = Field(default=False, description="是否流式输出")


class SourceItem(BaseModel):
    """引用来源"""
    source: str
    preview: str
    relevance: float


class AskResponse(BaseModel):
    """提问响应（非流式）"""
    answer: str
    sources: list[SourceItem]
    question: str


class ChatMessage(BaseModel):
    """对话消息"""
    role: str  # "user" | "ai"
    content: str
    sources: Optional[list[SourceItem]] = None


class ChatHistory(BaseModel):
    """对话历史"""
    messages: list[ChatMessage] = []
