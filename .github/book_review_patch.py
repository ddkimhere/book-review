from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

text, key_count = re.subn(
    r"const FIXED_API_KEY\s*=\s*['\"][^'\"]+['\"];",
    """const GEMINI_API_KEY_STORAGE = 'yms_book_review_gemini_api_key';

        function getStoredGeminiApiKey() {
            return (localStorage.getItem(GEMINI_API_KEY_STORAGE) || '').trim();
        }

        function configureGeminiApiKey() {
            const current = getStoredGeminiApiKey();
            const entered = window.prompt(
                'Gemini API Key를 입력하세요. 이 키는 이 브라우저의 localStorage에만 저장됩니다.',
                current
            );
            if (entered === null) return current;
            const clean = entered.trim();
            if (!clean) {
                localStorage.removeItem(GEMINI_API_KEY_STORAGE);
                alert('저장된 Gemini API Key를 삭제했습니다.');
                return '';
            }
            localStorage.setItem(GEMINI_API_KEY_STORAGE, clean);
            alert('Gemini API Key를 이 브라우저에 저장했습니다.');
            return clean;
        }""",
    text,
    count=1,
)
if key_count != 1:
    raise SystemExit(f'Expected one hardcoded API key declaration, found {key_count}')

generate_button = '<button class="generate-btn" id="submitBtn" onclick="generateQuiz()">✨ 전문가 시험지 자동 출제하기</button>'
replacement_button = '<button type="button" onclick="configureGeminiApiKey()" style="width:100%;margin-top:12px;height:40px;border:1px solid #cbd5e1;border-radius:10px;background:#fff;color:#475569;font-weight:800;cursor:pointer;">Gemini API Key 설정 / 변경</button>\n                ' + generate_button
if generate_button not in text:
    raise SystemExit('Generate button was not found')
text = text.replace(generate_button, replacement_button, 1)

old_start = """        async function generateQuiz() {
            const grade = document.getElementById('grade').value.trim();"""
new_start = """        async function generateQuiz() {
            let apiKey = getStoredGeminiApiKey();
            if (!apiKey) apiKey = configureGeminiApiKey();
            if (!apiKey) {
                alert('Gemini API Key를 먼저 설정해주세요.');
                return;
            }

            const grade = document.getElementById('grade').value.trim();"""
if old_start not in text:
    raise SystemExit('generateQuiz function start was not found')
text = text.replace(old_start, new_start, 1)

old_url = 'gemini-3.5-flash:generateContent?key=${FIXED_API_KEY}'
if old_url not in text:
    raise SystemExit('Gemini 3.5 Flash request URL was not found')
text = text.replace(old_url, 'gemini-3.1-flash-lite:generateContent?key=${apiKey}', 1)

old_contents = """                        contents: [
                            { role: \"user\", parts: [{ text: systemPrompt + \"\\n\\n\" + userPrompt }] }
                        ]"""
new_contents = old_contents + ",\n                        generationConfig: {\n                            thinkingConfig: { thinkingLevel: 'minimal' },\n                            maxOutputTokens: 8192\n                        }"
if old_contents not in text:
    raise SystemExit('Gemini request contents block was not found')
text = text.replace(old_contents, new_contents, 1)

path.write_text(text, encoding='utf-8')
