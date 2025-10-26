# 1. المرحلة الأساسية: استخدام صورة بايثون رسمية كقاعدة
FROM python:3.10-slim

# 2. تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# 3. نسخ ملف التبعيات أولاً لتسريع عملية البناء (Caching)
COPY requirements.txt .

# 4. تثبيت المكتبات (TensorFlow, PyTorch, Scikit-learn, Flask, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. نسخ باقي كود المشروع إلى مجلد العمل
COPY . .

# 6. تعريض المنفذ الذي ستعمل عليه واجهة API للنموذج (مثلاً: 5000)
# تأكد من أن كودك (app.py) يعمل على هذا المنفذ
EXPOSE 5000

# 7. الأمر النهائي لتشغيل تطبيق الـ API الخاص بالنموذج
# استبدل 'app.py' باسم ملف تشغيل النموذج الخاص بك
CMD ["python", "app.py"] 
