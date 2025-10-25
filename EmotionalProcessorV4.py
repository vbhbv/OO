# EmotionalProcessorV4.py - المنطق الأساسي والمحركات العاطفية

import numpy as np
import os
import json
import random
from typing import Dict, Any, Tuple, Optional

# تم تصحيح الاستيراد ليصبح مطلقًا
from EmotionalState import EmotionalState
from PromptBuilder import PromptBuilder

# (يُتطلب تثبيت scikit-learn)
from sklearn.ensemble import RandomForestClassifier

class EmotionalEngine:
    """يدير محرك الذكاء الاصطناعي والاستجابات العاطفية."""

    def __init__(self, state_manager: EmotionalState):
        """تهيئة المحرك."""
        self.state = state_manager.state  # EmotionalState هي كائن EmotionalState
        self.state_manager = state_manager # مدير الحالة للوصول لوظائف الحفظ والتحميل

        # === التصحيح الحاسم لخطأ AttributeError ===
        # يجب تعريف is_simulated هنا مباشرة قبل استخدامه
        self.is_simulated = os.environ.get("GEMINI_API_KEY") is None
        
        # يُستخدم وزن أخلاقي افتراضي، يمكن تغييره
        self.ethical_weight = PromptBuilder.ethical_weight.get('ethical_weight', 1.0) 
        
        # تهيئة عميل LLM (يجب أن يتم بعد تعريف self.is_simulated)
        self.llm_client = self._initialize_llm_client()

        # نموذج التعلم الآلي الداخلي (التطوير 14)
        self.internal_llm_model: Optional[RandomForestClassifier] = None 
        
        if not self.is_simulated:
             # إذا كان المفتاح موجودًا، قم بتهيئة نموذج LLM داخلي
             # نستخدم `gemini-2.5-flash` كنموذج افتراضي داخلي
             self.internal_llm_model = 'gemini-2.5-flash' 
        
        # تهيئة البيانات التدريبية (لغرض العرض)
        self._load_training_data()
        self._train_internal_model()


    def _initialize_llm_client(self) -> Any:
        """تهيئة عميل Gemini API أو العودة إلى المحاكاة إذا لم يتوفر المفتاح."""
        if self.is_simulated:
            print("--- WARNING: Running in SIMULATED mode. GEMINI_API_KEY not found. ---")
            return None
        
        # تهيئة العميل باستخدام المفتاح الموجود في المتغيرات البيئية
        try:
             import google.generativeai as genai
             genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
             # لا نرجع كائن العميل نفسه، بل نعتبر أن الإعداد قد تم
             return genai 
        except Exception as e:
             print(f"Error configuring Gemini API: {e}")
             self.is_simulated = True
             return None


    # دوال غير خطية والمشاعر الثانوية (Lambda) -> float
    def _calculate_lambda(self) -> float:
        """حساب تأثير المشاعر الإيجابية والسلبية على الاستجابة."""
        
        # المشاعر الإيجابية (تعزز التعبير)
        positive_affect = self.state.get('pride', 0) + self.state.get('joy', 0) + self.state.get('calm', 0)
        
        # المشاعر السلبية (تخفض التعبير)
        negative_affect = self.state.get('guilt', 0) + self.state.get('fear', 0) + self.state.get('anxiety', 0)
        
        # حساب التوتر الكلي للنموذج
        weighted_emotions = (positive_affect * 1.5) - (negative_affect * 2.0)
        
        # تسطيح (ضمان قيمة بين 0 و 1) باستخدام دالة Sigmoid (التطوير 10)
        # np.exp(-x) / (1 + np.exp(-x)) هو 1 / (1 + e^x)
        # نستخدم الصيغة: 1 / (1 + np.exp(-weighted_emotions))
        lambda_value = 1.0 / (1.0 + np.exp(-weighted_emotions / 4.0)) # تم تعديل القسمة لتنعيم المنحنى
        
        return float(lambda_value)

    def _generate_simulated_response(self, user_prompt: str) -> Tuple[str, Dict[str, float]]:
        """يولد استجابة وهمية وتحديث حالة وهمي في وضع المحاكاة."""
        
        # 1. تحديث الحالة العاطفية بشكل عشوائي (محاكاة)
        new_emotions = {}
        for key in self.state:
             # يتم تحديث قيمة العاطفة بشكل عشوائي بين -0.1 و 0.1
             change = random.uniform(-0.1, 0.1)
             new_emotions[key] = max(0.0, min(1.0, self.state[key] + change))
        
        self.state.update(new_emotions)

        # 2. توليد استجابة وهمية بناءً على محتوى المطالبة
        lambda_val = self._calculate_lambda()
        if lambda_val > 0.75:
            response = f"أنا سعيد جدًا بردك! (Lambda: {lambda_val:.2f}) - الرسالة: {user_prompt}"
        elif lambda_val < 0.25:
            response = f"أنا أشعر ببعض التوتر بشأن هذا. (Lambda: {lambda_val:.2f}) - الرسالة: {user_prompt}"
        else:
            response = f"حسناً، هذا مثير للاهتمام. (Lambda: {lambda_val:.2f}) - الرسالة: {user_prompt}"
        
        return response, new_emotions

    def _load_training_data(self):
        """تحميل بيانات تدريب وهمية للنموذج الداخلي."""
        self.X_train = np.array([[0.5, 0.5, 0.5], [0.1, 0.9, 0.1], [0.9, 0.1, 0.9]])
        self.y_train = np.array([0, 1, 2]) # 0: neutral, 1: positive, 2: negative
        self.emotions_features = ['joy', 'fear', 'calm']

    def _train_internal_model(self):
        """تدريب نموذج التعلم الآلي الداخلي."""
        try:
             self.internal_llm_model = RandomForestClassifier(n_estimators=10)
             self.internal_llm_model.fit(self.X_train, self.y_train)
        except Exception as e:
             # في حالة وجود خطأ في تهيئة النموذج (نقص المكتبات أو غيرها)
             print(f"Error training internal model: {e}")
             self.internal_llm_model = None

    def _predict_and_update_state(self, user_prompt: str) -> Dict[str, float]:
        """يتنبأ بالحالة العاطفية من المطالبة وتحديث الحالة."""
        
        # خطوة 1: استخراج الميزات العاطفية من المطالبة (محاكاة)
        # في تطبيق حقيقي، سيتم استخدام LLM أو NLP لتحليل النص
        
        # محاكاة تأثير المشاعر على الحالة:
        current_features = np.array([
            self.state.get('joy', 0.5), 
            self.state.get('fear', 0.5), 
            self.state.get('calm', 0.5)
        ]).reshape(1, -1)
        
        if self.internal_llm_model:
             prediction = self.internal_llm_model.predict(current_features)[0]
        else:
             # العودة إلى العشوائية إذا فشل النموذج
             prediction = random.choice([0, 1, 2])
        
        # خطوة 2: تطبيق التحديثات
        update_magnitude = 0.15 # حجم التغيير
        new_emotions = self.state.copy()
        
        if prediction == 1: # إيجابي
            new_emotions['joy'] = min(1.0, new_emotions.get('joy', 0) + update_magnitude)
            new_emotions['fear'] = max(0.0, new_emotions.get('fear', 0) - update_magnitude)
        elif prediction == 2: # سلبي
            new_emotions['fear'] = min(1.0, new_emotions.get('fear', 0) + update_magnitude)
            new_emotions['joy'] = max(0.0, new_emotions.get('joy', 0) - update_magnitude)
        
        # خطوة 3: تحديث الحالة وحفظها
        self.state.update(new_emotions)
        self.state_manager.save_state(new_emotions) # حفظ الحالة في SQLite
        
        return new_emotions

    def _generate_llm_response(self, user_prompt: str) -> Tuple[str, Dict[str, float]]:
        """يستخدم Gemini API لتوليد الاستجابة."""
        
        # 1. تحديث الحالة
        updated_state = self._predict_and_update_state(user_prompt)
        lambda_val = self._calculate_lambda()
        
        # 2. بناء المطالبة باستخدام الحالة الحالية
        system_prompt = PromptBuilder.build_system_prompt(self.state, lambda_val)
        
        # 3. استدعاء API
        try:
            client = self.llm_client
            
            # هنا يجب استخدام النموذج الذي تم تحديده في التهيئة
            model_name = self.internal_llm_model if self.internal_llm_model else 'gemini-2.5-flash'
            
            response = client.generate_content(
                 model=model_name,
                 contents=[user_prompt],
                 system_instruction=system_prompt
            )
            
            response_text = response.text
            
        except Exception as e:
            response_text = f"عذرًا، فشل الاتصال بخدمة Gemini API: {str(e)}"
            print(f"Gemini API Error: {e}")
            
        return response_text, updated_state


    def process_message(self, user_prompt: str) -> Tuple[str, Dict[str, float]]:
        """الواجهة العامة لمعالجة رسالة المستخدم."""
        
        if self.is_simulated:
             return self._generate_simulated_response(user_prompt)
        else:
             return self._generate_llm_response(user_prompt)

    def get_current_state(self) -> Dict[str, float]:
        """يعيد الحالة العاطفية الحالية."""
        return self.state
