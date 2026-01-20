#!/bin/bash
# Cloud Run用APIサーバー起動スクリプト

# ポート番号を取得（デフォルトは8080）
PORT=${PORT:-8080}

# デバッグ情報を出力
echo "Starting API server on port ${PORT}"

# gunicornでAPIサーバーを起動
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 1 \
    --threads 8 \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    api:app
