"""Agent Management Router"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.ai.agent_manager import agent_manager
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/agents", tags=["Agent Management"])

@router.get("/status")
async def get_agents_status():
    """جلب حالة جميع الـ Agents"""
    try:
        status = await agent_manager.get_agent_status()
        return {
            "success": True,
            "agents_status": status,
            "total_agents": len(status)
        }
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{agent_type}")
async def get_agent_status(agent_type: str):
    """جلب حالة Agent معين"""
    try:
        status = await agent_manager.get_agent_status(agent_type)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "success": True,
            "agent_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_type} status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_agents_health():
    """فحص صحة جميع الـ Agents"""
    try:
        health = await agent_manager.get_agent_health()
        return {
            "success": True,
            "health_status": health
        }
    except Exception as e:
        logger.error(f"Error getting agents health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart/{agent_type}")
async def restart_agent(agent_type: str):
    """إعادة تشغيل Agent معين"""
    try:
        result = await agent_manager.restart_agent(agent_type)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"],
            "agent_type": agent_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting agent {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/{agent_type}/{task_name}")
async def execute_agent_task(agent_type: str, task_name: str, data: Dict[str, Any]):
    """تنفيذ مهمة على Agent معين"""
    try:
        result = await agent_manager.execute_agent_task(agent_type, task_name, **data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "result": result["result"],
            "execution_time": result["execution_time"],
            "agent_type": agent_type,
            "task": task_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task {task_name} on agent {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coordinate/{coordination_type}")
async def coordinate_agents(coordination_type: str, data: Dict[str, Any]):
    """تنسيق بين الـ Agents لمهمة معقدة"""
    try:
        result = await agent_manager.coordinate_agents(coordination_type, data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "coordination_result": result,
            "coordination_type": coordination_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error coordinating agents for {coordination_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_agents_stats():
    """جلب إحصائيات مفصلة لجميع الـ Agents"""
    try:
        stats = {}
        for agent_type in agent_manager.agent_stats:
            agent_stats = agent_manager.agent_stats[agent_type]
            
            # حساب معدل النجاح
            success_rate = 0
            if agent_stats["total_requests"] > 0:
                success_rate = (agent_stats["successful_requests"] / agent_stats["total_requests"]) * 100
            
            stats[agent_type] = {
                "total_requests": agent_stats["total_requests"],
                "successful_requests": agent_stats["successful_requests"],
                "failed_requests": agent_stats["failed_requests"],
                "success_rate": round(success_rate, 2),
                "average_response_time": round(agent_stats["average_response_time"], 3),
                "last_activity": agent_stats["last_activity"].isoformat() if agent_stats["last_activity"] else None
            }
        
        return {
            "success": True,
            "agents_stats": stats,
            "summary": {
                "total_agents": len(stats),
                "total_requests": sum(s["total_requests"] for s in stats.values()),
                "overall_success_rate": round(
                    sum(s["success_rate"] for s in stats.values()) / len(stats) if stats else 0, 2
                )
            }
        }
    except Exception as e:
        logger.error(f"Error getting agents stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_available_agents():
    """قائمة الـ Agents المتاحة"""
    try:
        agents_list = []
        for agent_type, agent in agent_manager.agents.items():
            agents_list.append({
                "agent_type": agent_type,
                "class_name": agent.__class__.__name__,
                "description": agent.__doc__ or f"Agent of type {agent_type}",
                "available_tasks": _get_available_tasks(agent_type)
            })
        
        return {
            "success": True,
            "available_agents": agents_list,
            "total_count": len(agents_list)
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_available_tasks(agent_type: str) -> list:
    """جلب المهام المتاحة لـ Agent معين"""
    tasks_map = {
        "coach": ["generate_message"],
        "orchestrator": ["expand_goal"]
    }
    return tasks_map.get(agent_type, [])
