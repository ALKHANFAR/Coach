"""Tasks management endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import TaskCreate, TaskResponse
from app.db import get_db
from app.models import Task, User
from bson import ObjectId
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """إنشاء مهمة جديدة"""
    try:
        db = await get_db()
        
        # البحث عن المستخدم
        user = await db.users.find_one({"email": task_data.assignee_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # إنشاء المهمة
        task = Task(
            title=task_data.title,
            description=task_data.description,
            assignee_user_id=user["_id"],
            due_date=task_data.due_date,
            created_by_user_id=user["_id"]  # مبسط - نفس الشخص ينشئ ويستقبل
        )
        
        # حفظ في قاعدة البيانات
        result = await db.tasks.insert_one(task.dict(by_alias=True))
        task.id = result.inserted_id
        
        # إرجاع الاستجابة
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            assignee_email=task_data.assignee_email,
            due_date=task.due_date,
            status=task.status,
            source=task.source
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(assignee_email: Optional[str] = Query(None)):
    """جلب المهام"""
    try:
        db = await get_db()
        
        # بناء الاستعلام
        query = {}
        if assignee_email:
            user = await db.users.find_one({"email": assignee_email})
            if user:
                query["assignee_user_id"] = user["_id"]
        
        # جلب المهام
        tasks = []
        async for task_doc in db.tasks.find(query):
            # جلب بيانات المستخدم
            user = await db.users.find_one({"_id": task_doc["assignee_user_id"]})
            
            tasks.append(TaskResponse(
                id=str(task_doc["_id"]),
                title=task_doc["title"],
                description=task_doc.get("description"),
                assignee_email=user["email"] if user else "unknown",
                due_date=task_doc["due_date"],
                status=task_doc["status"],
                source=task_doc["source"]
            ))
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")
