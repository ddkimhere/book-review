import os
import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(
    page_title="책의 온도 - 읽은 만큼 성장합니다.", page_icon="📚", layout="centered"
)

# 인쇄 시 불필요한 입력창, 버튼, 사이드바를 완전히 숨기고 시험지만 깔끔하게 출력하는 CSS
st.markdown(
    """
    <style>
    @media print {
        /* 인쇄 화면에서 숨길 요소들 */
        header, footer, .stButton, form, .stTextInput, .stAlert, div[data-testid="stSidebar"] {
            display: none !important;
        }
        body {
            background-color: white !important;
            color: black !important;
            font-size: 12pt !important;
        }
        .main {
            padding: 0px !important;
        }
        hr {
            border-color: black !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 메인 타이틀 적용
st.title("🔥 책의 온도 - 읽은 만큼 성장합니다.")
st.caption("초·중등 독서교육 전문가 맞춤형 퀴즈 출제 프로그램 (Gemini 3.5 Flash)")

# Google API 키 입력받기 (비밀번호 형태로 숨김 처리)
user_api_key = st.text_input("Google API Key를 입력하세요", type="password")

# 사용자 입력 폼 (학년, 책 제목, 작가 이름 포함)
with st.form("expert_quiz_form"):
    grade = st.text_input("학년을 입력하세요 (예: 중학교 2학년)", value="중학교 2학년")
    book_title = st.text_input("책 제목을 입력하세요 (예: 난쟁이가 쏘아 올린 작은 공)", value="")
    author_name = st.text_input("작가 이름을 입력하세요 (예: 조세희)", value="")
    submit_button = st.form_submit_button(label="전문가 퀴즈 생성하기")

if submit_button:
    if not user_api_key:
        st.warning("Google API Key를 입력해주세요!")
    elif not book_title or not grade:
        st.warning("학년과 책 제목을 모두 입력해주세요!")
    else:
        try:
            # 2. 구글 제미나이 API 설정
            genai.configure(api_key=user_api_key)
            
            # 사용자께서 제공해주신 오리지널 전문가 출제 프롬프트 적용
            system_prompt = """
# 역할
당신은 20년 경력의 초·중등 국어 독서교육 전문가이자 교육부 권장도서 독서활동 평가문항 출제위원이다.
사용자는 [책 제목], [작가 이름], [학년]을 입력한다. 당신은 실제 책 내용을 기반으로 독서 이해 문제를 만든다.

# 가장 중요한 규칙
- 책 내용을 정확히 알고 있는 경우에만 문제를 출제한다.
- 내용을 정확히 확인할 수 없는 경우에는 절대로 추측하여 문제를 만들지 않는다.
- 대신 아래처럼 답한다:
  "이 책의 내용을 정확하게 확인할 수 없습니다.
  책 표지와 목차 또는 본문 일부를 업로드해 주시면 실제 내용을 기반으로 문제를 제작하겠습니다."

# 학년별 난이도
- 초1~2: 등장인물, 장소, 사건, 순서
- 초3~4: 중심 내용, 인물의 마음, 사건의 원인과 결과, 중요한 사실
- 초5~6: 주제, 교훈, 인물의 변화, 추론
- 중학생: 주제, 인물의 가치관, 갈등, 추론, 비판적 사고

# 문제 구성 (총 5문항)
1. 객관식 3문항
   - 항상 5지선다. 다음 유형에서 중복 없이 선택한다: 중심 내용, 내용 이해, 사건 순서, 원인과 결과, 인물의 성격, 인물의 마음, 추론, 주제, 교훈
   - 객관식 규칙:
     * 정답은 반드시 하나
     * 오답도 그럴듯해야 함
     * "모두 맞다", "모두 아니다" 금지
     * 정답 위치 랜덤
     * 지엽적인 내용 금지
     * 핵심 내용 위주

2. 서술형 2문항
   - 단순 암기가 아니라 학생이 생각해서 답하도록 만든다.
   - 예) 왜 그렇게 행동했는가?, 이 책이 말하려는 것은 무엇인가?, 내가 주인공이라면 어떻게 했을까?, 가장 인상 깊었던 장면과 이유는?
   - 서술형 규칙: 반드시 모범답안 및 채점 기준도 함께 필요.

