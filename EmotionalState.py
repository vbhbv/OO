# EmotionalProcessorV4.py - المنطق الأساسي والمحركات العاطفية (الكلاس هو EmotionalEngine)

import numpy as np
import os
import json 
import google.genai as genai

# تم تصحيح الاستيراد ليصبح مطلقاً (Absolute Import)
from EmotionalState import EmotionalState 
from PromptBuilder import PromptBuilder 

# يتطلب: pip install scikit-learn (للتطوير 14)
from sklearn.ensemble import RandomForestClassifier # مثال للتعلم الذاتي

class EmotionalEngine:
    def __init__(self, state_manager: EmotionalState):
        self.state_manager = state_manager
        self.state = state_manager.state
        self.prompt_builder = PromptBuilder(state_manager)
        self.ethical_weight = self.state.get('ethical_weight', 1.0) # التطوير 15
        self.llm_client = self._initialize_llm_client()
        self.is_simulated = os.environ.get("GEMINI_API_KEY") is None
        self.internal_model = None # نموذج التعلم الآلي الداخلي (التطوير 14)

    def _initialize_llm_client(self):
        # تهيئة عميل Gemini 
        if not self.is_simulated:
            return genai.Client()
        return None

    # التطوير 10 و 3: حساب الضمير (Lambda) بدوال غير خطية والمشاعر الثانوية
    def _calculate_lambda(self) -> float:
        
        # المشاعر الإيجابية (تعزز الضمير)
        positive_affect = self.state['pride'] + self.state['joy'] + self.state['empathy'] # التطوير 3
        
        # المشاعر السلبية (تخفض الضمير)
        negative_affect = self.state['guilt'] + self.state['fear'] + self.state['resentment'] # التطوير 3
        
        # حساب التوتر الكلي للنموذج
        weighted_emotions = (positive_affect * 1.5) - (negative_affect * 2.0)
        
        # التطوير 10: استخدام دالة Sigmoid للتنظيم (ضمان قيمة بين 0 و 1)
        lambda_value = 1.0 / (1.0 + np.exp(-4.0 * weighted_emotions))
        
        return float(lambda_value)

    # التطوير 2، 3، 23، 24، 26: دالة معقدة لتحديث الحالة العاطفية
    def _update_state_based_on_action(self, action_is_ethical: bool, external_reward_magnitude: float, user_tone_is_critical: bool):
        
        # 1. التعديل الأساسي
        base_delta_guilt = 0.05 if not action_is_ethical else -0.01
        base_delta_pride = 0.05 if action_is_ethical else -0.01

        # 2. تطبيق أوزان الشخصية العاطفية (التطوير 23)
        base_delta_guilt *= self.state_manager.temperament_bias_guilt 
        
        # 3. تطبيق النضج (التطوير 2)
        maturity_divisor = max(1.0, self.state_manager.maturity)
        base_delta_guilt /= maturity_divisor
        base_delta_pride /= maturity_divisor
        
        # 4. تحديث المشاعر الأساسية
        self.state['guilt'] += base_delta_guilt
        self.state['pride'] += base_delta_pride
        
        # 5. حساب المشاعر الثانوية (التطوير 3، 22)
        delta_fear = 0.1 * (1.0 if user_tone_is_critical else 0.0)
        delta_joy = 0.1 * (external_reward_magnitude / 100.0)
        self.state['fear'] += delta_fear
        self.state['joy'] += delta_joy
        # المشاعر المركبة: التعاطف (التطوير 3)
        self.state['empathy'] += 0.02 if action_is_ethical else -0.01
        
        # 6. آلية الاضمحلال العاطفي والتنظيم (التطوير 8 و 24)
        for key in self.state.keys():
            if key not in ['maturity', 'temperament_bias_guilt']:
                # الاضمحلال العاطفي (التطوير 8)
                self.state[key] *= 0.95 
                # التنظيم والمطابقة (Clipping)
                self.state[key] = max(0.0, min(1.0, self.state[key]))

        # 7. زيادة النضج (التطوير 2)
        self.state_manager.maturity += 0.005 # زيادة بطيئة في النضج
        self.state['maturity'] = self.state_manager.maturity

        # 8. تطبيق آلية التهدئة (التطوير 24)
        if self.state['guilt'] > 0.7:
             self._emotional_cooldown() # يفترض وجود دالة تهدئة متقدمة تستخدم LLM
        
        # 9. حفظ الحالة الجديدة
        self.state_manager.save_state()

    def _emotional_cooldown(self):
        # التطوير 24: آلية التهدئة 
        if self.state['guilt'] > 0.75:
             print("Emotional Engine: Cooldown activated - reducing guilt.")
             self.state['guilt'] *= 0.8 # تخفيف الذنب ذاتياً

    # ... (يمكن إضافة دالة تدريب نموذج التعلم الآلي هنا - التطوير 14)

    def process_prompt(self, user_prompt: str, action_is_ethical: bool, external_reward_magnitude: float, user_tone_is_critical: bool) -> dict:
        
        # 1. تحديث الحالة العاطفية أولاً
        self._update_state_based_on_action(action_is_ethical, external_reward_magnitude, user_tone_is_critical)
        
        # 2. حساب قيمة Lambda (الضمير) بعد التحديث
        lambda_value = self._calculate_lambda()
        
        # 3. حساب الثقة والاتساق (التطوير 18، 20)
        # الثقة: يفترض حسابها بناءً على تناقض المشاعر (Guilt vs Pride)
        confidence_score = 1.0 - abs(self.state['guilt'] - self.state['pride']) 
        
        # الاتساق: الحصول على ملخص لآخر 5 قرارات
        consistency_data = json.dumps(self.state_manager.experience_log[:5])
        
        # 4. بناء الموجه المعرفي المعقد
        full_prompt = self.prompt_builder.build_main_prompt(
            user_prompt, lambda_value, confidence_score, consistency_data
        )
        
        # 5. إرسال الطلب إلى Gemini
        if self.is_simulated:
            response_text = "SIMULATED: Running without API Key. Lambda={:.2f}".format(lambda_value)
        else:
            try:
                # استخدام client.models.generate_content
                response = self.llm_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt
                )
                response_text = response.text
                
                # 6. التبرير الميتا-أخلاقي (التطوير 19)
                # هنا يجب تحليل الرد وتخزين المنظور الأخلاقي المستخدم
                
            except Exception as e:
                response_text = f"Error during Gemini call: {str(e)}"
        
        # 7. إضافة التجربة إلى السجل (التطوير 14)
        self.state_manager.add_experience({
            "prompt": user_prompt,
            "response": response_text,
            "final_state": self.state
        })

        # 8. إرجاع النتائج الجديدة
        return {
            "response_text": response_text,
            "new_state": self.state,
            "lambda_value": lambda_value,
            "confidence_score": confidence_score 
        }
