"""
議事録AI - Vivid & Pop Edition
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import google.auth
import google.auth.transport.requests
from google.oauth2 import id_token

# ===== 設定 =====
API_URL = os.environ.get('API_URL', 'http://localhost:8080')

# ===== 認証処理 =====
def get_auth_headers(target_url):
    headers = {}
    try:
        if "localhost" not in target_url:
            auth_req = google.auth.transport.requests.Request()
            token = id_token.fetch_id_token(auth_req, target_url)
            headers["Authorization"] = f"Bearer {token}"
    except: pass
    return headers

# ===== ページ設定 =====
st.set_page_config(
    page_title="議事録AI | Minutes AI",
    page_icon="⭐",
    layout="wide"
)

# ===== カスタムCSS (ビビッド＆ポップ) =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'M PLUS Rounded 1c', sans-serif;
        background-color: #f0f7ff; /* 薄いブルーの背景 */
    }

    /* タイトルセクション */
    .header-container {
        text-align: center;
        padding: 40px 0;
        background: #0056b3; /* 濃いブルー */
        border-radius: 0 0 50px 50px;
        margin-bottom: 40px;
    }
    .main-title {
        color: #ffcc00; /* 鮮やかなイエロー */
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 0px #003366;
    }
    .sub-title-en {
        color: white;
        font-size: 1.2rem;
        letter-spacing: 0.3rem;
        font-weight: 700;
        opacity: 0.9;
    }

    /* はっきりしたカードデザイン */
    .st-emotion-cache-1r6slb0, .css-1r6slb0 {
        background-color: white;
        border-radius: 30px;
        padding: 35px;
        border: 4px solid #0056b3; /* 太めの青枠 */
        box-shadow: 10px 10px 0px #ffcc00; /* 黄色の影をあえてズラして配置 */
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: #003366;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 20px;
    }
    .st-emotion-cache-6qob1r { /* サイドバーテキスト */
        color: white !important;
    }

    /* ビビッドなボタン */
    .stButton > button {
        border-radius: 20px;
        background-color: #ffcc00;
        color: #003366 !important;
        border: 3px solid #003366;
        padding: 15px 30px;
        font-size: 1.3rem;
        font-weight: 800;
        transition: 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #ffd633;
        transform: translate(-3px, -3px);
        box-shadow: 5px 5px 0px #003366;
    }

    /* セレクトボックスなどの入力欄 */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 15px;
        border: 2px solid #0056b3;
    }

    /* ステータスカード */
    .info-tag {
        background-color: #e6f2ff;
        border-left: 8px solid #0056b3;
        padding: 15px;
        border-radius: 10px;
        color: #003366;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ===== データ取得・API関数 (中身は維持) =====
def get_master_data():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/master", headers=headers, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return {'departments': [{'id': 'sales', 'name': '営業部'}, {'id': 'dev', 'name': '開発部'}], 'folders': [{'id': 'f1', 'name': '定例'}]}

def upload_file_api(file, department, folder):
    try:
        headers = get_auth_headers(API_URL)
        files = {'file': (file.name, file.getvalue(), file.type)}
        data = {'department': department, 'folder': folder}
        response = requests.post(f"{API_URL}/upload", headers=headers, files=files, data=data, timeout=3600)
        return response.json()
    except Exception as e: return {'success': False, 'error': str(e)}

# ===== サイドバーメニュー =====
with st.sidebar:
    st.markdown("<h1 style='color: #ffcc00; text-align: center;'>MENU</h1>", unsafe_allow_html=True)
    page = st.radio("", ["🚀 UPLOAD", "📜 HISTORY", "⭐ GUIDE"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<p style='color: #88aaff; font-size: 0.8rem; text-align: center;'>System Status: Online</p>", unsafe_allow_html=True)

# ===== メインレイアウト =====
st.markdown("""
    <div class="header-container">
        <p class="main-title">議事録AI</p>
        <p class="sub-title-en">MINUTES AI GENERATOR</p>
    </div>
""", unsafe_allow_html=True)

if page == "🚀 UPLOAD":
    master = get_master_data()
    
    col_set1, col_set2 = st.columns([2, 1])
    
    with col_set1:
        st.markdown("### 🛠 SETTINGS / 設定")
        c1, c2 = st.columns(2)
        with c1:
            dept_options = {d['name']: d['id'] for d in master['departments']}
            selected_dept = st.selectbox("Select Dept (部署選択)", options=list(dept_options.keys()))
        with c2:
            folder_options = {f['name']: f['id'] for f in master['folders']}
            selected_folder = st.selectbox("Select Folder (保存先フォルダ)", options=list(folder_options.keys()))

        st.markdown("### 🎤 AUDIO UPLOAD / 音声アップロード")
        uploaded_file = st.file_uploader("", type=['mp3', 'mp4', 'wav', 'm4a'], label_visibility="collapsed")

        if uploaded_file:
            st.markdown(f'<div class="info-tag">📂 FILE: {uploaded_file.name}</div>', unsafe_allow_html=True)
            st.write("")
            if st.button("GENERATE / 議事録を作成する！"):
                with st.spinner("AI IS ANALYZING... 🚀"):
                    result = upload_file_api(uploaded_file, dept_options[selected_dept], folder_options[selected_folder])
                    if result.get('success'):
                        st.balloons()
                        st.success("SUCCESS! 議事録が完成しました！ ✨")
                    else:
                        st.error(f"ERROR: {result.get('error')}")

    with col_set2:
        st.markdown("### 💡 HINT")
        st.info("はっきりした録音ほど、AIの精度がアップします！✨")

elif page == "📜 HISTORY":
    st.markdown("### 📜 RECENT ACTIVITY / 利用履歴")
    st.info("過去に作成した議事録のデータがここに並びます。")

else:
    st.markdown("### ⭐ HOW TO USE / 使い方")
    st.markdown("""
    1. **SETTINGS**: 部署と保存先を選びます。
    2. **UPLOAD**: 音声ファイルをセットします。
    3. **GENERATE**: 黄色のボタンをポチッと押すだけ！
    """)

# フッター
st.markdown("<br><hr><p style='text-align: center; color: #0056b3; font-weight: bold;'>Minutes AI © 2026 | Smart & Vivid</p>", unsafe_allow_html=True)