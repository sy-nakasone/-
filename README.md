# Meeting Minutes Summarizer

AIを使って会議の音声を文字起こしし、要約するアプリケーションです。

## セットアップ

1. 必要なライブラリをインストールします:
   ```bash
   pip install -r requirements.txt
   ```

2. アプリケーションを実行します:
   ```bash
   streamlit run app.py
   ```

## 機能

- 音声ファイル (mp3, wav, m4a) のアップロード
- OpenAI Whisper API を使用した高精度な文字起こし
- GPT-4o を使用した議事録要約

## 注意事項

- OpenAI API Keyが必要です。`.env` ファイルに `OPENAI_API_KEY=your_key` と記述するか、画面上で入力してください。
