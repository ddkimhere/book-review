import os
import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="책의 온도 - 읽은 만큼 성장합니다.", page_icon="📚", layout="centered")

# 인쇄 최적화 CSS (버튼, 입력창 숨김)
st.markdown("""
    <style>
    @media print {
        header, footer, .stButton, form, .stTextInput, .stAlert, div[data-testid="stSidebar"] {
            display: none !important;
        }
        body { background-color: white !important; color: black !important; font-size: 11pt !important; }
        .main { padding: 0px !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 책의 온도 - 읽은 만큼 성장합니다.")
st.caption("초·중등 독서교육 전문가 맞춤형 퀴즈 출제 프로그램 (Gemini 3.5 Flash)")

user_api_key = st.text_input("Google API Key를 입력하세요", type="password")

with st.form("expert_quiz_form"):
    grade = st.text_input("학년을 입력하세요", value="중학교 2학년")
    book_title = st.text_input("책 제목을 입력하세요", value="")
    author_name = st.text_input("작가 이름을 입력하세요", value="")
    submit_button = st.form_submit_button(label="전문가 퀴즈 생성하기")

if submit_button:
    if not user_api_key:
        st.warning("Google API Key를 입력해주세요!")
    elif not book_title or not grade:
        st.warning("학년과 책 제목을 모두 입력해주세요!")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            # 선생님께서 제공해주신 오리지널 프롬프트 이식
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
     * 정답의 위치(1번~5번)를 매번 다르게 랜덤 배치할 것
     * 지엽적인 세부 내용(단순 암기용 숫자, 연도 등)은 금지하고 핵심 내용 위주로 출제할 것

2. 서술형 2문항
   - 형식: 학생이 스스로 생각하고 논리적으로 서술하도록 출제
   - 예시 유형: "왜 그렇게 행동했는가?", "이 책이 말하려는 것은 무엇인가?", "내가 주인공이라면 어떻게 했을까?", "가장 인상 깊었던 장면과 이유는?"
   - 서술형 규칙:
     * 반드시 학생용 발문과 함께 교사/학부모를 위한 '모범 답안' 및 '채점 기준'을 함께 제공할 것

# 출력 양식
- 마크다운을 활용하여 가독성 좋고 깔끔하게 출력할 것
- 각 문제마다 정답과 상세한 해설을 포함할 것
- [문제지] 섹션 맨 위에 반드시 학생 작성란을 포함할 것:
  ---
  **[독서 활동 평가지]**
  - **학년/반**: [     ]학년 [     ]반  |  **번호**: [     ]번  |  **이름**: [             ]
  ---
- 반드시 결과물을 [문제지] 와 [정답지] 섹션으로 명확히 구분할 것.
"""

            user_prompt = f"대상 학년: {grade}\n책 제목: {book_title}\n작가 이름: {author_name}\n\n[문제지]와 [정답지]를 명확히 구분하여 시험지 양식으로 출제해주세요."

            with st.spinner("전문가 페르소나가 문항을 출제 중입니다..."):
                model = genai.GenerativeModel(model_name="gemini-3.5-flash", system_instruction=system_prompt)
                response = model.generate_content(user_prompt)
                full_result = response.text
            
            if "[문제지]" in full_result and "[정답지]" in full_result:
                parts = full_result.split("[정답지]")
                st.session_state["quiz_part"] = parts[0].replace("[문제지]", "").strip()
                st.session_state["answer_part"] = parts[1].strip()
            st.session_state["generated"] = True
            st.success("시험지 형식이 완성되었습니다!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

if st.session_state.get("generated", False):
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.button("📝 학생용 문제지", on_click=lambda: st.session_state.update(view="quiz"))
    with col2: st.button("🔑 교사용 정답지", on_click=lambda: st.session_state.update(view="answer"))
    with col3: st.button("🖨️ 인쇄 (Ctrl+P)", on_click=lambda: st.components.v1.html("<script>window.print();</script>", height=0))
    
    view = st.session_state.get("view", "quiz")
    if view == "quiz":
        st.markdown(st.session_state["quiz_part"])
    else:
        st.markdown(st.session_state["answer_part"])
