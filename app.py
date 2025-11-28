import streamlit as st
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="수업 도우미 (진단모드)", page_icon="🔧")
st.title("🔧 모델 연결 진단 및 수업 도우미")

# 2. API 키 설정
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"API 키 설정 오류: {e}")
        st.stop()
else:
    st.error("🚨 API 키가 없습니다. Streamlit 설정을 확인해주세요.")
    st.stop()

# ==========================================
# 🔍 [진단 구간] 사용 가능한 모델 목록 출력
# ==========================================
st.markdown("### 1. Google 서버 연결 테스트")
try:
    st.write("사용 가능한 모델을 조회합니다...")
    available_models = []
    
    # 구글 서버에 "나한테 허용된 모델 다 보여줘" 요청
    for m in genai.list_models():
        # '대화(generateContent)'가 가능한 모델만 추리기
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    if available_models:
        st.success(f"✅ 연결 성공! 감지된 모델 {len(available_models)}개")
        st.json(available_models) # 화면에 목록을 예쁘게 보여줌
    else:
        st.warning("⚠️ 연결은 됐는데, 사용 가능한 모델이 하나도 없습니다. (API 키 권한 문제일 수 있음)")

except Exception as e:
    st.error(f"❌ 모델 목록 조회 실패 (원인): {e}")
    st.info("💡 팁: requirements.txt 버전을 확인하거나 API 키를 점검하세요.")

st.markdown("---")

# ==========================================
# 🏫 [본 기능] 수업 도우미 앱 로직
# ==========================================
st.markdown("### 2. 교재 분석 앱 실행")

# 👇 [중요] 깃허브에 올린 파일명과 똑같아야 함!
PDF_FILE_NAME = "단국한국어 1가_압축.pdf" 

@st.cache_resource
def load_ai_model():
    if not os.path.exists(PDF_FILE_NAME):
        return None, None, f"파일 없음: {PDF_FILE_NAME}"
    
    try:
        # A. 파일 업로드
        uploaded_file = genai.upload_file(path=PDF_FILE_NAME, mime_type="application/pdf")
        
        # B. 모델 설정 (위 진단 목록에 있는 이름 중 하나를 써야 함)
        # 일단 가장 기본형으로 시도
        target_model = 'gemini-1.5-flash' 
        
        # 만약 목록에 'models/'가 붙어있으면 붙여줘야 함
        # 안전하게 'models/gemini-1.5-flash'로 시도해봅니다.
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        return model, uploaded_file, "성공"
        
    except Exception as e:
        return None, None, str(e)

# 실행 버튼
if st.button("앱 실행 시도하기 (모델 로딩)"):
    with st.spinner("모델을 불러오는 중..."):
        model, sample_file, msg = load_ai_model()
        
        if model:
            st.success("🎉 모델 로딩 성공! 질문을 입력하세요.")
            st.session_state['model_loaded'] = True
            st.session_state['model'] = model
            st.session_state['file'] = sample_file
        else:
            st.error(f"❌ 모델 로딩 실패: {msg}")

# 모델이 로드되었을 때만 질문창 표시
if st.session_state.get('model_loaded'):
    user_question = st.text_area("질문 입력", placeholder="예: 문법 설명해줘")
    if st.button("질문하기"):
        if user_question:
            try:
                model = st.session_state['model']
                file = st.session_state['file']
                response = model.generate_content([user_question, file])
                st.markdown(response.text)
            except Exception as e:
                st.error(f"답변 생성 오류: {e}")

