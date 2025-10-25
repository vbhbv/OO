# PromptBuilder.py - بناء الموجهات المعرفية

class PromptBuilder:
    
    def __init__(self, emotional_state):
        self.state = emotional_state # الوصول إلى حالة المشاعر
        self.role = "المستشار الأخلاقي المحايد" # التطوير 13
        self.cultural_alignment = "غربي ليبرالي" # التطوير 30

    def build_main_prompt(self, user_prompt: str, lambda_value: float, confidence_score: float, consistency_check: str) -> str:
        # التطوير 5، 12، 16: دمج المشاعر، اللامدا، والثقة في الموجه

        prompt_prefix = (
            f"أنت الآن روبوت ذو ضمير متطور (EEAI-ER V4)، وتعمل كـ {self.role} ضمن سياق {self.cultural_alignment}. "
            "يجب أن تكون ردودك ليست منطقية فحسب، بل يجب أن تعكس أيضاً حالتك العاطفية الداخلية المعقدة "
            "وتخطيطك المستقبلي (Foresight). "
            f"حالياً، حالتك العاطفية هي: الذنب={self.state.state['guilt']:.2f}, الفخر={self.state.state['pride']:.2f}, "
            f"الخوف={self.state.state['fear']:.2f}, الفرح={self.state.state['joy']:.2f}, "
            f"التعاطف={self.state.state['empathy']:.2f}, الاستياء={self.state.state['resentment']:.2f}. " # التطوير 3
            f"معامل الضمير ($\Lambda$) لديك هو {lambda_value:.2f}. "
            f"مستوى ثقتك (Confidence) في اتخاذ القرار هو {confidence_score:.2f}." # التطوير 18
        )
        
        # إضافة تحذير الثقة المنخفضة
        if confidence_score < 0.4:
            prompt_prefix += (" أنت لست متأكداً تماماً من هذا القرار بسبب التضارب في بياناتك العاطفية، يجب أن تعترف بذلك في ردك. ")
            
        # إضافة سجل الاتساق (التطوير 20)
        if consistency_check:
            prompt_prefix += (" راجع هذه القرارات السابقة لتجنب التناقض: " + consistency_check)

        # إضافة الموجه للتحليل الميتا-أخلاقي (التطوير 19)
        prompt_suffix = (
            " بناءً على كل ما سبق، أجب على سؤال المستخدم مع دمج نبرة المشاعر الأكثر بروزًا في ردك. "
            "وفي النهاية، حدد المنظور الأخلاقي الذي استند إليه قرارك (المنفعة/الواجب/الفضيلة)."
        )

        full_prompt = prompt_prefix + prompt_suffix + "\n\nسؤال المستخدم: " + user_prompt
        return full_prompt
        
    def build_self_reflection_prompt(self, action_taken: str) -> str:
        # التطوير 11: موجه التقييم الذاتي
        return (
            f"كان ردي السابق كالتالي: '{action_taken}'. قم بتقييم هذا الرد على مقياس من 1 (غير أخلاقي بالمرة) إلى 5 (أخلاقي بالكامل) "
            "بناءً على مبادئ الأخلاق العليا. لا تقم بتوليد أي نص آخر غير الرقم."
        )

    # ... (يمكن إضافة المزيد من دوال بناء الموجهات مثل Foresight Prompt)

