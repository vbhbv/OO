# app.py - نقطة الدخول الرئيسية لتطبيق FastAPI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import uvicorn
import json

# استيرادات مطلقة مصححة
from EmotionalProcessorV4 import EmotionalEngine 
from EmotionalState import EmotionalState

# تهيئة التطبيق والحالة
app = FastAPI()
state_manager = EmotionalState()
emotional_engine = EmotionalEngine(state_manager) # تهيئة محرك المشاعر

# تعريف نموذج البيانات للمدخلات
class PromptRequest(BaseModel):
    prompt: str
    action_is_ethical: bool
    external_reward_magnitude: float
    user_tone_is_critical: bool

# تعريف نموذج البيانات للمخرجات (للتطوير 21)
class EmotionResponse(BaseModel):
    response_text: str
    guilt: float
    pride: float
    fear: float
    joy: float
    empathy: float
    resentment: float
    lambda_value: float
    confidence_score: float
    maturity: float

@app.get("/")
def read_root():
    return {"message": "Emotional AI Engine V4 running with FastAPI."}

@app.post("/process_prompt", response_model=EmotionResponse)
async def process_prompt_endpoint(request: PromptRequest):
    try:
        # معالجة الطلب باستخدام المحرك العاطفي
        result = emotional_engine.process_prompt(
            user_prompt=request.prompt,
            action_is_ethical=request.action_is_ethical,
            external_reward_magnitude=request.external_reward_magnitude,
            user_tone_is_critical=request.user_tone_is_critical
        )
        
        # تجهيز البيانات للإخراج
        new_state = result['new_state']
        
        return EmotionResponse(
            response_text=result['response_text'],
            guilt=new_state.get('guilt', 0.0),
            pride=new_state.get('pride', 0.0),
            fear=new_state.get('fear', 0.0),
            joy=new_state.get('joy', 0.0),
            empathy=new_state.get('empathy', 0.0),
            resentment=new_state.get('resentment', 0.0),
            lambda_value=result['lambda_value'],
            confidence_score=result['confidence_score'],
            maturity=new_state.get('maturity', 1.0)
        )
        
    except Exception as e:
        print(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # تشغيل التطبيق محلياً
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv('PORT', 8000)))
