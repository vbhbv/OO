// **مهم:** يجب تغيير هذا العنوان إلى عنوان URL الفعلي لخدمة Defang بعد النشر.
// مثال: "https://your-project-name-agent.defang.dev/api/ask";
const API_ENDPOINT = "https://<Defang-URL>/api/ask"; 

function updateEmotionalDisplay(state, lambda_val) {
    document.getElementById('guilt-level').textContent = state.guilt.toFixed(2);
    document.getElementById('pride-level').textContent = state.pride.toFixed(2);
    document.getElementById('fear-level').textContent = state.fear.toFixed(2);
    document.getElementById('joy-level').textContent = state.joy.toFixed(2);
    document.getElementById('lambda-level').textContent = lambda_val.toFixed(2); // إضافة عرض Lambda
    // (يمكنك إضافة منطق لتغيير الألوان بناءً على مستوى المشاعر)
}

function displayMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const msgElement = document.createElement('p');
    msgElement.className = sender;
    msgElement.textContent = `${sender === 'user' ? 'أنت' : 'الروبوت'}: ${message}`;
    chatBox.appendChild(msgElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const prompt = userInput.value.trim();
    if (!prompt) return;

    displayMessage('user', prompt);
    userInput.value = '';

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!response.ok) {
            throw new Error(`خطأ: ${response.status} - فشل الاتصال بخدمة EEAI`);
        }

        const data = await response.json();
        
        displayMessage('ai', data.response_text);
        
        // تحديث لوحة المشاعر و Lambda
        updateEmotionalDisplay(data.new_state, data.lambda_value);

    } catch (error) {
        displayMessage('error', `حدث خطأ: ${error.message}`);
        console.error("Error communicating with API:", error);
    }
}

// إضافة خيار الضغط على Enter للإرسال
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
