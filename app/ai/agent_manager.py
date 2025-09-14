"""Agent Manager - مدير الـ AI Agents"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import structlog
from app.ai.coach import CoachAI
from app.ai.orchestrator import OrchestratorAI

logger = structlog.get_logger()

class AgentManager:
    """مدير مركزي لجميع الـ AI Agents"""
    
    def __init__(self):
        self.agents = {}
        self.agent_stats = {}
        self.agent_tasks = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """تهيئة جميع الـ Agents"""
        try:
            self.agents["coach"] = CoachAI()
            self.agents["orchestrator"] = OrchestratorAI()
            
            # إحصائيات الأداء
            self.agent_stats = {
                "coach": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "last_activity": None,
                    "average_response_time": 0.0
                },
                "orchestrator": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "last_activity": None,
                    "average_response_time": 0.0
                }
            }
            
            logger.info("Agent Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
    
    async def get_agent(self, agent_type: str) -> Optional[Any]:
        """جلب Agent معين"""
        if agent_type not in self.agents:
            logger.warning(f"Agent {agent_type} not found")
            return None
        
        return self.agents[agent_type]
    
    async def execute_agent_task(self, agent_type: str, task_name: str, **kwargs) -> Dict[str, Any]:
        """تنفيذ مهمة على Agent معين مع تتبع الأداء"""
        start_time = datetime.now()
        
        try:
            agent = await self.get_agent(agent_type)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_type} not found",
                    "agent_type": agent_type,
                    "task": task_name
                }
            
            # تنفيذ المهمة
            if agent_type == "coach" and task_name == "generate_message":
                result = await agent.generate_coach_message(kwargs.get("user_data", {}))
            elif agent_type == "orchestrator" and task_name == "expand_goal":
                result = await agent.expand_goal_to_tasks(kwargs.get("goal_text", ""), **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task {task_name} for agent {agent_type}",
                    "agent_type": agent_type,
                    "task": task_name
                }
            
            # تحديث الإحصائيات
            await self._update_agent_stats(agent_type, True, start_time)
            
            return {
                "success": True,
                "result": result,
                "agent_type": agent_type,
                "task": task_name,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_name} on agent {agent_type}: {e}")
            await self._update_agent_stats(agent_type, False, start_time)
            
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
                "task": task_name,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _update_agent_stats(self, agent_type: str, success: bool, start_time: datetime):
        """تحديث إحصائيات Agent"""
        if agent_type not in self.agent_stats:
            return
        
        stats = self.agent_stats[agent_type]
        stats["total_requests"] += 1
        stats["last_activity"] = datetime.now()
        
        if success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        # حساب متوسط وقت الاستجابة
        execution_time = (datetime.now() - start_time).total_seconds()
        if stats["average_response_time"] == 0:
            stats["average_response_time"] = execution_time
        else:
            stats["average_response_time"] = (stats["average_response_time"] + execution_time) / 2
    
    async def get_agent_status(self, agent_type: str = None) -> Dict[str, Any]:
        """جلب حالة Agent أو جميع الـ Agents"""
        if agent_type:
            if agent_type not in self.agent_stats:
                return {"error": f"Agent {agent_type} not found"}
            
            return {
                "agent_type": agent_type,
                "status": "active" if agent_type in self.agents else "inactive",
                "stats": self.agent_stats[agent_type]
            }
        
        # حالة جميع الـ Agents
        all_status = {}
        for agent_type in self.agent_stats:
            all_status[agent_type] = {
                "status": "active" if agent_type in self.agents else "inactive",
                "stats": self.agent_stats[agent_type]
            }
        
        return all_status
    
    async def restart_agent(self, agent_type: str) -> Dict[str, Any]:
        """إعادة تشغيل Agent معين"""
        try:
            if agent_type == "coach":
                self.agents["coach"] = CoachAI()
            elif agent_type == "orchestrator":
                self.agents["orchestrator"] = OrchestratorAI()
            else:
                return {
                    "success": False,
                    "error": f"Unknown agent type: {agent_type}"
                }
            
            # إعادة تعيين الإحصائيات
            self.agent_stats[agent_type] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "last_activity": None,
                "average_response_time": 0.0
            }
            
            logger.info(f"Agent {agent_type} restarted successfully")
            
            return {
                "success": True,
                "message": f"Agent {agent_type} restarted successfully",
                "agent_type": agent_type
            }
            
        except Exception as e:
            logger.error(f"Failed to restart agent {agent_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type
            }
    
    async def get_agent_health(self) -> Dict[str, Any]:
        """فحص صحة جميع الـ Agents"""
        health_status = {
            "overall_status": "healthy",
            "agents": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for agent_type in self.agents:
            try:
                agent = self.agents[agent_type]
                stats = self.agent_stats[agent_type]
                
                # حساب معدل النجاح
                success_rate = 0
                if stats["total_requests"] > 0:
                    success_rate = (stats["successful_requests"] / stats["total_requests"]) * 100
                
                # تحديد الحالة
                if success_rate >= 90:
                    status = "excellent"
                elif success_rate >= 75:
                    status = "good"
                elif success_rate >= 50:
                    status = "warning"
                else:
                    status = "critical"
                    health_status["overall_status"] = "unhealthy"
                
                health_status["agents"][agent_type] = {
                    "status": status,
                    "success_rate": success_rate,
                    "total_requests": stats["total_requests"],
                    "average_response_time": stats["average_response_time"],
                    "last_activity": stats["last_activity"].isoformat() if stats["last_activity"] else None
                }
                
            except Exception as e:
                health_status["agents"][agent_type] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def coordinate_agents(self, task_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """تنسيق بين الـ Agents لمهمة معقدة"""
        try:
            if task_type == "project_with_coaching":
                # مشروع مع رسائل تحفيز
                goal_text = data.get("goal_text", "")
                user_data = data.get("user_data", {})
                
                # تفكيك الهدف
                orchestrator_result = await self.execute_agent_task(
                    "orchestrator", 
                    "expand_goal", 
                    goal_text=goal_text
                )
                
                # رسالة تحفيز
                coach_result = await self.execute_agent_task(
                    "coach", 
                    "generate_message", 
                    user_data=user_data
                )
                
                return {
                    "success": True,
                    "project_plan": orchestrator_result.get("result"),
                    "motivation_message": coach_result.get("result"),
                    "coordination_type": "project_with_coaching"
                }
            
            elif task_type == "performance_analysis":
                # تحليل الأداء مع توصيات
                user_data = data.get("user_data", {})
                
                # رسالة تحفيز
                coach_result = await self.execute_agent_task(
                    "coach", 
                    "generate_message", 
                    user_data=user_data
                )
                
                # اقتراح مشروع تحسين
                improvement_goal = f"تحسين أداء {user_data.get('name', 'الموظف')} في قسم {user_data.get('department', 'العام')}"
                orchestrator_result = await self.execute_agent_task(
                    "orchestrator", 
                    "expand_goal", 
                    goal_text=improvement_goal
                )
                
                return {
                    "success": True,
                    "motivation_message": coach_result.get("result"),
                    "improvement_plan": orchestrator_result.get("result"),
                    "coordination_type": "performance_analysis"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown coordination type: {task_type}"
                }
                
        except Exception as e:
            logger.error(f"Error in agent coordination: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# إنشاء instance عام
agent_manager = AgentManager()
