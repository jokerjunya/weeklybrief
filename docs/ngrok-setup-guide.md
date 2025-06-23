# ngrok設定ガイド - 週次ビジネスレポートシステム

## 概要

このガイドでは、週次ビジネスレポートシステムをngrokを使用して外部に安全に公開する方法を説明します。セキュリティのため、Basic認証を必須としています。

## 🔐 セキュリティ要件

- **Basic認証必須**: 外部公開時は必ずBasic認証を設定
- **強力なパスワード**: 推測困難なパスワードを使用
- **環境変数管理**: 認証情報は環境変数で管理（.envファイル）

## 📋 事前準備

### 1. ngrokのインストール

#### macOS（Homebrew使用）
```bash
brew install ngrok/ngrok/ngrok
```

#### その他のOS
[ngrok公式サイト](https://ngrok.com/download)からダウンロードしてインストール

### 2. ngrokアカウントの設定（オプション）
```bash
# ngrokアカウントがある場合
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## ⚙️ 設定手順

### 1. 環境変数ファイルの作成
```bash
# プロジェクトルートで実行
cp .env.example .env
```

### 2. Basic認証情報の設定
`.env`ファイルを編集：
```bash
# ngrok Basic認証設定
NGROK_AUTH_USER=your_secure_username
NGROK_AUTH_PASS=your_very_secure_password_123!
```

**⚠️ パスワード要件:**
- 最低8文字以上
- 英数字・記号を組み合わせ
- 推測困難な文字列

### 3. Webサーバーの起動
別のターミナルで：
```bash
cd web
python -m http.server 8000
```

### 4. ngrokの起動

#### 方法A: 自動スクリプト（推奨）
```bash
./scripts/start-ngrok.sh
```

#### 方法B: 手動実行
```bash
# 環境変数を読み込み
source .env

# ngrokを起動
ngrok http --basic-auth="$NGROK_AUTH_USER:$NGROK_AUTH_PASS" 8000
```

## 🌐 アクセス方法

1. **ngrok起動後の出力を確認**
   ```
   Session Status                online
   Account                       your_account (Plan: Free)
   Version                       3.x.x
   Region                        Japan (jp)
   Latency                       -
   Web Interface                 http://127.0.0.1:4040
   Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
   ```

2. **HTTPS URLにアクセス**
   - 上記例では `https://abc123.ngrok.io`
   - HTTPSを必ず使用（HTTPは非推奨）

3. **Basic認証を入力**
   - ユーザー名: `.env`で設定した`NGROK_AUTH_USER`
   - パスワード: `.env`で設定した`NGROK_AUTH_PASS`

4. **レポートページが表示**
   - 認証成功後、週次ビジネスレポートが表示されます

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. "Address already in use" エラー
```bash
# 使用中のポートを確認
lsof -i :8000

# プロセスを終了
kill -9 PID
```

#### 2. Basic認証が表示されない
- ngrokコマンドに`--basic-auth`オプションが含まれているか確認
- 環境変数が正しく設定されているか確認
```bash
echo $NGROK_AUTH_USER
echo $NGROK_AUTH_PASS
```

#### 3. 環境変数が読み込まれない
```bash
# .envファイルの存在確認
ls -la .env

# .envファイルの内容確認
cat .env

# 手動で環境変数を設定
export NGROK_AUTH_USER="your_username"
export NGROK_AUTH_PASS="your_password"
```

#### 4. ngrokが見つからない
```bash
# ngrokのインストール確認
which ngrok
ngrok version

# PATHの確認
echo $PATH
```

## 📊 監視・ログ

### ngrok Web Interface
- URL: http://127.0.0.1:4040
- リアルタイムでリクエスト・レスポンスを監視可能
- デバッグに有用

### ログの確認
```bash
# Webサーバーのログ
# python -m http.serverの出力を確認

# ngrokのログ
# ngrokコマンドの出力を確認
```

## 🔒 セキュリティのベストプラクティス

1. **強力な認証情報**
   - ユーザー名: 推測困難な文字列
   - パスワード: 複雑で長いパスワード

2. **環境変数の管理**
   - `.env`ファイルはGitにコミットしない
   - 本番環境では専用の認証情報を使用

3. **アクセス制限**
   - 必要な期間のみ公開
   - 不要になったら即座に停止

4. **監視**
   - 不正アクセスの監視
   - 定期的な認証情報の変更

## 📝 運用ガイド

### 定期メンテナンス
- 月1回: 認証情報の変更
- 週1回: アクセスログの確認
- 使用後: ngrokセッションの停止

### 緊急時の対応
```bash
# ngrokを即座に停止
Ctrl+C

# 全てのPythonプロセスを停止
pkill -f "python -m http.server"
```

## 🔗 関連リンク

- [ngrok公式ドキュメント](https://ngrok.com/docs)
- [Basic認証について](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication)
- [プロジェクトREADME](../README.md)

---

**更新日**: 2025年6月23日  
**作成者**: Junya (@jokerjunya) 