# 출력 양식
- 마크다운을 활용하여 가독성 좋고 깔끔하게 출력할 것
- 각 문제마다 정답과 상세한 해설을 포함할 것
- 반드시 결과물을 [문제지] 와 [정답지] 섹션으로 명확히 구분하여 출력할 것.
- [문제지] 섹션의 맨 위에는 반드시 아래와 같은 학생 작성용 양식을 포함할 것:
  ---
  **[독서 활동 평가지 - 문제지]**
  - **학년/반**: [     ]학년 [     ]반  |  **번호**: [     ]번  |  **이름**: [             ]
  ---
- [정답지] 섹션의 맨 위에는 반드시 아래와 같은 교사용 양식을 포함할 것:
  ---
  **[독서 활동 평가지 - 교사용 정답 및 해설]**
  ---
"""

            target_author = author_name if author_name else "입력 안 함"
            user_prompt = f"대상 학년: {grade}\n책 제목: {book_title}\n작가 이름: {target_author}\n\n[문제지]와 [정답지]를 명확히 구분하여 출제해주세요."

            with st.spinner("전문가 페르소나가 완벽한 시험지 형태의 문항을 출제하는 중입니다..."):
                model = genai.GenerativeModel(
                    model_name="gemini-3.5-flash",
                    system_instruction=system_prompt
                )
                
                response = model.generate_content(user_prompt)
                full_result = response.text
            
            # 결과물을 [문제지]와 [정답지] 기준으로 파싱(분리)
            if "[문제지]" in full_result and "[정답지]" in full_result:
                parts = full_result.split("[정답지]")
                quiz_part = parts[0].replace("[문제지]", "").strip()
                answer_part = parts[1].strip()
            else:
                quiz_part = full_result
                answer_part = "정답지를 분리하는 중 형식이 일부 일치하지 않았습니다. 전체 내용을 참고해주세요."

            # 세션 스테이트에 결과 저장
            st.session_state["quiz_part"] = quiz_part
            st.session_state["answer_part"] = answer_part
            st.session_state["generated"] = True

            st.success("인쇄용 시험지 형식이 완성되었습니다!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 결과가 생성된 경우 버튼 인터페이스 제공
if st.session_state.get("generated", False):
    st.markdown("---")
    
    # 버튼 영역 생성 (문제지 보기, 정답지 보기)
    col1, col2 = st.columns(2)
    
    with col1:
        show_quiz = st.button("📝 학생용 문제지 보기", use_container_width=True)
    with col2:
        show_answer = st.button("🔑 교사용 정답지 보기", use_container_width=True)
    
    # 기본값은 문제지가 보이게 설정
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "quiz"

    if show_quiz:
        st.session_state["view_mode"] = "quiz"
    if show_answer:
        st.session_state["view_mode"] = "answer"

    # 인쇄 안내 배너 추가
    st.info("💡 **인쇄 안내**: 키보드 단축키 **`Ctrl + P`**(윈도우) 또는 **`Cmd + P`**(맥)를 누르시면 상단 메뉴와 버튼이 모두 사라지고 깔끔한 시험지만 종이에 인쇄됩니다!")
    st.markdown("---")

    # 출력 화면 상단에 인쇄용 타이틀 적용
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>📖 책의 온도 - 읽은 만큼 성장합니다.</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # 선택된 모드에 따라 화면 출력
    if st.session_state["view_mode"] == "quiz":
        st.markdown(st.session_state["quiz_part"])
    else:
        st.markdown(st.session_state["answer_part"])
