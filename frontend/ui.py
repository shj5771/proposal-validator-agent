import streamlit as st
import time
import requests
import json
from pypdf import PdfReader

BACKEND_URL_SYNC = "http://127.0.0.1:8000/api/v1/chat/sync"

st.set_page_config(page_title="기획서 검증 에이전트", page_icon="💬", layout="centered")

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css');
        * { font-family: 'Pretendard Variable', Pretendard, -apple-system, system-ui, sans-serif !important; }
        .stApp { background-color: #ffffff; color: #0a0b0d; }
        header {visibility: hidden;}
        .stChatMessageAvatar { background-color: transparent !important; border-radius: 50%; }
        [data-testid="stChatMessage"]:not([data-testid="stChatMessage"][aria-label="user"]) {
            background-color: #f7f7f7; border-radius: 24px; padding: 16px 24px; margin: 12px 0px; max-width: 85%; border: 1px solid #dee1e6; box-shadow: none;
        }
        [data-testid="stChatMessage"]:not([data-testid="stChatMessage"][aria-label="user"]) .stMarkdown * {
            color: #0a0b0d !important; font-weight: 450 !important; line-height: 1.6;
        }
        [data-testid="stChatMessage"][aria-label="user"] {
            background-color: #0052ff; border-radius: 24px; padding: 16px 24px; margin: 12px 0px 12px auto; max-width: 85%; flex-direction: row-reverse; border: none;
        }
        [data-testid="stChatMessage"][aria-label="user"] .stMarkdown * {
            color: #ffffff !important; font-weight: 450 !important; line-height: 1.6;
        }
        [data-testid="stChatMessage"][aria-label="user"] .stChatMessageAvatar {
            margin-left: 1rem; margin-right: 0; background-color: #ffffff !important; color: #0052ff !important;
        }
        .stChatInputContainer { background-color: #ffffff !important; padding: 16px !important; border-top: 1px solid #dee1e6; }
        .st-emotion-cache-28gi3v.ewh6kot2 { display: none !important; }
        [data-testid="stVerticalBlock"]:has(.upload-container-marker) {
            background-color: rgb(255, 255, 255); padding: 28px 24px; border-radius: 24px; border: 1px solid rgb(222, 225, 230); box-shadow: rgba(0, 0, 0, 0.02) 0px 4px 12px; text-align: center; margin-bottom: 40px; margin-top: 32px;
        }
        .upload-container-marker { display: none; }
        .primary-cta-container .stButton > button { background-color: #0052ff !important; border-radius: 100px !important; padding: 16px 32px !important; border: none !important; }
        .primary-cta-container .stButton > button * { color: #ffffff !important; font-weight: 600 !important; font-size: 16px !important; }
        .primary-cta-container .stButton > button:hover { background-color: #003ecc !important; }
        .exit-button-container .stButton > button { background-color: #eef0f3 !important; border-radius: 100px !important; padding: 8px 16px !important; border: none !important; }
        .exit-button-container .stButton > button * { color: #0a0b0d !important; font-weight: 600 !important; }
        .exit-button-container .stButton > button:hover { background-color: #dee1e6 !important; }
        h1, h2, h3 { color: #0a0b0d; font-weight: 700 !important; letter-spacing: -1px !important; }
        </style>
    """, unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "upload"
if "messages" not in st.session_state: st.session_state.messages = []
if "proposal_text" not in st.session_state: st.session_state.proposal_text = ""

def parse_file(uploaded_file) -> str:
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages])
    return uploaded_file.read().decode("utf-8")

def render_upload_page():
    st.markdown("""
        <div style="background-color: #0a0b0d; color: #ffffff; padding: 64px 32px; border-radius: 24px; text-align: center; margin-bottom: 48px;">
            <h1 style="color: #ffffff !important; font-size: 48px; font-weight: 700; margin-bottom: 16px;">기획의 빈틈을 찾다</h1>
            <p style="color: #a8acb3; font-size: 18px; max-width: 600px; margin: 0 auto;">실제 발표 전에 3명의 AI 심사위원에게 가장 날카로운 압박 질문을 미리 맞아보세요.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div style="background-color: #ffffff; padding: 28px 24px; border-radius: 24px; border: 1px solid #dee1e6;"><h2>💼 투자자</h2><p>시장성과 수익성 검증</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div style="background-color: #ffffff; padding: 28px 24px; border-radius: 24px; border: 1px solid #dee1e6;"><h2>💻 CTO</h2><p>기술 실현 가능성 평가</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div style="background-color: #ffffff; padding: 28px 24px; border-radius: 24px; border: 1px solid #dee1e6;"><h2>🦉 멘토</h2><p>논리적 일관성과 범위 지적</p></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="upload-container-marker"></span>', unsafe_allow_html=True)
        st.markdown('<h2>기획서 업로드</h2><p>TXT 또는 PDF 형식의 기획서를 올려주세요.</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("파일 첨부", type=['txt', 'pdf'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            st.success("파일 업로드 성공!")
            st.markdown('<div class="primary-cta-container">', unsafe_allow_html=True)
            if st.button("🚀 모의 심사 시작하기", use_container_width=True):
                st.session_state.proposal_text = parse_file(uploaded_file)
                st.session_state.page = "chat"
                # 🎯 핵심: 화면 넘어가면서 오케스트레이터의 인사말을 미리 깔아둔다.
                st.session_state.messages = [
                    {"role": "assistant", "name": "오케스트레이터", "content": "기획서 파싱을 완료했습니다. 지금부터 투자자, CTO, 멘토 심사위원의 압박 질문을 시작하겠습니다. 준비되셨나요?", "avatar": "🤖"}
                ]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_chat_page():
    col1, col2 = st.columns([8, 2])
    with col1: st.subheader("💬 기획서 검증 방")
    with col2:
        st.markdown('<div class="exit-button-container">', unsafe_allow_html=True)
        if st.button("나가기"):
            st.session_state.page = "upload"
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "👤")):
            if msg["role"] == "assistant":
                st.caption(f"**{msg.get('name', '심사위원')}**")
            st.markdown(msg["content"])

    if prompt := st.chat_input("답변을 입력해주세요... (예: 네)"):
        # 내 채팅 추가 (👤 아바타 고정)
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🤖"):
            st.caption("**답변 분석 중...**")
            with st.spinner("다음 심사위원이 압박 질문을 준비 중입니다..."):
                try:
                    # 백엔드에 쏠 때, 오케스트레이터 인사말(0번 인덱스)은 빼고 유저 채팅 기록만 보냄
                    history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] == "user"]
                    
                    res = requests.post(
                        BACKEND_URL_SYNC, 
                        json={
                            "message": prompt, 
                            "proposal_text": st.session_state.proposal_text,
                            "history": history_payload
                        }
                    )
                    
                    if res.status_code == 200:
                        data = res.json()
                        answer = data.get("answer", "")
                        domain = data.get("domain", "")

                        # 🎯 백엔드에서 받은 domain 명찰에 따라 아바타와 닉네임 강제 교체!
                        persona_map = {
                            "investor": ("투자자", "💼"),
                            "cto": ("CTO", "💻"),
                            "mentor": ("멘토", "🦉"),
                            "report": ("오케스트레이터 (최종 결과)", "📊")
                        }
                        
                        name, icon = persona_map.get(domain, ("오케스트레이터", "🤖"))
                        
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "name": name, "content": answer, "avatar": icon})
                except Exception as e:
                    st.error(f"백엔드 연결 실패: {e}")
        st.rerun()

def main():
    inject_custom_css()
    if st.session_state.page == "upload":
        render_upload_page()
    elif st.session_state.page == "chat":
        render_chat_page()

if __name__ == "__main__":
    main()