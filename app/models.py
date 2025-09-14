"""نماذج البيانات الأساسية"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId

class PyObjectId(ObjectId):
    """تحويل ObjectId لـ Pydantic v2 - الحل النهائي"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return {"type": "string"}
    
    def __str__(self):
        return str(super())
    
    def __repr__(self):
        return f"PyObjectId('{str(self)}')"

# نماذج المستخدمين
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    name: str
    role: str  # employee, manager, executive
    department: str  # sales, marketing, tech, sondos
    manager_id: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# نماذج المهام
class Task(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: Optional[str] = None
    assignee_user_id: PyObjectId
    due_date: datetime
    status: str = "open"  # open, in_progress, done, overdue
    created_by_user_id: PyObjectId
    source: str = "system"  # slack, email, form, system
    project_id: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# نماذج KPIs
class KPI(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    department: str
    month: str  # YYYY-MM
    target: int
    actual: int
    drift: float = 0.0  # محسوب تلقائياً
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# نماذج الرسائل
class Message(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[PyObjectId] = None
    type: str  # coach_reply, daily_digest, executive_digest, alert
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# نماذج الـ AI Prompts (الأهم!)
class AIPrompt(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    agent_type: str  # coach, orchestrator
    prompt_name: str
    template: str
    variables: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# نماذج المشاريع
class Project(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    owner_user_id: PyObjectId
    goal_deadline: datetime
    status: str = "planning"  # planning, active, completed, cancelled
    tasks_ids: List[PyObjectId] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
