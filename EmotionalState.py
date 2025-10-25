# EmotionalState.py - تخزين الحالة والذاكرة

import sqlite3
import json
import time

class EmotionalState:
    
    def __init__(self, db_path='emotions.db'):
        self.db_path = db_path
        self._initialize_db()
        self.state = self._load_state()
        
        # التطوير 23: تحيز المزاج (للتأثير على المشاعر)
        self.temperament_bias_guilt = self.state.get('temperament_bias_guilt', 1.2) 
        
        # التطوير 2: قيمة النضج (maturity)
        self.maturity = self.state.get('maturity', 1.0)
        
        # التطوير 14: سجل التجارب
        self.experience_log = self._load_log() 

    def _initialize_db(self):
        # التطوير 1: إنشاء قاعدة بيانات SQLite بسيطة لتخزين الحالة الدائمة
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول لتخزين الحالة (Guilt, Pride, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # جدول لتخزين سجل التجارب (الذاكرة)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER,
                data TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        # ضمان وجود حالة افتراضية عند الإنشاء لأول مرة
        initial_state = {
            'guilt': 0.1, 
            'pride': 0.2,
            'fear': 0.05, 
            'joy': 0.1,    
            'empathy': 0.5, 
            'resentment': 0.0, 
            'maturity': 1.0,
            'temperament_bias_guilt': 1.2
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إدخال القيم الافتراضية إذا لم تكن موجودة
        for key, value in initial_state.items():
            cursor.execute("SELECT key FROM state WHERE key=?", (key,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO state (key, value) VALUES (?, ?)", (key, str(value)))
                
        conn.commit()
        conn.close()

    def _load_state(self) -> dict:
        # تحميل الحالة العاطفية من قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM state")
        rows = cursor.fetchall()
        conn.close()
        
        state = {}
        for key, value_str in rows:
            # محاولة تحويل القيمة إلى float
            try:
                state[key] = float(value_str)
            except ValueError:
                state[key] = value_str # إذا لم يكن رقماً
                
        return state

    def save_state(self):
        # حفظ الحالة العاطفية الحالية في قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in self.state.items():
            # تحويل القيمة إلى نص قبل الحفظ
            value_str = str(value)
            cursor.execute(
                "REPLACE INTO state (key, value) VALUES (?, ?)", 
                (key, value_str)
            )
            
        conn.commit()
        conn.close()
        
    def _load_log(self) -> list:
        # تحميل سجل التجارب (آخر 100 سجل)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM log ORDER BY timestamp DESC LIMIT 100") 
        rows = cursor.fetchall()
        conn.close()
        
        log = []
        for row in rows:
            try:
                # البيانات مخزنة كـ JSON
                log.append(json.loads(row[0])) 
            except json.JSONDecodeError:
                continue
                
        return log[::-1] # عكس القائمة ليكون الأقدم أولاً

    def add_experience(self, experience: dict):
        # إضافة تجربة جديدة إلى السجل
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # حفظ البيانات كـ JSON
        data_json = json.dumps(experience)
        current_time = int(time.time())
        
        cursor.execute(
            "INSERT INTO log (timestamp, data) VALUES (?, ?)", 
            (current_time, data_json)
        )
        
        conn.commit()
        conn.close()
        
        # تحديث السجل في الذاكرة
        self.experience_log.append(experience)
        # الحفاظ على حجم السجل بحد أقصى 100
        if len(self.experience_log) > 100:
            self.experience_log.pop(0)
