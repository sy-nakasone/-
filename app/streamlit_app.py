"""
会議文字起こしシステム
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
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
    page_title="会議文字起こしシステム",
    page_icon="📝",
    layout="wide"
)

# ===== カスタムCSS =====
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', sans-serif;
        background-color: #f5f5f5;
    }

    /* タイトルセクション */
    .header-container {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-bottom: 30px;
        border-radius: 0 0 20px 20px;
    }
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        margin-bottom: 10px;
    }
    .sub-title {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
    }

    /* ナビゲーションボタン */
    .nav-button {
        padding: 12px 24px;
        margin: 5px;
        border-radius: 8px;
        border: none;
        background-color: #e0e0e0;
        color: #333;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .nav-button:hover {
        background-color: #d0d0d0;
    }
    .nav-button.active {
        background-color: #667eea;
        color: white;
    }

    /* 統計カード */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        margin: 10px 0;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
    }
    .stat-change {
        font-size: 0.85rem;
        color: #4caf50;
        font-weight: 600;
    }

    /* 履歴アイテム */
    .history-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .history-file-name {
        font-weight: 600;
        color: #333;
        margin-bottom: 5px;
    }
    .history-meta {
        font-size: 0.85rem;
        color: #666;
        margin: 5px 0;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-completed {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .status-processing {
        background-color: #fff3e0;
        color: #e65100;
    }

    /* アップロードエリア */
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background-color: #f8f9ff;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== データ取得・API関数 =====
def get_master_data():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/master", headers=headers, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return {'departments': [{'id': 'sales', 'name': '営業部'}, {'id': 'dev', 'name': '開発部'}], 'folders': [{'id': 'f1', 'name': '定例'}]}

def get_statistics():
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/statistics", headers=headers, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return {'total_count': 0, 'this_month': 0, 'by_department': {}}

def get_history(limit=100):
    try:
        headers = get_auth_headers(API_URL)
        response = requests.get(f"{API_URL}/history?limit={limit}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('history', [])
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

# ===== ヘッダー =====
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">会議文字起こしシステム</h1>
        <p class="sub-title">会議録音を自動で文字起こしして保存・管理</p>
    </div>
""", unsafe_allow_html=True)

