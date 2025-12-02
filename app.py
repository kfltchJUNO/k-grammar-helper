import streamlit as st
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 수업 도우미", page_icon="🏫")
st.title("🏫 우리 반 한국어 수업 도우미")

# =========================================================
# 👇 [설정 1] GitHub에 올린 교재 파일 이름 (정확히 일치해야 함!)
PDF_FILE_NAME = "단국한국어 1가_압축.pdf", "단국한국어 1-나_압축.pdf" 
# =========================================================

# 2. API 키 설정 (Secrets에서 가져옴)
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"API 키 설정 오류: {e}")
        st.stop()
else:
    st.error("🚨 API 키가 없습니다. Streamlit 설정을 확인해주세요.")
    st.stop()

# 3. 모델 및 파일 로딩 (캐싱 적용)
@st.cache_resource
def load_ai_model():
    if not os.path.exists(PDF_FILE_NAME):
        return None, None, f"파일을 찾을 수 없습니다: {PDF_FILE_NAME}"
    
    try:
        # 파일 업로드
        uploaded_file = genai.upload_file(path=PDF_FILE_NAME, mime_type="application/pdf")
        
        # =========================================================
        # 👇 [설정 2] 사용할 AI 모델 이름 (아까 확인한 무료/고성능 모델)
        # 2.0-flash가 가장 빠르고 성능이 좋습니다.
        model = genai.GenerativeModel('models/gemini-flash-latest')
        # =========================================================
        
        return model, uploaded_file, "성공"
        
    except Exception as e:
        return None, None, str(e)

# 4. 로딩 실행 (화면 표시)
with st.spinner("AI 선생님이 교재를 읽고 있습니다..."):
    model, sample_file, msg = load_ai_model()

if model is None:
    st.error(f"❌ 오류 발생: {msg}")
    st.stop()

# 5. 질문 입력 화면
st.success("✅ 준비 완료! 교재 내용에 대해 물어보세요.")

user_question = st.text_area("질문 입력", height=100, placeholder="예: 7과의 문법으로 사지선다 문제를 5개 만들어줘.")

if st.button("질문하기", type="primary"):
    if not user_question:
        st.warning("질문 내용을 입력해주세요.")
    else:
        with st.spinner("답변을 작성 중입니다..."):
            try:
                # =========================================================
                # ⭐⭐⭐ [설정 3] AI 성격 및 답변 지침 설정 (가장 중요!) ⭐⭐⭐
                # 이 아래 따옴표 안의 문장들을 수정하면 AI의 말투가 바뀝니다.
                # =========================================================
                system_instruction = [
                    "당신은 선생님들에게 수업 준비를 도와주는 상담가입니다.",
                    "선생님들이 문법이나 단어에 대해서 질문하거나 문제를 요구할 것입니다.",
                    "답변할 때는 다음 원칙을 반드시 지키세요:",
                    "1. 무조건 제공된 교재 파일(PDF)에 있는 예문을 최우선으로 인용하세요.",
                    "2. 교재에 없는 내용을 설명할 때는 '교재에는 없지만...'이라고 언급하세요.",
                    "3. 문법을 비교할 때는 표(Table) 형식을 사용하여 시각적으로 명확하게 보여주세요.",
                    "4. 말투는 '해요체'를 사용하고, 매우 친절하고 격려하는 태도를 보이세요.",
                    f"학생의 질문: {user_question}", # 👈 학생 질문이 들어가는 곳 (수정 X)
                    sample_file # 👈 교재 파일이 들어가는 곳 (수정 X)
                ]
                # =========================================================

                # 답변 생성
                response = model.generate_content(system_instruction)
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"답변 생성 중 오류가 발생했습니다: {e}")



