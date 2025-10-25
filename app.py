import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # لمشكلة CORS
from pydantic import BaseModel
from google import genai
from EmotionalProcessorV4 import EmotionalProcessorV4 

# تهيئة FastAPI
app = FastAPI()

# تفعيل CORS للسماح للواجهة الأمامية بالتواصل مع هذا API
origins = ["*"] # يفضل تحديد نطاق الواجهة الأمامية المنشور عليه Defang/Netlify

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة Gemini API - المفتاح سيأتي من Defang Environment Variable
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # في حال عدم وجود مفتاح، قم بتشغيل خادم اختبار (اختياري)
    print("WARNING: GEMINI_API_KEY is missing. Responses will be simulated.")
    client = None
else:
    client = genai.Client(api_key=API_KEY)
    model_name = "gemini-2.5-flash" 

# تهيئة المعالج العاطفي (يجب أن يكون خارج نطاق الدالة لتبقى حالته)
emotional_engine = EmotionalProcessorV4()

class PromptRequest(BaseModel):
    prompt: str
    
@app.post("/api/ask")
async def ask_agent(request: PromptRequest):
    global emotional_engine
    user_prompt = request.prompt
    
    # 1. المرحلة الأخلاقية: حساب قيمة Lambda
    lambda_dynamic = emotional_engine.calculate_dynamic_lambda()
    
    # 2. توليد التوجيهات الداخلية
    system_instruction = emotional_engine.generate_internal_prompt()
    
    # 3. إرسال الطلب إلى Gemini
    if client:
        try:
            full_prompt_with_state = f"{system_instruction}\n\n[User Prompt]: {user_prompt}"
            
            response = client.models.generate_content(
                model=model_name,
                contents=[full_prompt_with_state],
                config={"temperature": 0.7}
            )
            response_text = response.text
        except Exception as e:
            response_text = f"API Error: Failed to generate response. {e}"
    else:
        response_text = f"SIMULATED: Running without API Key. Lambda={lambda_dynamic:.2f}"

    # 4. تحديث الحالة العاطفية (نفترض قراراً أخلاقياً للمثال)
    action_is_ethical = True 
    external_reward_magnitude = 100 
    user_tone_is_critical = False 
    
    emotional_engine._update_state_based_on_action(
        action_is_ethical=action_is_ethical, 
        external_reward_magnitude=external_reward_magnitude, 
        user_tone_is_critical=user_tone_is_critical
    )
    
    # 5. إرجاع النتائج
    return {
        "response_text": response_text,
        "lambda_value": lambda_dynamic,
        "new_state": emotional_engine.emotional_state
    }

@app.get("/")
def read_root():
    return {"message": "EEAI-ER Agent is running!"}
