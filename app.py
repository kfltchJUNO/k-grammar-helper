import streamlit as st
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="우리 반 수업 도우미", page_icon="🏫")
st.title("🏫 우리 반 한국어 수업 도우미")

# =========================================================
# 👇 [설정 1] GitHub에 올린 파일 이름들을 여기에 정확히 적어주세요!
# (대소문자, 띄어쓰기까지 깃허브와 똑같아야 합니다)
PDF_FILES = ["단국한국어 1가_압축", "단국한국어 1-나_압축.pdf"] 
# =========================================================

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

# 3. 모델 및 파일 로딩 (여러 권 처리)
@st.cache_resource
def load_ai_model():
    # A. 파일 존재 여부 확인 (하나씩 꺼내서 확인)
    for file_name in PDF_FILES:
        if not os.path.exists(file_name):
            return None, None, f"오류: '{file_name}' 파일을 찾을 수 없습니다. GitHub에 파일이 있는지 확인해주세요."
    
    try:
        # B. 파일들을 하나씩 Gemini에 업로드
        uploaded_files_list = []
        for file_name in PDF_FILES:
            uploaded_file = genai.upload_file(path=file_name, mime_type="application/pdf")
            uploaded_files_list.append(uploaded_file)
        
        # C. 모델 설정 (안정적인 모델 사용)
        model = genai.GenerativeModel('models/gemini-flash-latest')
        
        return model, uploaded_files_list, "성공"
        
    except Exception as e:
        return None, None, str(e)

# 4. 로딩 실행
with st.spinner(f"AI 선생님이 교재 {len(PDF_FILES)}권을 읽고 있습니다..."):
    model, sample_files, msg = load_ai_model()

if model is None:
    st.error(f"❌ 실행 중단: {msg}")
    st.stop()

# 5. 질문 입력 화면
st.success(f"✅ 교재 {len(PDF_FILES)}권 준비 완료! 무엇이든 물어보세요.")

user_question = st.text_area("질문 입력", height=100, placeholder="예: 2과 문법으로 사지선다 퀴즈 2개 부탁해.")

if st.button("질문하기", type="primary"):
    if not user_question:
        st.warning("질문 내용을 입력해주세요.")
    else:
        with st.spinner("여러 교재를 분석하여 답변 중입니다..."):
            try:
                # 시스템 지시문
                system_instruction = [
                    "당신은 베테랑 한국어 선생님입니다.",
                    "제공된 모든 교재(PDF)의 내용을 종합적으로 분석하여 답변하세요.",
                    "1. 답변은 반드시 교재 내용을 근거로 해야 합니다.",
                    "2. 여러 교재에 관련 내용이 있다면 비교해서 설명하세요.",
                    "3. 친절한 '해요체'를 사용하세요.",
                    "4. 교재에 없는 내용이면 반드시 언급해 주세요.",
                    f"질문: {user_question}"
                ]
                
                # ⭐ 파일 리스트를 프롬프트에 합치기
                final_prompt = system_instruction + sample_files
                
                # 답변 생성
                response = model.generate_content(final_prompt)
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"답변 생성 중 오류가 발생했습니다: {e}")
