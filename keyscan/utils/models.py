from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TemplateInfo(BaseModel):
    name: str
    author: Optional[str] = None
    severity: Optional[str] = None

class RequestModel(BaseModel):
    type: str = "http" # 'http' or 'command'
    method: str = "GET"
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    command: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)

class MatcherModel(BaseModel):
    type: str # 'status', 'word', 'regex'
    status: Optional[List[int]] = None
    words: Optional[List[str]] = None
    regex: Optional[List[str]] = None
    condition: Optional[str] = "and" # or "or"

class TemplateModel(BaseModel):
    id: str
    info: TemplateInfo
    requests: List[RequestModel]
    matchers: List[MatcherModel]

class ClassificationResult(BaseModel):
    service: str
    confidence: float
    regex_match: bool = False
    prefix_match: bool = False

class ValidationResult(BaseModel):
    key: str
    service: str
    status: str # valid, invalid, unknown
    confidence: float
    message: Optional[str] = None
