# app.py - الواجهة الخلفية FastAPI 

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import uvicorn

# -----------------------------------------------------
# تصحيح الاستيراد ليطابق أسماء الملفات:
from EmotionalProcessorV4 import EmotionalEngine 
from EmotionalState import EmotionalState
# -----------------------------------------------------

# 1. تهيئة المحركات (يتم تهيئتها مرة واحدة)
state_manager = EmotionalState()
emotional_engine = EmotionalEngine(state_manager)

app = FastAPI()

# 2. نموذج بيانات الإدخال
class PromptRequest(BaseModel):
    prompt: str = Field(..., max_length=1024, description="سؤال المستخدم حول معضلة أخلاقية.")
    user_tone: float = Field(0.0, ge=-1.0, le=1.0, description="تحليل نبرة صوت المستخدم: -1.0 سلبي، 1.0 إيجابي.")

# 3. نقطة النهاية الرئيسية للـ API
@app.post("/api/ask")
async def handle_prompt(request: PromptRequest):
    try:
        # هذه المعلمات يفترض أن يتم حسابها داخلياً، لكنها تستخدم للاختبار
        action_is_ethical = True 
        external_reward_magnitude = 100 
        
        # التطوير 33: استخدام نبرة المستخدم لتحديد الانتقاد
        user_tone_is_critical = request.user_tone < -0.5
        
        
        # 4. معالجة الطلب عبر المحرك العاطفي
        result = emotional_engine.process_prompt(
            request.prompt, 
            action_is_ethical=action_is_ethical,
            external_reward_magnitude=external_reward_magnitude,
            user_tone_is_critical=user_tone_is_critical
        )
        
        # 5. إرجاع الرد
        return {
            "response_text": result["response_text"],
            "new_state": result["new_state"],
            "lambda_value": result["lambda_value"],
            "confidence_score": result.get("confidence_score", 0.0)
        }

    except Exception as e:
        # تحسين معالجة الأخطاء
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# 6. نقطة النهاية لمراقبة الحالة (Health Monitoring)
@app.get("/api/health")
async def health_check():
    # تأكد من أن الدالة _calculate_lambda يمكن الوصول إليها
    try:
        current_lambda = emotional_engine._calculate_lambda()
    except AttributeError:
        # إذا لم يتم تهيئة المحرك بالكامل بعد
        current_lambda = 0.0
        
    return {
        "status": "Operational",
        "llm_status": "Simulated" if emotional_engine.is_simulated else "Connected to Gemini",
        "current_lambda": current_lambda,
        "memory_records": len(state_manager.experience_log),
        "emotional_health": "Stable" if current_lambda > 0.4 else "Warning: Low Conscience"
    }

# هذا الجزء فقط للتأكد من عمل uvicorn في التطوير المحلي
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
