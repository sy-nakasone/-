"""
会議議事録自動生成 - バックエンドAPI（共有ドライブ対応版）
"""

import os
import tempfile
import logging
from datetime import datetime, timedelta
from typing import Optional
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.generativeai as genai
import requests

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ===== 環境変数から設定を読み込み =====
CONFIG = {
    'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY', ''),
    'SPREADSHEET_ID': os.environ.get('SPREADSHEET_ID', ''),
    'CHATWORK_API_TOKEN': os.environ.get('CHATWORK_API_TOKEN', ''),
    'CHATWORK_ROOM_ID': os.environ.get('CHATWORK_ROOM_ID', ''),
}

# Gemini設定
if CONFIG['GEMINI_API_KEY']:
    genai.configure(api_key=CONFIG['GEMINI_API_KEY'])

# 対応音声フォーマット
SUPPORTED_FORMATS = ['mp3', 'mp4', 'wav', 'm4a', 'webm', 'ogg', 'flac', 'mpeg']


def get_credentials():
    """認証情報を取得"""
    credentials, _ = default(scopes=[
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ])
    return credentials


def get_drive_service():
    """Google Drive APIサービス"""
    return build('drive', 'v3', credentials=get_credentials())


def get_sheets_service():
    """Google Sheets APIサービス"""
    return build('sheets', 'v4', credentials=get_credentials())


# ===== スプレッドシート操作 =====

def get_master_data_from_sheet():
    """スプレッドシートからマスタデータを取得"""
    if not CONFIG['SPREADSHEET_ID']:
        return get_default_master_data()
    
    try:
        sheets = get_sheets_service()
        
        # 部署マスタ取得
        dept_result = sheets.spreadsheets().values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range='部署マスタ!A2:B100'
        ).execute()
        departments = [
            {'id': row[0], 'name': row[1]}
            for row in dept_result.get('values', [])
            if len(row) >= 2
        ]
        
        # フォルダマスタ取得
        folder_result = sheets.spreadsheets().values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range='フォルダマスタ!A2:C100'
        ).execute()
        folders = [
            {'id': row[0], 'name': row[1], 'drive_folder_id': row[2] if len(row) > 2 else ''}
            for row in folder_result.get('values', [])
            if len(row) >= 2
        ]
        
        return {'departments': departments, 'folders': folders}
    
    except Exception as e:
        logger.error(f"マスタデータ取得エラー: {e}")
        return get_default_master_data()


def get_default_master_data():
    """デフォルトのマスタデータ"""
    return {
        'departments': [
            {'id': 'sales', 'name': '営業部'},
            {'id': 'dev', 'name': '開発部'},
            {'id': 'hr', 'name': '人事部'},
            {'id': 'marketing', 'name': 'マーケティング部'},
            {'id': 'finance', 'name': '経理部'},
        ],
        'folders': [
            {'id': 'regular', 'name': '定例会議', 'drive_folder_id': ''},
            {'id': 'project', 'name': 'プロジェクト会議', 'drive_folder_id': ''},
            {'id': 'other', 'name': 'その他', 'drive_folder_id': ''},
        ]
    }


def add_history_record(department: str, folder: str, file_name: str, 
                       status: str, doc_url: str = ''):
    """履歴をスプレッドシートに追加"""
    if not CONFIG['SPREADSHEET_ID']:
        logger.info("SPREADSHEET_ID未設定のため履歴記録をスキップ")
        return
    
    try:
        sheets = get_sheets_service()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = [[timestamp, department, folder, file_name, status, doc_url]]
        
        sheets.spreadsheets().values().append(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range='利用履歴!A:F',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
        
        logger.info(f"履歴を記録しました: {department} / {folder} / {file_name}")
    
    except Exception as e:
        logger.error(f"履歴記録エラー: {e}")


def get_history_from_sheet(limit: int = 100):
    """スプレッドシートから履歴を取得"""
    if not CONFIG['SPREADSHEET_ID']:
        return []
    
    try:
        sheets = get_sheets_service()
        
        result = sheets.spreadsheets().values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range=f'利用履歴!A2:F{limit + 1}'
        ).execute()
        
        rows = result.get('values', [])
        history = []
        
        for row in reversed(rows):  # 新しい順
            if len(row) >= 5:
                history.append({
                    'date': row[0],
                    'department': row[1],
                    'folder': row[2],
                    'file': row[3],
                    'status': row[4],
                    'doc_url': row[5] if len(row) > 5 else ''
                })
        
        return history[:limit]
    
    except Exception as e:
        logger.error(f"履歴取得エラー: {e}")
        return []


