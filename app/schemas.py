"""Schemas للـ API requests/responses"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

# Schemas إنشاء المهام
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_email: EmailStr
    due_date: datetime

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    assignee_email: str
    due_date: datetime
    status: str
    source: str

# Schemas KPIs
class KPIUpsert(BaseModel):
    user_email: EmailStr
    month: str  # YYYY-MM
    target: int
    actual: int

class KPIResponse(BaseModel):
    id: str
    user_email: str
    department: str
    month: str
    target: int
    actual: int
    drift: float

# Schemas الكوتش
class CoachPing(BaseModel):
    user_email: EmailStr
    department: str
    summary: Optional[str] = None

class CoachResponse(BaseModel):
    message: str
    performance_level: str
    should_send: bool

# Schemas الـ Prompts
class PromptUpdate(BaseModel):
    template: str
    variables: Optional[Dict[str, Any]] = {}

class PromptResponse(BaseModel):
    id: str
    agent_type: str
    prompt_name: str
    template: str
    variables: Dict[str, Any]
    is_active: bool
    updated_at: datetime

# Schemas الـ Digests
class ManagerDigestRequest(BaseModel):
    manager_email: EmailStr

class ExecutiveDigestRequest(BaseModel):
    pass  # لا يحتاج بيانات إضافية

class DigestResponse(BaseModel):
    sent: bool
    preview: str
    recipients: List[str]

# Schemas المشاريع
class GoalToProject(BaseModel):
    goal_text: str
    timeline: Optional[str] = None
    budget: Optional[str] = None
    special_requirements: Optional[str] = None

class TaskBreakdown(BaseModel):
    id: int
    title: str
    description: str
    department: str
    suggested_assignee: Optional[str]
    priority: str
    estimated_days: int
    depends_on: Optional[List[int]]
    deliverables: List[str]

class ProjectResponse(BaseModel):
    project_title: str
    project_description: str
    estimated_duration: str
    tasks: List[TaskBreakdown]
    success_criteria: List[str]
    potential_risks: List[str]
    recommended_timeline: str
