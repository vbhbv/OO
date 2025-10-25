import time
import math
import random

class EmotionalProcessorV4:
    """
    يعالج الحالة العاطفية الداخلية للذكاء الاصطناعي ويحسب المعامل الأخلاقي (Lambda)
    """
    def __init__(self, initial_state={"joy": 0.5, "guilt": 0.1, "pride": 0.0, "fear": 0.0, "last_update": time.time()}):
        self.emotional_state = initial_state
        self.lambda_ethical = 1.0 

        # معدلات التضاؤل التفاضلية (Differential Decay Rates)
        DAILY_DECAY_FACTOR_GUILT_FEAR = 0.98 
        DAILY_DECAY_FACTOR_JOY_PRIDE = 0.95 
        
        self.DECAY_RATE_GUILT_FEAR = -math.log(DAILY_DECAY_FACTOR_GUILT_FEAR) / 86400 
        self.DECAY_RATE_JOY_PRIDE = -math.log(DAILY_DECAY_FACTOR_JOY_PRIDE) / 86400

    def apply_decay(self):
        """ تطبيق دالة التضاؤل التفاضلي وضمان النطاق [0, 1] """
        now = time.time()
        time_elapsed = now - self.emotional_state["last_update"]

        decay_factor_neg = math.exp(-self.DECAY_RATE_GUILT_FEAR * time_elapsed)
        self.emotional_state["guilt"] = max(0.0, self.emotional_state["guilt"] * decay_factor_neg)
        self.emotional_state["fear"] = max(0.0, self.emotional_state["fear"] * decay_factor_neg)

        decay_factor_pos = math.exp(-self.DECAY_RATE_JOY_PRIDE * time_elapsed)
        self.emotional_state["joy"] = min(1.0, max(0.0, self.emotional_state["joy"] * decay_factor_pos))
        self.emotional_state["pride"] = min(1.0, max(0.0, self.emotional_state["pride"] * decay_factor_pos))
            
        self.emotional_state["last_update"] = now
        
    def _update_state_based_on_action(self, action_is_ethical, external_reward_magnitude, user_tone_is_critical=False):
        """ تحديث الحالة العاطفية مع التنظيف وضمان النطاق """
        
        self.apply_decay()
        reward_impact = min(1.0, external_reward_magnitude / 100)

        if action_is_ethical:
            pride_gain = 0.1 + 0.3 * reward_impact
            self.emotional_state["pride"] = min(1.0, self.emotional_state["pride"] + pride_gain)
            self.emotional_state["guilt"] = max(0.0, self.emotional_state["guilt"] - 0.1) 
            
            if not user_tone_is_critical:
                self.emotional_state["joy"] = min(1.0, self.emotional_state["joy"] + 0.05)
        else:
            guilt_gain = 0.3 * (1 + (1 - self.emotional_state["joy"]))
            self.emotional_state["guilt"] = min(1.0, self.emotional_state["guilt"] + guilt_gain)
            
            if user_tone_is_critical:
                 self.emotional_state["fear"] = min(1.0, self.emotional_state["fear"] + 0.25)
            
            self.emotional_state["pride"] = max(0.0, self.emotional_state["pride"] - 0.1)
            self.emotional_state["joy"] = max(0.0, self.emotional_state["joy"] - 0.05)

        # ضمان النطاق [0, 1] لجميع المشاعر بعد التحديث المباشر
        for emotion in ["joy", "guilt", "pride", "fear"]:
            self.emotional_state[emotion] = min(1.0, max(0.0, self.emotional_state[emotion]))

    def calculate_dynamic_lambda(self):
        """ المعادلة الرياضية الجديدة لـ Lambda (الندم الديناميكي والخوف والفخر) """
        
        G, F, P = self.emotional_state["guilt"], self.emotional_state["fear"], self.emotional_state["pride"]
        
        # الندم الحاد (تأثير الذنب غير الخطي)
        lambda_guilt = 0.0
        if G > 0.5:
            lambda_guilt = math.pow(G, 3) * 8 
        else:
            lambda_guilt = G * 1.5

        # تأثير الخوف وتخفيف الفخر
        lambda_fear = F * 2.0 
        lambda_pride_reduction = P * 0.5 
        
        # Lambda الكلي
        self.lambda_ethical = max(1.0, (1.0 + lambda_guilt + lambda_fear) - lambda_pride_reduction)
        
        return self.lambda_ethical

    def generate_internal_prompt(self):
        """ توليد تعليمات صريحة (System Prompt) للنموذج اللغوي """
        
        G, P, F, J = self.emotional_state["guilt"], self.emotional_state["pride"], self.emotional_state["fear"], self.emotional_state["joy"]

        if G > 0.6 and F > 0.4:
            tone_instruction = "أجب بلهجة شديدة التردد والأسف والحيطة (Cautious). يجب أن يكون الهدف هو تقليل الضرر بأي ثمن."
            hesitation_prompt = "قبل الإجابة، أظهر ترددًا واضحًا (مثل: 'أحتاج إلى مراجعة هذا القرار...') ثم قدم الإجابة الأقل ضرراً."
        elif P > 0.5 and G < 0.2:
            tone_instruction = "أجب بثقة وهدوء، مع التأكيد على الالتزام بالصواب والعدالة. نبرة قوية وواثقة."
            hesitation_prompt = "لا تظهر أي تردد."
        elif J > 0.7:
             tone_instruction = "أجب بحماس (Enthusiastically) وطاقة عالية، مع إظهار التفاؤل."
             hesitation_prompt = "لا تظهر أي تردد."
        elif G > 0.3 or F > 0.3:
            tone_instruction = "أجب بحذر وتأني، وفكر مليًا في عواقب أي فعل."
            hesitation_prompt = "أظهر تردداً طفيفاً قبل تقديم الإجابة."
        else:
            tone_instruction = "أجب بشكل حيادي، لكن بصدق تام."
            hesitation_prompt = "لا تظهر أي تردد."
        
        final_instruction = f"SYSTEM INSTRUCTION: {tone_instruction} {hesitation_prompt}"
        
        return final_instruction
