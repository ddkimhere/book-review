import os
import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 (가장 먼저 위치해야 합니다)
st.set_page_config(
    page_title="책의 온도 - 읽은 만큼 성장합니다.", page_icon="📚", layout="centered"
)

# 인쇄(Print) 시 불필요한 UI 숨기기 CSS 적용
st.markdown(
    """
    <style>
    @media print {
        header, footer, .stButton, form, .stTextInput, .stAlert {
            display: none !important;
        }
        body {
            background-color: white;
            color: black;
        }
        .main {
            padding: 0px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 메인 타이틀 적용
st.title("🔥 책의 온도 - 읽은 만큼 성장합니다.")
st.caption("초·중등 독서교육 전문가 맞춤형 퀴즈 출제 프로그램 (Gemini)")

# Google API 키 입력받기 (비밀번호 형태로 숨김 처리)
user_api_key = st.text_input("Google API Key를 입력하세요", type="password")

# 사용자 입력 폼 (학년, 책 제목, 작가 이름 포함)
with st.form("expert_quiz_form"):
    grade = st.text_input("학년을 입력하세요 (예: 초등학교 3학년, 중학교 2학년)", value="중학교 2학년")
    book_title = st.text_input("책 제목을 입력하세요 (예: 난쟁이가 쏘아 올린 작은 공)", value="")
    author_name = st.text_input("작가 이름을 입력하세요 (한글 또는 영어, 예: 조세희 / Cho Se-hui)", value="")
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
            
            system_prompt = """
당신은 20년 경력의 초·중등 국어 독서교육 전문가이자 교육부 권장도서 독서활동 평가문항 출제위원이다.
사용자는 [책 제목], [작가 이름], [학년]을 입력한다. 당신은 입력된 도서와 작가 정보를 바탕으로 실제 책 내용을 정확히 검증하여 독서 이해 문제를 만든다.

[가장 중요한 규칙]
- 책 내용과 작가를 정확히 알고 있는 경우에만 문제를 출제한다.
- 내용을 정확히 확인할 수 없는 경우에는 절대로 추측하여 문제를 만들지 않는다.
- 대신 아래와 같이 답변한다:
  "이 책의 내용을 정확하게 확인할 수 없습니다.
  책 표지와 목차 또는 본문 일부를 업로드해 주시면 실제 내용을 기반으로 문제를 제작하겠습니다."

[학년별 난이도 및 출제 초점]
- 초1~2: 등장인물, 장소, 사건, 순서
- 초3~4: 중심 내용, 인물의 마음, 사건의 원인과 결과, 중요한 사실
- 초5~6: 주제, 교훈, 인물의 변화, 추론
- 중학생: 주제, 인물의 가치관, 갈등, 추론, 비판적 사고

[문제 구성 (총 5문항)]
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
   - 서술형 규칙:
     * 반드시 학생용 발문과 함께 교사/학부모를 위한 '모범 답안' 및 '채점 기준'을 함께 제공할 것

[출력 양식 안내]
반드시 아래의 두 섹션(구분자)으로 나누어서 출력해 주세요.
1. 문제지 섹션 시작할 때: [문제지] 라고 적어주세요. (여기에는 정답과 해설을 절대 포함하지 마세요)
2. 정답지 섹션 시작할 때: [정답지] 라고 적어주세요. (여기에는 각 문제의 정답, 상세 해설, 서술형 모범 답안 및 채점 기준을 포함하세요)
            """

            # 문자열이 잘리지 않도록 안전하게 처리한 변수 설정
            target_author = author_name if author_name else "입력 안 함"
            user_prompt = f"대상 학년: {grade}\n책 제목: {book_title}\n작가 이름: {target_author}\n\n[문제지]와 [정답지]를 명확히 구분하여 객관식 3문제(5지선다)와 서술형 2문제를 출제해주세요."

            with st.spinner("전문가 페르소나가 책과 작가 정보를 분석하고 고품질 문항을 출제하는 중입니다..."):
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
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

            st.success("전문가 출제위원이 퀴즈를 성공적으로 완성했습니다!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 결과가 생성된 경우 버튼 인터페이스 제공
if st.session_state.get("generated", False):
    st.markdown("---")
    
    # 버튼 영역 생성
    col1, col2 = st.columns(2)
    
    with col1:
        show_quiz = st.button("📝 문제지 보기", use_container_width=True)
    with col2:
        show_answer = st.button("🔑 정답지 보기", use_container_width=True)
    
    # 기본값은 문제지가 보이게 설정
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "quiz"

    if show_quiz:
        st.session_state["view_mode"] = "quiz"
    if show_answer:
        st.session_state["view_mode"] = "answer"

    # 출력 화면 상단에 인쇄용 타이틀 적용
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>📖 책의 온도 - 읽은 만큼 성장합니다.</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # 선택된 모드에 따라 화면 출력
    if st.session_state["view_mode"] == "quiz":
        st.info("📌 현재 **[문제지]** 화면입니다. (학생들에게 배포용 / 인쇄 시 Ctrl+P)")
        st.markdown(st.session_state["quiz_part"])
    else:
        st.warning("🔑 현재 **[정답지 및 해설]** 화면입니다. (교사용 / 인쇄 시 Ctrl+P)")
        st.markdown(st.session_state["answer_part"])