def get_statistics_from_sheet():
    """スプレッドシートから統計を計算"""
    if not CONFIG['SPREADSHEET_ID']:
        return {
            'total_count': 0,
            'this_month': 0,
            'completed_count': 0,
            'by_department': {},
            'active_folders': 0
        }
    
    try:
        sheets = get_sheets_service()
        
        result = sheets.spreadsheets().values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range='利用履歴!A2:F10000'
        ).execute()
        
        rows = result.get('values', [])
        
        total_count = len(rows)
        this_month = 0
        completed_count = 0
        by_department = {}
        active_folders = set()
        
        current_month = datetime.now().strftime('%Y-%m')
        
        for row in rows:
            if len(row) >= 2:
                # 今月のカウント
                if row[0].startswith(current_month):
                    this_month += 1
                
                # 完了済みカウント
                if len(row) >= 5 and row[4] == '完了':
                    completed_count += 1
                
                # 部署別カウント
                dept = row[1]
                by_department[dept] = by_department.get(dept, 0) + 1
                
                # 使用中のフォルダー
                if len(row) >= 3 and row[2]:
                    active_folders.add(row[2])
        
        return {
            'total_count': total_count,
            'this_month': this_month,
            'completed_count': completed_count,
            'by_department': by_department,
            'active_folders': len(active_folders)
        }
    
    except Exception as e:
        logger.error(f"統計取得エラー: {e}")
        return {
            'total_count': 0,
            'this_month': 0,
            'completed_count': 0,
            'by_department': {},
            'active_folders': 0
        }


# ===== Gemini処理 =====

def transcribe_with_gemini(file_path: str, file_name: str) -> str:
    """Gemini APIで音声を文字起こし"""
    ext = file_name.split('.')[-1].lower()
    mime_types = {
        'mp3': 'audio/mp3', 'mp4': 'audio/mp4', 'wav': 'audio/wav',
        'm4a': 'audio/mp4', 'webm': 'audio/webm', 'ogg': 'audio/ogg',
        'flac': 'audio/flac', 'mpeg': 'audio/mpeg'
    }
    mime_type = mime_types.get(ext, 'audio/mp3')
    
    logger.info(f"Geminiにアップロード中: {file_name}")
    uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = """この音声ファイルの内容を正確に文字起こししてください。

以下のルールに従ってください：
- 話者が複数いる場合は、可能な限り話者を区別してください
- 相槌や言い淀みは省略して、内容を読みやすくしてください
- 専門用語や固有名詞は正確に記載してください
- 日本語で出力してください"""

    response = model.generate_content([prompt, uploaded_file])
    
    try:
        genai.delete_file(uploaded_file.name)
    except:
        pass
    
    return response.text


def summarize_with_gemini(transcript: str) -> str:
    """Gemini APIで議事録を要約"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""以下の会議の文字起こしを読み、構造化された議事録を作成してください。

以下の形式で出力してください：

## 📋 会議概要
- 会議の主な目的や議題を簡潔に記載

## 🎯 主要な議論ポイント
- 議論された主要なトピックを箇条書きで

## 📌 決定事項
- 会議で決定された事項を明確に記載

## ✅ アクションアイテム
- 誰が何をいつまでに行うか（可能な限り特定）

## 📝 その他のメモ
- その他の重要な情報や補足事項

---
文字起こし内容：
{transcript}"""
    
    response = model.generate_content(prompt)
    return response.text


# ===== Googleドライブ =====

def upload_to_drive(file_path: str, file_name: str, folder_id: str) -> dict:
    """ファイルをGoogleドライブにアップロード（共有ドライブ対応）"""
    drive = get_drive_service()
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id] if folder_id else []
    }
    
    media = MediaFileUpload(file_path)
    # supportsAllDrives=True を追加
    file = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink',
        supportsAllDrives=True
    ).execute()
    
    return file


def create_doc_in_drive(title: str, content: str, folder_id: str) -> dict:
    """Google Docsを作成（共有ドライブ対応）"""
    drive = get_drive_service()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        tmp_path = f.name
    
    try:
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id] if folder_id else []
        }
        
        media = MediaFileUpload(tmp_path, mimetype='text/plain')
        # supportsAllDrives=True を追加
        file = drive.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink',
            supportsAllDrives=True
        ).execute()
        
        return file
    finally:
        os.unlink(tmp_path)


# ===== Chatwork通知 =====

def notify_chatwork(doc_info: dict, department: str, folder: str, file_name: str):
    """Chatworkに通知"""
    if not CONFIG['CHATWORK_API_TOKEN'] or not CONFIG['CHATWORK_ROOM_ID']:
        return
    
    message = f"""[info][title]📝 会議議事録が作成されました[/title]
🏢 部署: {department}
📁 フォルダ: {folder}
🎤 元ファイル: {file_name}
📄 議事録: {doc_info.get('name', '')}
🔗 URL: {doc_info.get('webViewLink', '')}
⏰ 処理日時: {datetime.now().strftime('%Y/%m/%d %H:%M')}
[/info]"""
    
    url = f"https://api.chatwork.com/v2/rooms/{CONFIG['CHATWORK_ROOM_ID']}/messages"
    headers = {'X-ChatWorkToken': CONFIG['CHATWORK_API_TOKEN']}
    
    try:
        requests.post(url, headers=headers, data={'body': message})
        logger.info("Chatwork通知を送信しました")
    except Exception as e:
        logger.error(f"Chatwork通知エラー: {e}")


