# GitBashでのデプロイ手順

## 前提条件

1. Google Cloud SDK (gcloud) がインストールされていること
2. GitBashがインストールされていること
3. GCPプロジェクトが作成済みであること

## デプロイ手順

### 1. GitBashを開く

GitBashを起動します。

### 2. プロジェクトディレクトリに移動

```bash
cd "/c/Users/CENTRIC Ikeshita/Desktop/--cursor-ai-meeting-minutes-summarization-bef7/app"
```

### 3. デプロイスクリプトに実行権限を付与（初回のみ）

```bash
chmod +x deploy.sh
```

### 4. デプロイスクリプトを実行

```bash
./deploy.sh
```

## デプロイ時の入力項目

スクリプトを実行すると、以下の情報を順番に入力するよう求められます：

1. **GCPプロジェクトID**
   - 例: `meeting-minutes-483607`

2. **Gemini APIキー**
   - 取得先: https://aistudio.google.com/apikey

3. **管理用スプレッドシートID**
   - スプレッドシートURLの `/d/` と `/edit` の間の文字列
   - 例: `1itcfighiIO4cJnBITtl25nuP1QiTES_38eKbn3Q-WL4`

4. **Chatwork設定（任意）**
   - APIトークン（Enterでスキップ可能）
   - ルームID（Enterでスキップ可能）

5. **確認**
   - `y` を入力してデプロイを開始

## ワンライナーコマンド（上級者向け）

環境変数を事前に設定して実行する場合：

```bash
cd "/c/Users/CENTRIC Ikeshita/Desktop/--cursor-ai-meeting-minutes-summarization-bef7/app" && \
export PROJECT_ID="your-project-id" && \
export GEMINI_API_KEY="your-api-key" && \
export SPREADSHEET_ID="your-spreadsheet-id" && \
chmod +x deploy.sh && \
./deploy.sh
```

## トラブルシューティング

### エラー: `gcloud: command not found`

Google Cloud SDKがインストールされていないか、PATHが通っていません。

**解決方法:**
1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)をインストール
2. GitBashを再起動

### エラー: `Permission denied`

デプロイスクリプトに実行権限がありません。

**解決方法:**
```bash
chmod +x deploy.sh
```

### エラー: `Reauthentication required`

GCPの認証が必要です。

**解決方法:**
```bash
gcloud auth login
```

### エラー: Dockerfileが見つからない

`app`ディレクトリに移動してから実行してください。

**解決方法:**
```bash
cd app
./deploy.sh
```

## デプロイ後の確認事項

デプロイが完了すると、以下の情報が表示されます：

1. **アプリURL** - WebアプリにアクセスするURL
2. **API URL** - APIサーバーのURL
3. **サービスアカウント** - スプレッドシートとGoogleドライブフォルダに共有する必要があるメールアドレス

## 次のステップ

1. 管理用スプレッドシートをサービスアカウントに共有
2. Googleドライブのフォルダをサービスアカウントに共有
3. アプリURLにアクセスして動作確認

## 参考

- [Google Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Streamlit ドキュメント](https://docs.streamlit.io/)
