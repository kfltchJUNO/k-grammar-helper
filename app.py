import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 페이지 설정
st.set_page_config(page_title="한국어 수업 도우미", page_icon="📚")
st.title("📚 한국어 수업 준비 도우미")

# 사이드바
with st.sidebar:
    st.header("설정")
    uploaded_file = st.file_uploader("교재 PDF 업로드", type=["pdf"])

# 메인 로직
if uploaded_file is not None:
    # API 키 확인 (Streamlit Secrets에서 가져옴)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("API 키가 설정되지 않았습니다.")
        st.stop()

    # 파일 처리
    with st.spinner("교재를 읽고 있습니다..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            model = genai.GenerativeModel('gemini-1.5-flash')
            sample_file = genai.upload_file(path=tmp_file_path, mime_type="application/pdf")
            st.success("분석 완료! 질문하세요.")
        except Exception as e:
            st.error(f"오류: {e}")

    # 질문 입력
    user_question = st.text_area("질문 예시: -던과 -았/었던의 차이를 설명해줘")
    
    if st.button("질문하기"):
        if user_question:
            with st.spinner("답변 생성 중..."):
                prompt = [
                    "당신은 한국어 교육 전문가입니다. 교재 내용을 바탕으로 답변하세요.",
                    "질문: " + user_question,
                    sample_file
                ]
                response = model.generate_content(prompt)
                st.markdown(response.text)

elif uploaded_file is None:
    st.info("👈 왼쪽에서 교재 PDF를 먼저 업로드해주세요.")