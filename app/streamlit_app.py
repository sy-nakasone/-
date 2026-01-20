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
    page_title="GIJIROKU AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== カスタムCSS =====
st.markdown("""
<style>
    /* ベーススタイル */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', sans-serif;
        background-color: #f8f9fa;
    }
    
    /* Streamlitのデフォルトスタイルをリセット */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* ヘッダー */
    .gijiroku-header {
        text-align: left;
        padding: 2rem 0 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e0e0e0;
    }
    .gijiroku-title {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .gijiroku-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* タブナビゲーション */
    .tab-container {
        display: flex;
        gap: 0;
        margin-bottom: 2rem;
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .tab-button {
        flex: 1;
        padding: 0.75rem 1.5rem;
        border: none;
        background: transparent;
        color: #6b7280;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .tab-button:hover {
        background: #f3f4f6;
        color: #374151;
    }
    .tab-button.active {
        background: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
    }
    
    /* カードUI */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
    }
    .card-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 設定カード */
    .setting-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .setting-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* アップロードエリア */
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafbfc;
        margin: 1.5rem 0;
        transition: all 0.2s ease;
    }
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #f0f9ff;
    }
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
    .upload-text {
        font-size: 1rem;
        color: #374151;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .upload-hint {
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    /* ボタン */
    .primary-button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.875rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(59,130,246,0.2);
    }
    .primary-button:hover {
        background: #2563eb;
        box-shadow: 0 4px 8px rgba(59,130,246,0.3);
        transform: translateY(-1px);
    }
    
    /* 統計カード */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        height: 100%;
    }
    .stat-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    .stat-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    .stat-change {
        font-size: 0.875rem;
        color: #10b981;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* 履歴カード */
    .history-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        transition: all 0.2s ease;
    }
    .history-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    .history-file-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .history-meta {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0.25rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .history-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .status-completed {
        background: #dbeafe;
        color: #1e40af;
    }
    .status-processing {
        background: #fef3c7;
        color: #92400e;
    }
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    .history-link {
        color: #3b82f6;
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    .history-link:hover {
        color: #2563eb;
        text-decoration: underline;
    }
    
    /* セクションタイトル */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 2rem 0 1rem 0;
    }
    
    /* Streamlitコンポーネントのスタイル調整 */
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    .stSelectbox > div > div:hover {
        border-color: #3b82f6;
    }
    .stFileUploader > div {
        border: none;
        background: transparent;
    }
    
    /* Streamlitのデフォルトメッセージを非表示 */
    .stSuccess, .stError, .stInfo, .stWarning {
        display: none;
    }
    
    /* サイドバーを非表示 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* フッター */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid #e0e0e0;
        color: #6b7280;
        font-size: 0.875rem;
    }
    
    /* 空状態 */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #6b7280;
    }
    .empty-state-icon {
        font-size: 3rem;
        opacity: 0.4;
        margin-bottom: 1rem;
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
    <div class="gijiroku-header">
        <h1 class="gijiroku-title">GIJIROKU AI</h1>
        <p class="gijiroku-subtitle">会議録音を自動で文字起こし・議事録化</p>
    </div>
""", unsafe_allow_html=True)

# ===== ナビゲーション =====
current_page = st.session_state.get('page', 'upload')

