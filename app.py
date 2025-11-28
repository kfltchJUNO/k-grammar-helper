import streamlit as st
import google.generativeai as genai
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="우리 반 수업 도우미", page_icon="🏫")
st.title("🏫 우리 반 한국어 수업 도우미")

# ==========================================
# 👇 [중요] GitHub에 올린 PDF 파일 이름과 똑같이 적어주세요!
# (대소문자까지 정확해야 합니다. 예: textbook.pdf)
PDF_FILE_NAME = "textbook.pdf" 
# ==========================================

# 2. API 키 확인 (Secrets에서 가져오기)
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
        st.stop()
else:
    st.error("🚨 API 키가 설정되지 않았습니다. Streamlit 설정을 확인해주세요.")
    st.stop()

# 3. 모델 및 파일 로딩 함수 (캐싱 적용)
@st.cache_resource
def load_ai_model():
    # A. 파일 존재 여부 확인
    if not os.path.exists(PDF_FILE_NAME):
        return None, None, f"파일을 찾을 수 없습니다: {PDF_FILE_NAME}"
    
    try:
        # B. Gemini에 파일 업로드
        uploaded_file = genai.upload_file(path=PDF_FILE_NAME, mime_type="application/pdf")
        
        # C. 모델 불러오기 (models/ 접두사 포함)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        return model, uploaded_file, "성공"
        
    except Exception as e:
        return None, None, f"AI 연결 중 오류 발생: {e}"

# 4. 로딩 실행
with st.spinner("AI 선생님이 교재를 읽고 있습니다..."):
    model, sample_file, status_msg = load_ai_model()

# 5. 로딩 실패 시 중단 (여기서 NameError 방지)
if model is None:
    st.error(f"❌ 오류가 발생하여 앱을 실행할 수 없습니다.\n원인: {status_msg}")
    st.info("💡 팁: GitHub에 올린 PDF 파일 이름이 코드와 일치하는지 확인해보세요.")
    st.stop() # 여기서 멈추기 때문에 밑에 코드는 실행 안 됨

# 6. 질문 입력 화면
st.markdown("---")
st.success("✅ 교재 준비 완료! 무엇이든 물어보세요.")

user_question = st.text_area("질문 입력", height=100, placeholder="예: 이 교재에서 -던과 -았/었던의 차이를 설명해줘")

if st.button("질문하기", type="primary"):
    if not user_question:
        st.warning("내용을 입력해주세요.")
    else:
        with st.spinner("답변을 작성 중입니다..."):
            try:
                # 프롬프트 구성
                prompt = [
                    "당신은 한국어 교육 전문가입니다.",
                    "다음 교재 파일을 분석하여 질문에 답변하세요.",
                    "학생 수준에 맞춰 쉽고 친절하게 설명하세요.",
                    f"질문: {user_question}",
                    sample_file
                ]
                
                # 답변 생성
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"답변 생성 중 오류가 발생했습니다: {e}")
