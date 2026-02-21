const API_URL = "http://127.0.0.1:8000/predict";

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('checkForm');
    if (!form) return;

    const urlInput = document.getElementById('urlInput');
    const resultBox = document.getElementById('result');
    const loader = document.getElementById('loader');
    
    const btn = document.getElementById('submitBtn'); 

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        resultBox.style.display = 'none';
        loader.style.display = 'block';
        
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Проверка...';
        }

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) throw new Error('Ошибка соединения с сервером');
            
            const data = await response.json();
            showResult(data);

        } catch (err) {
            alert('Ошибка: Не удалось связаться с сервером. Убедитесь, что FastAPI запущен.');
            console.error(err);
        } finally {
            loader.style.display = 'none';
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Проверить';
            }
        }
    });

    function showResult(data) {
        const title = document.getElementById('resTitle');
        const text = document.getElementById('resText');
        const prob = document.getElementById('resProb');

        resultBox.style.display = 'block';
        
        resultBox.classList.remove('bg-safe', 'bg-danger');
        resultBox.classList.add(data.is_phishing ? 'bg-danger' : 'bg-safe');

        if (data.is_phishing) {
            title.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> ОПАСНО';
            text.textContent = 'Эта ссылка похожа на фишинговую.';
            if (data.rule_based) {
                text.textContent += ' (Обнаружено правилом: @ в URL)';
            }
        } else {
            title.innerHTML = '<i class="bi bi-check-circle-fill"></i> БЕЗОПАСНО';
            text.textContent = 'Угрозы не обнаружены.';
        }
        
        prob.textContent = `Вероятность угрозы: ${(data.probability * 100).toFixed(1)}%`;
    }
});