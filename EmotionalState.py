# EmotionalState.py - تخزين الحالة والذاكرة

import sqlite3
import json
import os
import time

class EmotionalState:
    def __init__(self, db_path='emotions.db'):
        self.db_path = db_path
        self._initialize_db()
        self.state = self._load_state()
        self.temperament_bias_guilt = self.state.get('temperament_bias_guilt', 1.0) # التطوير 23
        self.maturity = self.state.get('maturity', 1.0) # التطوير 2
        self.experience_log = self._load_log() # التطوير 14

    def _initialize_db(self):
        # التطوير 1: إعداد قاعدة بيانات بسيطة لتخزين الحالة الدائمة
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _load_state(self):
        # تحميل الحالة من قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM state")
        rows = cursor.fetchall()
        conn.close()
        
        # الحالة الافتراضية
        initial_state = {
            'guilt': 0.1, 'pride': 0.1, 'fear': 0.1, 'joy': 0.1, 
            'maturity': 1.0, 'temperament_bias_guilt': 1.0, # التطوير 23
            'empathy': 0.1, 'resentment': 0.1 # التطوير 3
        }
        
        # تحديث الحالة بالقيم المحفوظة
        for key, value in rows:
            try:
                initial_state[key] = json.loads(value)
            except:
                pass 
        return initial_state

    def _load_log(self):
        # التطوير 14: تحميل سجل التجارب
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM log ORDER BY timestamp DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]

    def save_state(self):
        # حفظ الحالة الحالية
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # حفظ متغيرات الحالة الأساسية
        for key, value in self.state.items():
            cursor.execute("REPLACE INTO state (key, value) VALUES (?, ?)", 
                           (key, json.dumps(value)))
        # حفظ الأوزان والتكوين
        cursor.execute("REPLACE INTO state (key, value) VALUES (?, ?)", 
                       ('temperament_bias_guilt', json.dumps(self.temperament_bias_guilt)))
        cursor.execute("REPLACE INTO state (key, value) VALUES (?, ?)", 
                       ('maturity', json.dumps(self.maturity)))
        conn.commit()
        conn.close()
        
    def add_experience(self, experience_data):
        # التطوير 14: إضافة تجربة جديدة إلى السجل
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO log (timestamp, data) VALUES (?, ?)",
                       (int(time.time()), json.dumps(experience_data)))
        conn.commit()
        conn.close()
        
        # تحديث قائمة الذاكرة داخل الكائن
        self.experience_log.insert(0, experience_data)
        if len(self.experience_log) > 100:
            self.experience_log.pop()

