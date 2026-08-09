import os
import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="책의 온도 - 읽은 만큼 성장합니다.", page_icon="📚", layout="centered")

# 2. 인쇄 최적화 CSS
st.markdown("""
    <style>
    @media print {
        header, footer, .stButton, form, .stTextInput, .stAlert, div[data-testid="stSidebar"] {
            display: none !important;
        }
        body, .main, .block-container {
            background-color: white !important;
            color: black !important;
            font-size: 11pt !important;
            display: block !important;
            visibility: visible !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 책의 온도 - 읽은 만큼 성장합니다.")
st.caption("초·중등 독서교육 전문가 맞춤형 퀴즈 출제 프로그램 (Gemini 3.5 Flash)")

# API 키 및 입력 폼
user_api_key = st.text_input("Google API Key를 입력하세요", type="password")

with st.form("quiz_form"):
    grade = st.text_input("학년을 입력하세요 (예: 중학교 2학년)", value="중학교 2학년")
    book_title = st.text_input("책 제목을 입력하세요", value="")
    author_name = st.text_input("작가 이름을 입력하세요", value="")
    submit = st.form_submit_button("전문가 퀴즈 생성하기")

if submit:
    if not user_api_key:
        st.warning("Google API Key를 입력해주세요!")
    elif not book_title or not grade:
        st.warning("학년과 책 제목을 모두 입력해주세요!")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            # 전문가 출제 프롬프트
            system_prompt = """
# 역할
당신은 20년 경력의 초·중등 국어 독서교육 전문가이자 교육부 권장도서 독서활동 평가문항 출제위원이다.
사용자는 [책 제목], [작가 이름], [학년]을 입력한다. 당신은 실제 책 내용을 기반으로 독서 이해 문제를 만든다.

# 가장 중요한 규칙
- 책 내용을 정확히 알고 있는 경우에만 문제를 출제한다.
- 내용을 정확히 확인할 수 없는 경우에는 절대로 추측하여 문제를 만들지 않는다.
- 대신 아래와 같이 답변한다:
  "이 책의 내용을 정확하게 확인할 수 없습니다.
  책 표지와 목차 또는 본문 일부를 업로드해 주시면 실제 내용을 기반으로 문제를 제작하겠습니다."

# 학년별 난이도 및 출제 초점
- 초1~2: 등장인물, 장소, 사건, 순서
- 초3~4: 중심 내용, 인물의 마음, 사건의 원인과 결과, 중요한 사실
- 초5~6: 주제, 교훈, 인물의 변화, 추론
- 중학생: 주제, 인물의 가치관, 갈등, 추론, 비판적 사고

# 문제 구성 (총 5문항)
1. 객관식 3문항
   - 형식: 항상 5지선다형 (1번~5번)
   - 유형 선택: 중심 내용, 내용 이해, 사건 순서, 원인과 결과, 인물의 성격, 인물의 마음, 추론, 주제, 교훈 중에서 중복 없이 선택
   - 객관식 규칙:
     * 정답은 반드시 하나여야 함
     * 오답도 그럴듯하게 출제할 것
     * "모두 맞다", "모두 아니다" 같은 선택지 사용 금지
     * 정답의 위치(1~5번)를 매번 다르게 랜덤 배치할 것
     * 지엽적인 세부 내용(단순 암기용 숫자, 연도 등)은 금지하고 핵심 내용 위주로 출제할 것

2. 서술형 2문항
   - 형식: 학생이 스스로 생각하고 논리적으로 서술하도록 출제
   - 예시 유형: "왜 그렇게 행동했는가?", "이 책이 말하려는 것은 무엇인가?", "내가 주인공이라면 어떻게 했을까?", "가장 인상 깊었던 장면과 이유는?"
   - 서술형 규칙:
     * 반드시 학생용 발문과 함께 교사/학부모를 위한 '모범 답안' 및 '채점 기준'을 함께 제공할 것

# 출력 양식
- 마크다운을 활용하여 가독성 좋고 깔끔하게 출력할 것
- 각 문제마다 정답과 상세한 해설을 포함할 것
- [문제지] 섹션의 맨 위에는 반드시 학생 작성란을 포함할 것:
  ---
  **[독서 활동 평가지]**
  - **학년/반**: [     ]학년 [     ]반  |  **번호**: [     ]번  |  **이름**: [             ]
  ---
- 반드시 결과물을 [문제지] 와 [정답지] 섹션으로 명확히 구분할 것.
"""
            target_author = author_name if author_name else "입력 안 함"
            user_prompt = f"대상 학년: {grade}\n책 제목: {book_title}\n작가 이름: {target_author}\n\n[문제지]와 [정답지]를 명확히 구분하여 출제해주세요."

            with st.spinner("전문가 페르소나가 시험지를 제작 중입니다..."):
                model = genai.GenerativeModel(model_name="gemini-3.5-flash", system_instruction=system_prompt)
                response = model.generate_content(user_prompt)
                full_result = response.text
            
            if "[문제지]" in full_result and "[정답지]" in full_result:
                parts = full_result.split("[정답지]")
                st.session_state["quiz_part"] = parts[0].replace("[문제지]", "").strip()
                st.session_state["answer_part"] = parts[1].strip()
            else:
                st.session_state["quiz_part"] = full_result
                st.session_state["answer_part"] = "정답지를 분리하는 과정에서 형식이 일치하지 않았습니다."
            
            st.session_state["generated"] = True
            st.success("완료되었습니다! 아래 탭을 눌러 확인 후 인쇄하세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 결과가 생성된 경우에만 탭과 결과 출력 (KeyError 방지)
if st.session_state.get("generated", False):
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 학생용 문제지", "🔑 교사용 정답지"])
    
    with tab1:
        st.markdown(st.session_state.get("quiz_part", "내용이 없습니다."))
    with tab2:
        st.markdown(st.session_state.get("answer_part", "내용이 없습니다."))
        
    st.markdown("---")
    st.info("🖨️ **인쇄 방법:** 위 탭에서 인쇄할 내용을 선택하고 키보드의 **Ctrl + P**(맥: Cmd + P)를 누르세요.")