# ===== ナビゲーション =====
st.markdown("""
<style>
    .nav-container {
        display: flex;
        gap: 10px;
        margin-bottom: 30px;
    }
    .nav-btn {
        flex: 1;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        background-color: #e0e0e0;
        color: #333;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }
    .nav-btn:hover {
        background-color: #d0d0d0;
    }
    .nav-btn.active {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    upload_btn = st.button("アップロード", use_container_width=True, key="nav_upload", type="primary" if st.session_state.get('page', 'upload') == 'upload' else "secondary")
with col2:
    history_btn = st.button("履歴", use_container_width=True, key="nav_history", type="primary" if st.session_state.get('page') == 'history' else "secondary")
with col3:
    stats_btn = st.button("統計", use_container_width=True, key="nav_stats", type="primary" if st.session_state.get('page') == 'stats' else "secondary")

# ページ選択
if upload_btn:
    st.session_state.page = "upload"
elif history_btn:
    st.session_state.page = "history"
elif stats_btn:
    st.session_state.page = "stats"
elif 'page' not in st.session_state:
    st.session_state.page = "upload"

# ===== メインコンテンツ =====
if st.session_state.page == "upload":
    st.markdown("### 新規アップロード")
    
    master = get_master_data()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**部門の設定**")
        dept_options = {d['name']: d['id'] for d in master['departments']}
        selected_dept = st.selectbox("", options=list(dept_options.keys()), label_visibility="collapsed")
    
    with col2:
        st.markdown("**保存先フォルダー**")
        folder_options = {f['name']: f['id'] for f in master['folders']}
        selected_folder = st.selectbox("", options=list(folder_options.keys()), label_visibility="collapsed")
    
    st.markdown("**音声・動画ファイル**")
    uploaded_file = st.file_uploader(
        "ファイルをドラッグ&ドロップ または ファイルを選択",
        type=['mp3', 'mp4', 'wav', 'm4a', 'mov'],
        label_visibility="collapsed",
        help="対応形式: MP3, WAV, M4A, MP4, MOV"
    )
    
    if uploaded_file:
        st.info(f"📂 選択されたファイル: {uploaded_file.name}")
        if st.button("🚀 議事録を生成", type="primary", use_container_width=True):
            with st.spinner("処理中..."):
                result = upload_file_api(uploaded_file, dept_options[selected_dept], folder_options[selected_folder])
                if result.get('success'):
                    st.success("✅ 議事録の生成が完了しました！")
                    if result.get('doc_url'):
                        st.markdown(f"📄 [議事録を表示]({result.get('doc_url')})")
                else:
                    st.error(f"❌ エラー: {result.get('error')}")

elif st.session_state.page == "history":
    st.markdown("### アップロード履歴")
    
    history = get_history()
    
    if history:
        for item in history:
            status_class = "status-completed" if item.get('status') == '完了' else "status-processing"
            status_text = item.get('status', '処理中')
            file_name = item.get('file', 'N/A')
            date_str = item.get('date', 'N/A')
            department = item.get('department', 'N/A')
            folder = item.get('folder', 'N/A')
            doc_url = item.get('doc_url', '')
            
            # 日付をフォーマット（YYYY-MM-DD HH:MM形式に変換）
            try:
                if ' ' in date_str:
                    date_part, time_part = date_str.split(' ', 1)
                    formatted_date = f"{date_part} {time_part[:5]}"
                else:
                    formatted_date = date_str
            except:
                formatted_date = date_str
            
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-file-name">{file_name}</div>
                    <div class="history-meta">
                        🏢 {department} | 📁 {folder} | 📅 {formatted_date}
                    </div>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if doc_url:
                    st.markdown(f'<a href="{doc_url}" target="_blank" style="color: #667eea; text-decoration: none;">表示</a>', unsafe_allow_html=True)
            with col3:
                if doc_url:
                    st.markdown(f'<a href="{doc_url}" target="_blank" style="color: #667eea; text-decoration: none;">DL</a>', unsafe_allow_html=True)
    else:
        st.info("履歴がありません")

elif st.session_state.page == "stats":
    st.markdown("### 統計情報")
    
    stats = get_statistics()
    
    # 統計カード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">今月のアップロード</div>
            <div class="stat-value">{stats.get('this_month', 0)} ファイル</div>
            <div class="stat-change">+12% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">総文字起こし時間</div>
            <div class="stat-value">18.5 時間</div>
            <div class="stat-change">+8% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">完了済み</div>
            <div class="stat-value">{stats.get('completed_count', stats.get('total_count', 0))} ファイル</div>
            <div class="stat-change">+15% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">使用中のフォルダー</div>
            <div class="stat-value">{stats.get('active_folders', 8)} フォルダー</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 部門別利用状況
    st.markdown("### 部門別利用状況")
    
    dept_stats = stats.get('by_department', {})
    if dept_stats:
        df = pd.DataFrame([
            {'部門': dept, '利用回数': count}
            for dept, count in dept_stats.items()
        ])
        
        # 色のマッピング
        color_map = {
            '営業部': '#2196F3',
            '開発部': '#4CAF50',
            'マーケティング部': '#9C27B0',
            '人事部': '#FF9800',
            '経理部': '#E91E63'
        }
        
        fig = px.bar(
            df,
            x='部門',
            y='利用回数',
            color='部門',
            color_discrete_map=color_map,
            text='利用回数',
            labels={'利用回数': '利用回数', '部門': '部門'}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="利用回数"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("データがありません")

# フッター
st.markdown("<br><hr><p style='text-align: center; color: #666; font-size: 0.9rem;'>© 2026 会議文字起こしシステム - DX推進プラットフォーム</p>", unsafe_allow_html=True)