# タブナビゲーションのスタイル
st.markdown("""
<style>
    div[data-testid="column"]:nth-of-type(1) button {
        border-radius: 8px 0 0 8px !important;
    }
    div[data-testid="column"]:nth-of-type(3) button {
        border-radius: 0 8px 8px 0 !important;
    }
    div[data-testid="column"] button {
        border-radius: 0 !important;
        border: none !important;
        background: white !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] button:hover {
        background: #f3f4f6 !important;
        color: #374151 !important;
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    upload_btn = st.button("議事録生成", use_container_width=True, key="nav_upload")
    if upload_btn:
        st.session_state.page = "upload"
with col2:
    history_btn = st.button("履歴", use_container_width=True, key="nav_history")
    if history_btn:
        st.session_state.page = "history"
with col3:
    stats_btn = st.button("統計", use_container_width=True, key="nav_stats")
    if stats_btn:
        st.session_state.page = "stats"

# アクティブなタブのスタイルを適用
active_tab_style = """
<style>
"""
if current_page == "upload":
    active_tab_style += """
    div[data-testid="column"]:nth-of-type(1) button {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        font-weight: 600 !important;
    }
    """
elif current_page == "history":
    active_tab_style += """
    div[data-testid="column"]:nth-of-type(2) button {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        font-weight: 600 !important;
    }
    """
elif current_page == "stats":
    active_tab_style += """
    div[data-testid="column"]:nth-of-type(3) button {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        font-weight: 600 !important;
    }
    """
active_tab_style += "</style>"
st.markdown(active_tab_style, unsafe_allow_html=True)

# ページ選択（ボタンクリック時は既に設定済み）
if 'page' not in st.session_state:
    st.session_state.page = "upload"

# ===== メインコンテンツ =====
if st.session_state.page == "upload":
    master = get_master_data()
    
    # 設定カード
    st.markdown('<div class="card"><div class="card-title">設定</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="setting-label">部署名</span>', unsafe_allow_html=True)
        dept_options = {d['name']: d['id'] for d in master['departments']}
        selected_dept = st.selectbox("", options=list(dept_options.keys()), label_visibility="collapsed", key="dept_select")
    
    with col2:
        st.markdown('<span class="setting-label">保存先フォルダ</span>', unsafe_allow_html=True)
        folder_options = {f['name']: f['id'] for f in master['folders']}
        selected_folder = st.selectbox("", options=list(folder_options.keys()), label_visibility="collapsed", key="folder_select")
    
    # 会議シーン/パターン（デフォルト値で追加）
    st.markdown('<span class="setting-label">会議シーン / パターン</span>', unsafe_allow_html=True)
    scene_options = ['定例会議', 'プロジェクト会議', '1on1', '全体会議', 'その他']
    selected_scene = st.selectbox("", options=scene_options, label_visibility="collapsed", key="scene_select")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # アップロードエリア
    st.markdown("""
    <div class="card">
        <div class="card-title">音声・動画ファイル</div>
    </div>
    <style>
        .uploadedFile {
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            background: white !important;
        }
        .uploadedFile:hover {
            border-color: #3b82f6 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "",
        type=['mp3', 'mp4', 'wav', 'm4a', 'mov'],
        label_visibility="collapsed",
        help="対応形式: MP3, WAV, M4A, MP4, MOV"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="setting-card">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">📄</span>
                <div>
                    <div style="font-weight: 600; color: #1a1a1a; margin-bottom: 0.25rem;">{uploaded_file.name}</div>
                    <div style="font-size: 0.875rem; color: #6b7280;">ファイルが選択されました</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            .stButton > button {
                background: #3b82f6 !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 0.875rem 2rem !important;
                font-size: 1rem !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 2px 4px rgba(59,130,246,0.2) !important;
            }
            .stButton > button:hover {
                background: #2563eb !important;
                box-shadow: 0 4px 8px rgba(59,130,246,0.3) !important;
                transform: translateY(-1px) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col2:
            if st.button("議事録生成", type="primary", use_container_width=True):
                with st.spinner("処理中..."):
                    result = upload_file_api(uploaded_file, dept_options[selected_dept], folder_options[selected_folder])
                    if result.get('success'):
                        st.markdown("""
                        <div class="setting-card" style="background: #dbeafe; border-color: #3b82f6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <span style="font-size: 1.5rem;">✅</span>
                                <div>
                                    <div style="font-weight: 600; color: #1e40af; margin-bottom: 0.25rem;">議事録の生成が完了しました</div>
                                    <div style="font-size: 0.875rem; color: #1e3a8a;">
                                        {link}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """.format(link=f'<a href="{result.get("doc_url")}" target="_blank" class="history-link">📄 議事録を表示</a>' if result.get('doc_url') else ''), unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="setting-card" style="background: #fee2e2; border-color: #ef4444;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <span style="font-size: 1.5rem;">❌</span>
                                <div>
                                    <div style="font-weight: 600; color: #991b1b; margin-bottom: 0.25rem;">エラーが発生しました</div>
                                    <div style="font-size: 0.875rem; color: #7f1d1d;">{result.get('error', '不明なエラー')}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

elif st.session_state.page == "history":
    history = get_history()
    
    if history:
        for item in history:
            status = item.get('status', '処理中')
            if status == '完了':
                status_class = "status-completed"
                status_text = "完了"
            elif 'エラー' in status or 'error' in status.lower():
                status_class = "status-error"
                status_text = "エラー"
            else:
                status_class = "status-processing"
                status_text = "処理中"
            
            file_name = item.get('file', 'N/A')
            date_str = item.get('date', 'N/A')
            department = item.get('department', 'N/A')
            folder = item.get('folder', 'N/A')
            doc_url = item.get('doc_url', '')
            
            # 日付をフォーマット
            try:
                if ' ' in date_str:
                    date_part, time_part = date_str.split(' ', 1)
                    formatted_date = f"{date_part} {time_part[:5]}"
                else:
                    formatted_date = date_str
            except:
                formatted_date = date_str
            
            st.markdown(f"""
            <div class="history-card">
                <div class="history-file-name">{file_name}</div>
                <div class="history-meta">
                    <span class="history-meta-item">🏢 {department}</span>
                    <span class="history-meta-item">📁 {folder}</span>
                    <span class="history-meta-item">📅 {formatted_date}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.75rem;">
                    <span class="status-badge {status_class}">{status_text}</span>
                    <div style="display: flex; gap: 1rem;">
                        {f'<a href="{doc_url}" target="_blank" class="history-link">表示</a>' if doc_url else ''}
                        {f'<a href="{doc_url}" target="_blank" class="history-link">ダウンロード</a>' if doc_url else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">履歴がありません</div>
            <div style="font-size: 0.875rem;">議事録を生成すると、ここに履歴が表示されます</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "stats":
    stats = get_statistics()
    
    # 統計カード
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">今月のアップロード</div>
            <div class="stat-value">{stats.get('this_month', 0)}</div>
            <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">ファイル</div>
            <div class="stat-change">+12% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">総文字起こし時間</div>
            <div class="stat-value">18.5</div>
            <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">時間</div>
            <div class="stat-change">+8% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">完了済み</div>
            <div class="stat-value">{stats.get('completed_count', stats.get('total_count', 0))}</div>
            <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">ファイル</div>
            <div class="stat-change">+15% 前月比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">使用中のフォルダー</div>
            <div class="stat-value">{stats.get('active_folders', 8)}</div>
            <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">フォルダー</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 部門別利用状況
    st.markdown('<div class="section-title">部門別利用状況</div>', unsafe_allow_html=True)
    
    dept_stats = stats.get('by_department', {})
    if dept_stats:
        df = pd.DataFrame([
            {'部門': dept, '利用回数': count}
            for dept, count in dept_stats.items()
        ])
        
        # 淡い青系で統一
        fig = px.bar(
            df,
            x='部門',
            y='利用回数',
            text='利用回数',
            labels={'利用回数': '利用回数', '部門': '部門'},
            color='利用回数',
            color_continuous_scale=['#e0f2fe', '#3b82f6']
        )
        fig.update_traces(
            textposition='outside',
            marker_line_color='#3b82f6',
            marker_line_width=1
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            margin=dict(l=0, r=0, t=20, b=0)
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        st.markdown('<div class="card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">データがありません</div>
            <div style="font-size: 0.875rem;">議事録を生成すると、統計データが表示されます</div>
        </div>
        """, unsafe_allow_html=True)

# フッター
st.markdown('<div class="footer">© 2026 GIJIROKU AI - DX推進プラットフォーム</div>', unsafe_allow_html=True)