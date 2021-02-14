from pydantic import BaseModel
from typing import List, Optional


class Document(BaseModel):
    index: Optional[str]
    text: Optional[str]
    vector: Optional[List[float]]


class DocumentText(BaseModel):
    text: str


class DocumentIndex(BaseModel):
    index: str


class SearchResult(BaseModel):
    index: str
    text: str
    score: float
