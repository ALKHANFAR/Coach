"""إدارة الـ AI Prompts - الأهم في النظام!"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from datetime import datetime
from app.schemas import PromptUpdate, PromptResponse
from app.db import get_db
from app.models import AIPrompt
from app.ai.prompts.coach_prompts import AVAILABLE_VARIABLES as COACH_VARS
from app.ai.prompts.orchestrator_prompts import AVAILABLE_VARIABLES as ORCHESTRATOR_VARS
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/prompts", tags=["AI Prompts Management"])

@router.get("/{agent_type}", response_model=List[PromptResponse])
async def get_agent_prompts(agent_type: str):
    """عرض جميع prompts للـ agent مع إمكانية التعديل"""
    try:
        db = await get_db()
        
        # جلب من قاعدة البيانات
        prompts = []
        async for prompt_doc in db.ai_prompts.find({"agent_type": agent_type}):
            prompts.append(PromptResponse(
                id=str(prompt_doc["_id"]),
                agent_type=prompt_doc["agent_type"],
                prompt_name=prompt_doc["prompt_name"],
                template=prompt_doc["template"],
                variables=prompt_doc.get("variables", {}),
                is_active=prompt_doc["is_active"],
                updated_at=prompt_doc["updated_at"]
            ))
        
        # إذا لم توجد prompts في قاعدة البيانات، أضف الافتراضية
        if not prompts:
            await _initialize_default_prompts(agent_type)
            return await get_agent_prompts(agent_type)
        
        return prompts
        
    except Exception as e:
        logger.error(f"Error getting prompts for {agent_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompts")

@router.put("/{agent_type}/{prompt_name}", response_model=PromptResponse)
async def update_prompt(agent_type: str, prompt_name: str, prompt_data: PromptUpdate):
    """تحديث prompt معين (للمدراء غير التقنيين)"""
    try:
        db = await get_db()
        
        # البحث عن الـ prompt الموجود
        existing_prompt = await db.ai_prompts.find_one({
            "agent_type": agent_type,
            "prompt_name": prompt_name
        })
        
        if existing_prompt:
            # تحديث موجود
            await db.ai_prompts.update_one(
                {"_id": existing_prompt["_id"]},
                {
                    "$set": {
                        "template": prompt_data.template,
                        "variables": prompt_data.variables or {},
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # إنشاء جديد
            new_prompt = AIPrompt(
                agent_type=agent_type,
                prompt_name=prompt_name,
                template=prompt_data.template,
                variables=prompt_data.variables or {}
            )
            await db.ai_prompts.insert_one(new_prompt.dict(by_alias=True))
        
        # إرجاع النسخة المحدثة
        updated_prompt = await db.ai_prompts.find_one({
            "agent_type": agent_type,
            "prompt_name": prompt_name
        })
        
        return PromptResponse(
            id=str(updated_prompt["_id"]),
            agent_type=updated_prompt["agent_type"],
            prompt_name=updated_prompt["prompt_name"],
            template=updated_prompt["template"],
            variables=updated_prompt.get("variables", {}),
            is_active=updated_prompt["is_active"],
            updated_at=updated_prompt["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error updating prompt {agent_type}/{prompt_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prompt")

@router.post("/{agent_type}/test")
async def test_prompt(agent_type: str, test_data: Dict[str, Any]):
    """اختبار الـ prompt مع بيانات تجريبية قبل التطبيق"""
    try:
        # جلب الـ prompt
        db = await get_db()
        prompt_doc = await db.ai_prompts.find_one({
            "agent_type": agent_type,
            "prompt_name": test_data.get("prompt_name", "system"),
            "is_active": True
        })
        
        if not prompt_doc:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # تنسيق القالب مع البيانات التجريبية
        template = prompt_doc["template"]
        variables = test_data.get("variables", {})
        
        try:
            formatted_prompt = template.format(**variables)
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing variable: {e}",
                "available_variables": _get_available_variables(agent_type)
            }
        
        return {
            "success": True,
            "formatted_prompt": formatted_prompt,
            "original_template": template,
            "variables_used": variables
        }
        
    except Exception as e:
        logger.error(f"Error testing prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to test prompt")

@router.get("/templates")
async def get_prompt_templates():
    """جلب جميع القوالب الجاهزة"""
    return {
        "coach": {
            "available_variables": COACH_VARS,
            "performance_templates": ["excellent", "good", "needs_improvement", "critical"],
            "departments": ["sales", "marketing", "tech", "sondos"]
        },
        "orchestrator": {
            "available_variables": ORCHESTRATOR_VARS,
            "project_templates": ["website_launch", "marketing_campaign", "sales_increase"]
        }
    }

@router.get("/{agent_type}/edit", response_class=HTMLResponse)
async def edit_prompt_form(agent_type: str):
    """صفحة HTML بسيطة لتعديل الـ prompts"""
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تعديل Prompts - {agent_type}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            h1 {{ color: #333; text-align: center; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            textarea {{ height: 200px; resize: vertical; }}
            button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            .variables {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; }}
            .variable {{ display: inline-block; background: #e9ecef; padding: 2px 6px; margin: 2px; border-radius: 3px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>تعديل Prompts - {agent_type}</h1>
            <form id="promptForm">
                <div class="form-group">
                    <label for="promptName">اسم الـ Prompt:</label>
                    <input type="text" id="promptName" name="prompt_name" value="system" required>
                </div>
                <div class="form-group">
                    <label for="template">القالب:</label>
                    <textarea id="template" name="template" placeholder="اكتب الـ prompt هنا..." required></textarea>
                </div>
                <button type="submit">حفظ التغييرات</button>
            </form>
            
            <div class="variables">
                <h3>المتغيرات المتاحة:</h3>
                <div id="variablesList">
                    <!-- سيتم ملؤها بـ JavaScript -->
                </div>
            </div>
        </div>
        
        <script>
            // جلب المتغيرات المتاحة
            fetch('/prompts/templates')
                .then(response => response.json())
                .then(data => {{
                    const variables = data.{agent_type}.available_variables || {{}};
                    const variablesList = document.getElementById('variablesList');
                    
                    Object.entries(variables).forEach(([key, value]) => {{
                        const span = document.createElement('span');
                        span.className = 'variable';
                        span.textContent = key + ': ' + value;
                        variablesList.appendChild(span);
                    }});
                }});
            
            // معالجة إرسال النموذج
            document.getElementById('promptForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {{
                    template: formData.get('template'),
                    variables: {{}}
                }};
                
                try {{
                    const response = await fetch(`/prompts/{agent_type}/${{formData.get('prompt_name')}}`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(data)
                    }});
                    
                    if (response.ok) {{
                        alert('تم حفظ التغييرات بنجاح!');
                    }} else {{
                        alert('حدث خطأ في الحفظ');
                    }}
                }} catch (error) {{
                    alert('حدث خطأ في الاتصال');
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

async def _initialize_default_prompts(agent_type: str):
    """تهيئة الـ prompts الافتراضية في قاعدة البيانات"""
    db = await get_db()
    
    if agent_type == "coach":
        from app.ai.prompts.coach_prompts import COACH_AI_SYSTEM_PROMPT, COACH_USER_TEMPLATE
        
        prompts = [
            {
                "agent_type": "coach",
                "prompt_name": "system",
                "template": COACH_AI_SYSTEM_PROMPT,
                "variables": {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "agent_type": "coach", 
                "prompt_name": "user_template",
                "template": COACH_USER_TEMPLATE,
                "variables": {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    elif agent_type == "orchestrator":
        from app.ai.prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT, ORCHESTRATOR_USER_TEMPLATE
        
        prompts = [
            {
                "agent_type": "orchestrator",
                "prompt_name": "system", 
                "template": ORCHESTRATOR_SYSTEM_PROMPT,
                "variables": {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "agent_type": "orchestrator",
                "prompt_name": "user_template",
                "template": ORCHESTRATOR_USER_TEMPLATE,
                "variables": {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
    else:
        return
    
    # إدراج الـ prompts
    await db.ai_prompts.insert_many(prompts)

def _get_available_variables(agent_type: str) -> Dict[str, str]:
    """جلب المتغيرات المتاحة للـ agent"""
    if agent_type == "coach":
        return COACH_VARS
    elif agent_type == "orchestrator":
        return ORCHESTRATOR_VARS
    return {}
