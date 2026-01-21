#!/bin/bash
# Cloud Run用APIサーバー起動スクリプト

# ポート番号を取得（Cloud Runが自動設定するPORT環境変数を使用）
PORT=${PORT:-8080}

# デバッグ情報を出力
echo "=========================================="
echo "Starting API server"
echo "PORT environment variable: ${PORT}"
echo "Binding to: 0.0.0.0:${PORT}"
echo "=========================================="

# gunicornでAPIサーバーを起動
# execを使用してプロセスを置き換える
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 1 \
    --threads 8 \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    api:app
