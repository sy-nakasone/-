#!/bin/bash
# =====================================================
# 会議議事録自動生成アプリ デプロイスクリプト
# Webアプリ版（部署管理・利用履歴付き）
# =====================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   📝 会議議事録自動生成アプリ デプロイ                   ║${NC}"
echo -e "${GREEN}║      Webアプリ版 - 部署管理・利用履歴付き                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# ----- GCPプロジェクトID -----
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[1/5] GCPプロジェクトID${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -p "プロジェクトID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}エラー: プロジェクトIDは必須です${NC}"
    exit 1
fi

# ----- Gemini APIキー -----
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[2/5] Gemini APIキー${NC}"
echo "取得先: https://aistudio.google.com/apikey"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -p "APIキー: " GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}エラー: Gemini APIキーは必須です${NC}"
    exit 1
fi

# ----- スプレッドシートID -----
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[3/5] 管理用スプレッドシートID${NC}"
echo "※先にテンプレートからスプレッドシートを作成してください"
echo "スプレッドシートURLの /d/ と /edit の間の文字列"
echo "例: https://docs.google.com/spreadsheets/d/XXXXX/edit"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -p "スプレッドシートID: " SPREADSHEET_ID

# ----- Chatwork設定（任意） -----
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[4/5] Chatwork設定（任意・Enterでスキップ）${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -p "Chatwork APIトークン: " CHATWORK_API_TOKEN
read -p "Chatwork ルームID: " CHATWORK_ROOM_ID

# 設定確認
REGION="asia-northeast1"
API_SERVICE_NAME="meeting-minutes-api"
APP_SERVICE_NAME="meeting-minutes-app"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}設定内容の確認${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  プロジェクトID: $PROJECT_ID"
echo "  リージョン: $REGION"
echo "  スプレッドシートID: ${SPREADSHEET_ID:-未設定}"
echo "  Chatwork: ${CHATWORK_API_TOKEN:+設定あり}${CHATWORK_API_TOKEN:-なし}"
echo ""
read -p "この設定でデプロイしますか？ (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi

# ----- デプロイ開始 -----
echo ""
echo -e "${YELLOW}[5/5] デプロイ中...${NC}"

# GCPプロジェクトを設定
gcloud config set project $PROJECT_ID

# 必要なAPIを有効化
echo "APIを有効化中..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com drive.googleapis.com sheets.googleapis.com

# APIサーバーをデプロイ
echo ""
echo "APIサーバーをデプロイ中..."
# 一時的にDockerfile.apiをDockerfileにリネーム（--sourceはDockerfileを探すため）
HAD_ORIGINAL_DOCKERFILE=false
if [ -f "Dockerfile" ]; then
    mv Dockerfile Dockerfile.streamlit.backup
    HAD_ORIGINAL_DOCKERFILE=true
fi
cp Dockerfile.api Dockerfile

# エラーが発生してもDockerfileを元に戻すためのtrapを設定
cleanup_api_dockerfile() {
    rm -f Dockerfile
    if [ "$HAD_ORIGINAL_DOCKERFILE" = true ] && [ -f "Dockerfile.streamlit.backup" ]; then
        mv Dockerfile.streamlit.backup Dockerfile
    fi
}
trap cleanup_api_dockerfile EXIT

gcloud run deploy $API_SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --timeout 600 \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
    --set-env-vars "SPREADSHEET_ID=$SPREADSHEET_ID" \
    --set-env-vars "CHATWORK_API_TOKEN=$CHATWORK_API_TOKEN" \
    --set-env-vars "CHATWORK_ROOM_ID=$CHATWORK_ROOM_ID"

DEPLOY_API_RESULT=$?
cleanup_api_dockerfile
trap - EXIT

if [ $DEPLOY_API_RESULT -ne 0 ]; then
    echo -e "${RED}APIサーバーのデプロイに失敗しました${NC}"
    exit 1
fi

# IAMポリシーを設定（公開アクセスを許可）
echo "IAMポリシーを設定中..."
gcloud run services add-iam-policy-binding $API_SERVICE_NAME \
    --region $REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet || echo "IAMポリシー設定をスキップ（既に設定済みの可能性があります）"

# APIサーバーのURLを取得
API_URL=$(gcloud run services describe $API_SERVICE_NAME --region $REGION --format 'value(status.url)')

# Streamlitアプリをデプロイ
echo ""
echo "Webアプリをデプロイ中..."
# 一時的にDockerfile.streamlitをDockerfileにリネーム
HAD_ORIGINAL_DOCKERFILE=false
if [ -f "Dockerfile" ]; then
    mv Dockerfile Dockerfile.api.backup
    HAD_ORIGINAL_DOCKERFILE=true
fi
cp Dockerfile.streamlit Dockerfile

# エラーが発生してもDockerfileを元に戻すためのtrapを設定
cleanup_app_dockerfile() {
    rm -f Dockerfile
    if [ "$HAD_ORIGINAL_DOCKERFILE" = true ] && [ -f "Dockerfile.api.backup" ]; then
        mv Dockerfile.api.backup Dockerfile
    fi
}
trap cleanup_app_dockerfile EXIT

gcloud run deploy $APP_SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --timeout 300 \
    --set-env-vars "API_URL=$API_URL"

DEPLOY_APP_RESULT=$?
cleanup_app_dockerfile
trap - EXIT

if [ $DEPLOY_APP_RESULT -ne 0 ]; then
    echo -e "${RED}Webアプリのデプロイに失敗しました${NC}"
    exit 1
fi

# IAMポリシーを設定（公開アクセスを許可）
echo "IAMポリシーを設定中..."
gcloud run services add-iam-policy-binding $APP_SERVICE_NAME \
    --region $REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet || echo "IAMポリシー設定をスキップ（既に設定済みの可能性があります）"

# アプリのURLを取得
APP_URL=$(gcloud run services describe $APP_SERVICE_NAME --region $REGION --format 'value(status.url)')

# サービスアカウントを取得
SA_EMAIL=$(gcloud run services describe $API_SERVICE_NAME --region $REGION --format 'value(spec.template.spec.serviceAccountName)')
if [ -z "$SA_EMAIL" ]; then
    PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
    SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ デプロイ完了！                                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🌐 アプリURL:${NC}"
echo -e "${GREEN}   $APP_URL${NC}"
echo ""
echo -e "${CYAN}🔧 API URL:${NC}"
echo -e "   $API_URL"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  重要: 以下の設定を行ってください${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. 管理用スプレッドシートをサービスアカウントに共有:"
echo -e "   ${GREEN}$SA_EMAIL${NC}"
echo ""
echo "2. Googleドライブのフォルダもサービスアカウントに共有"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 上記URLにアクセスしてアプリを使用できます！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