# ===== APIエンドポイント =====

@app.route('/master', methods=['GET'])
def get_master():
    """マスタデータを取得"""
    data = get_master_data_from_sheet()
    return jsonify(data)


@app.route('/history', methods=['GET'])
def get_history():
    """利用履歴を取得"""
    limit = request.args.get('limit', 100, type=int)
    history = get_history_from_sheet(limit)
    return jsonify({'history': history})


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """利用統計を取得"""
    stats = get_statistics_from_sheet()
    return jsonify(stats)


@app.route('/upload', methods=['POST'])
def upload_and_process():
    """ファイルをアップロードして処理"""
    try:
        # ファイルと情報を取得
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ファイルがありません'}), 400
        
        file = request.files['file']
        department = request.form.get('department', '')
        folder = request.form.get('folder', '')
        
        if not file.filename:
            return jsonify({'success': False, 'error': 'ファイル名がありません'}), 400
        
        # ファイル拡張子チェック
        ext = file.filename.split('.')[-1].lower()
        if ext not in SUPPORTED_FORMATS:
            return jsonify({'success': False, 'error': f'非対応のファイル形式です: {ext}'}), 400
        
        logger.info(f"処理開始: {file.filename} (部署: {department}, フォルダ: {folder})")
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # マスタからフォルダ情報を取得
            master = get_master_data_from_sheet()
            folder_info = next((f for f in master['folders'] if f['id'] == folder), None)
            folder_name = folder_info['name'] if folder_info else folder
            drive_folder_id = folder_info.get('drive_folder_id', '') if folder_info else ''
            
            dept_info = next((d for d in master['departments'] if d['id'] == department), None)
            dept_name = dept_info['name'] if dept_info else department
            
            # 音声をGoogleドライブにアップロード
            if drive_folder_id:
                logger.info("音声ファイルをGoogleドライブにアップロード中...")
                upload_to_drive(tmp_path, file.filename, drive_folder_id)
            
            # Geminiで文字起こし
            logger.info("Geminiで文字起こし中...")
            transcript = transcribe_with_gemini(tmp_path, file.filename)
            logger.info(f"文字起こし完了: {len(transcript)} 文字")
            
            # Geminiで要約
            logger.info("Geminiで要約中...")
            summary = summarize_with_gemini(transcript)
            logger.info("要約完了")
            
            # Google Docs作成
            doc_title = f"【議事録】{file.filename.rsplit('.', 1)[0]}_{datetime.now().strftime('%Y-%m-%d')}"
            doc_content = f"""📝 会議議事録

作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
部署: {dept_name}
フォルダ: {folder_name}

{'=' * 50}

{summary}

{'=' * 50}

📎 文字起こし（原文）

{transcript}
"""
            
            logger.info("Google Docs作成中...")
            doc_info = create_doc_in_drive(doc_title, doc_content, drive_folder_id)
            logger.info(f"議事録作成完了: {doc_info.get('webViewLink', '')}")
            
            # 履歴を記録
            add_history_record(
                department=dept_name,
                folder=folder_name,
                file_name=file.filename,
                status='完了',
                doc_url=doc_info.get('webViewLink', '')
            )
            
            # Chatwork通知
            notify_chatwork(doc_info, dept_name, folder_name, file.filename)
            
            return jsonify({
                'success': True,
                'doc_name': doc_info.get('name', ''),
                'doc_url': doc_info.get('webViewLink', ''),
                'message': '議事録の生成が完了しました'
            })
            
        finally:
            # 一時ファイル削除
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"処理エラー: {e}")
        
        # エラーも履歴に記録
        add_history_record(
            department=request.form.get('department', ''),
            folder=request.form.get('folder', ''),
            file_name=request.files.get('file', {}).filename if 'file' in request.files else '',
            status=f'エラー: {str(e)[:50]}',
            doc_url=''
        )
        
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'config': {
            'gemini': bool(CONFIG['GEMINI_API_KEY']),
            'spreadsheet': bool(CONFIG['SPREADSHEET_ID']),
            'chatwork': bool(CONFIG['CHATWORK_API_TOKEN'])
        }
    })


@app.route('/', methods=['GET'])
def index():
    """ルート"""
    return jsonify({
        'service': '会議議事録自動生成API',
        'version': '2.1',
        'endpoints': {
            '/upload': 'POST - ファイルアップロード・処理',
            '/master': 'GET - マスタデータ取得',
            '/history': 'GET - 利用履歴取得',
            '/statistics': 'GET - 利用統計取得',
            '/health': 'GET - ヘルスチェック'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)