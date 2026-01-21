"""
会議文字起こしシステム - UI改良版（重複IDエラー修正済み）
"""

import streamlit as st
import requests
import pandas as pd
import os
import google.auth
import google.auth.transport.requests
from google.oauth2 import id_token
import plotly.express as px

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
    page_title="GIJIROKU AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== カスタムCSS (スタイリッシュなデザイン) =====
st.markdown("""
<style>
    /* 背景グラデーション */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 15s ease infinite !important;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 900px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-top: 1rem;
        margin-bottom: 2rem;
        padding: 2rem;
    }
    
    /* ヘッダー */
    .gijiroku-header {
        text-align: center;
        padding: 2rem 1.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        color: white;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    .gijiroku-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* カード */
    .card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 2px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
    }
    
    .card-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e7ff;
    }
    
    /* ナビゲーションボタン */
    div[data-testid="column"] button {
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        border: 2px solid transparent !important;
    }
    div[data-testid="column"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* タブボタン（デフォルト） */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, #f8f9ff 0%, #e0e7ff 100%) !important;
        color: #667eea !important;
        border: 2px solid #c7d2fe !important;
    }
    
    /* メインボタン（議事録生成） */
    div.stButton > button[type="primary"],
    button[data-testid*="execute_gen_btn"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button[type="primary"]:hover,
    button[data-testid*="execute_gen_btn"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    /* 設定ラベル */
    .setting-label {
        font-size: 0.85rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff9c4 0%, #ffe082 100%);
        padding: 0.4rem 0.8rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 0.5rem;
        display: inline-block;
        border-radius: 6px;
        color: #856404;
        box-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
    }
    
    /* セレクトボックス */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%) !important;
        border-radius: 10px !important;
        border: 2px solid #c7d2fe !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:hover {
        border-color: #667eea !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ファイルアップローダー */
    .stFileUploader {
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    .stFileUploader:hover {
        border-color: #764ba2 !important;
        background: linear-gradient(135deg, #e0e7ff 0%, #d1d9ff 100%) !important;
    }
    
    /* ステータスバッジ */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 0.5rem;
    }
    .status-completed { 
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
        color: #1b5e20;
        box-shadow: 0 2px 4px rgba(46, 125, 50, 0.2);
    }
    .status-error { 
        background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%);
        color: #b71c1c;
        box-shadow: 0 2px 4px rgba(198, 40, 40, 0.2);
    }
    
    /* リンク */
    a {
        color: #667eea !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
    }
    a:hover {
        color: #764ba2 !important;
        text-decoration: underline !important;
    }
    
    /* テーブル */
    .stTable {
        background: white !important;
        border-radius: 12px !important;
    }
    
    /* 警告・成功メッセージ */
    .stSuccess {
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%) !important;
        border-left: 4px solid #4caf50 !important;
        border-radius: 8px !important;
    }
    .stError {
        background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%) !important;
        border-left: 4px solid #f44336 !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background: linear-gradient(135deg, #fff9c4 0%, #ffe082 100%) !important;
        border-left: 4px solid #ffc107 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== API関数 =====
def get_master_data():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/master", headers=headers, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return {'departments': [{'id': 'sales', 'name': '営業部'}], 'folders': [{'id': 'f1', 'name': '定例'}]}

def get_statistics():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/statistics", headers=headers, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return {'this_month': 0, 'total_count': 0, 'monthly_history': {}}

def get_history():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/history?limit=50", headers=headers, timeout=10)
        if response.status_code == 200: return response.json().get('history', [])
    except: pass
    return []

def upload_file_api(file, department, folder):
    try:
        headers = get_auth_headers(API_URL)
        files = {'file': (file.name, file.getvalue(), file.type)}
        data = {'department': department, 'folder': folder}
        response = requests.post(f"{API_URL}/upload", headers=headers, files=files, data=data, timeout=3600)
        return response.json()
    except Exception as e: return {'success': False, 'error': str(e)}

# ===== メイン処理 =====
st.markdown('<div class="gijiroku-header"><h1>GIJIROKU AI</h1></div>', unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = "upload"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("議事録生成", use_container_width=True, key="nav_btn_upload"): st.session_state.page = "upload"
with col2:
    if st.button("履歴", use_container_width=True, key="nav_btn_history"): st.session_state.page = "history"
with col3:
    if st.button("統計", use_container_width=True, key="nav_btn_stats"): st.session_state.page = "stats"

# 選択中タブ強調
idx = {"upload": 1, "history": 2, "stats": 3}[st.session_state.page]
st.markdown(f'<style>div[data-testid="column"]:nth-of-type({idx}) button {{ background: #E0F2FE !important; color: #0047AB !important; border: 2px solid #0047AB !important; }}</style>', unsafe_allow_html=True)

if st.session_state.page == "upload":
    master = get_master_data()
    
    st.markdown('<div class="card"><div class="card-title">設定</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="setting-label">部署名</span>', unsafe_allow_html=True)
        dept_map = {d['name']: d['id'] for d in master['departments']}
        sel_dept = st.selectbox("", options=list(dept_map.keys()), label_visibility="collapsed", key="select_dept")
    with c2:
        st.markdown('<span class="setting-label">保存先フォルダ</span>', unsafe_allow_html=True)
        fold_map = {f['name']: f['id'] for f in master['folders']}
        sel_fold = st.selectbox("", options=list(fold_map.keys()), label_visibility="collapsed", key="select_folder")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-title">音声・動画ファイル</div>', unsafe_allow_html=True)
    up_file = st.file_uploader("", type=['mp3', 'mp4', 'wav', 'm4a'], label_visibility="collapsed", key="file_uploader_main")
    
    # 議事録生成ボタンを常時表示
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    if st.button("🚀 議事録を生成開始", type="primary", use_container_width=True, key="execute_gen_btn"):
        if not up_file:
            st.warning("⚠️ ファイルをアップロードしてください。")
        else:
            with st.spinner("⏳ 処理中...しばらくお待ちください"):
                result = upload_file_api(up_file, dept_map[sel_dept], fold_map[sel_fold])
                if result.get('success'):
                    st.success("✅ 完了しました。履歴を確認してください。")
                    if result.get('doc_url'):
                        st.markdown(f'<a href="{result.get("doc_url")}" target="_blank" style="font-size: 1rem; font-weight: 600;">📄 議事録を表示</a>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ エラーが発生しました: {result.get('error')}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "history":
    hist = get_history()
    if not hist:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">履歴がありません</div>
            <div style="color: #6b7280;">議事録を生成すると、ここに履歴が表示されます</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in hist:
            status = item.get('status', '処理中')
            if status == '完了':
                s_class = "status-completed"
            elif "エラー" in status or "error" in status.lower():
                s_class = "status-error"
            else:
                s_class = "status-processing"
                st.markdown("""
                <style>
                .status-processing {
                    background: linear-gradient(135deg, #fff9c4 0%, #ffe082 100%);
                    color: #856404;
                    box-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
                }
                </style>
                """, unsafe_allow_html=True)
            
            doc_url = item.get('doc_url', '')
            link_html = f'<a href="{doc_url}" target="_blank" style="margin-left: 1rem; padding: 0.4rem 0.8rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600;">📄 表示</a>' if doc_url else ""
            
            st.markdown(f'''
            <div class="card">
                <div style="font-weight:700; font-size:1.1rem; color:#1a1a1a; margin-bottom:0.75rem;">📄 {item.get("file", "N/A")}</div>
                <div style="color:#6b7280; font-size:0.9rem; margin-bottom:0.75rem;">
                    🏢 {item.get("department", "N/A")} | 📁 {item.get("folder", "N/A")} | 📅 {item.get("date", "N/A")}
                </div>
                <div style="display: flex; align-items: center;">
                    <span class="status-badge {s_class}">{status}</span>
                    {link_html}
                </div>
            </div>
            ''', unsafe_allow_html=True)

elif st.session_state.page == "stats":
    stats = get_statistics()
    
    # KPIカード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align: center; background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #0369a1; margin-bottom: 0.5rem; text-transform: uppercase;">今月のアップロード</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #0c4a6e; margin: 0.5rem 0;">{stats.get('this_month', 0)}</div>
            <div style="font-size: 0.85rem; color: #0369a1;">ファイル</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card" style="text-align: center; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #92400e; margin-bottom: 0.5rem; text-transform: uppercase;">総文字起こし時間</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #78350f; margin: 0.5rem 0;">18.5</div>
            <div style="font-size: 0.85rem; color: #92400e;">時間</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card" style="text-align: center; background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #1e40af; margin-bottom: 0.5rem; text-transform: uppercase;">完了済み</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e3a8a; margin: 0.5rem 0;">{stats.get('total_count', 0)}</div>
            <div style="font-size: 0.85rem; color: #1e40af;">ファイル</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="card" style="text-align: center; background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #4338ca; margin-bottom: 0.5rem; text-transform: uppercase;">使用中フォルダー</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #312e81; margin: 0.5rem 0;">8</div>
            <div style="font-size: 0.85rem; color: #4338ca;">フォルダー</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 月別統計
    st.markdown('<div class="card"><div class="card-title">月別処理ファイル数</div>', unsafe_allow_html=True)
    m_hist = stats.get('monthly_history', {})
    if m_hist:
        df = pd.DataFrame([{'年月': k, '件数': v} for k, v in m_hist.items()])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #6b7280;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div>データがありません</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)