import streamlit as st
import os
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="Meeting Minutes Summarizer", page_icon="📝")
    
    st.title("📝 会議議事録生成AI")
    st.write("音声ファイルをアップロードして、文字起こしと要約を行います。")

    # API Key Input (Optional if set in env)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("OpenAI API Keyを入力してください", type="password")
    
    if not api_key:
        st.warning("API Keyが必要です。")
        return

    # File Upload
    uploaded_file = st.file_uploader("音声ファイルをアップロード (mp3, m4a, wav, etc.)", type=["mp3", "m4a", "wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("議事録を作成する"):
            with st.spinner("音声を処理中..."):
                try:
                    # Save uploaded file temporarily
                    with NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name

                    # Placeholder for Transcription
                    st.info("文字起こしを開始します...")
                    transcript_text = transcribe_audio(api_key, temp_file_path)
                    st.success("文字起こし完了!")
                    with st.expander("文字起こし結果を見る"):
                        st.text_area("Transcript", transcript_text, height=200)

                    # Placeholder for Summarization
                    st.info("要約を作成中...")
                    summary_text = summarize_text(api_key, transcript_text)
                    st.success("要約完了!")
                    
                    st.subheader("📋 議事録要約")
                    st.markdown(summary_text)

                    # Cleanup
                    os.remove(temp_file_path)

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

def transcribe_audio(api_key, file_path):
    # TODO: Implement OpenAI Whisper API call
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text

def summarize_text(api_key, text):
    # TODO: Implement OpenAI ChatCompletion call
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたは優秀な書記です。提供された会議の文字起こしテキストをもとに、簡潔で分かりやすい議事録を作成してください。以下のフォーマットに従ってください。\n\n# 会議議事録\n## 議題\n## 決定事項\n## 次回のアクション\n## 詳細メモ"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    main()
