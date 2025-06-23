#!/bin/bash

# ngrok Basic認証付きでWebサーバーを公開するスクリプト
# 週次ビジネスレポート自動生成システム

set -e

# 色付きメッセージ用の関数
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_info "週次ビジネスレポートシステム - ngrok起動スクリプト"
print_info "プロジェクトルート: $PROJECT_ROOT"

# .envファイルの読み込み
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    print_info ".envファイルを読み込み中..."
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    print_success ".envファイルを読み込みました"
else
    print_warning ".envファイルが見つかりません"
    print_info ".env.exampleを参考に.envファイルを作成してください"
    
    # 環境変数が設定されているかチェック
    if [ -z "$NGROK_AUTH_USER" ] || [ -z "$NGROK_AUTH_PASS" ]; then
        print_error "NGROK_AUTH_USERとNGROK_AUTH_PASSの環境変数が設定されていません"
        print_info "以下のコマンドで設定するか、.envファイルを作成してください:"
        echo ""
        echo "export NGROK_AUTH_USER=\"your_username\""
        echo "export NGROK_AUTH_PASS=\"your_password\""
        echo ""
        exit 1
    fi
fi

# ngrokがインストールされているかチェック
if ! command -v ngrok &> /dev/null; then
    print_error "ngrokがインストールされていません"
    print_info "以下のコマンドでインストールしてください:"
    echo ""
    echo "# Homebrewを使用する場合:"
    echo "brew install ngrok/ngrok/ngrok"
    echo ""
    echo "# または公式サイトからダウンロード:"
    echo "https://ngrok.com/download"
    echo ""
    exit 1
fi

# ポート番号の設定（デフォルト: 8000）
PORT=${1:-8000}
print_info "使用ポート: $PORT"

# Basic認証の設定確認
if [ -z "$NGROK_AUTH_USER" ] || [ -z "$NGROK_AUTH_PASS" ]; then
    print_error "Basic認証の設定が不完全です"
    print_info "NGROK_AUTH_USERとNGROK_AUTH_PASSを設定してください"
    exit 1
fi

print_info "Basic認証設定:"
print_info "  ユーザー名: $NGROK_AUTH_USER"
print_info "  パスワード: [非表示]"

# Webサーバーが起動しているかチェック
print_info "ポート$PORTでのWebサーバー起動状況をチェック中..."
if ! curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    print_warning "ポート$PORTでWebサーバーが起動していません"
    print_info "別のターミナルで以下のコマンドを実行してください:"
    echo ""
    echo "cd $PROJECT_ROOT/web"
    echo "python -m http.server $PORT"
    echo ""
    read -p "Webサーバーを起動したら、Enterキーを押してください..."
fi

# ngrok起動
print_info "ngrokを起動中..."
print_info "コマンド: ngrok http --basic-auth=\"$NGROK_AUTH_USER:***\" $PORT"

# ngrokを起動（Basic認証付き）
ngrok http --basic-auth="$NGROK_AUTH_USER:$NGROK_AUTH_PASS" $PORT 