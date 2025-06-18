# Teams Chat ID 取得ガイド

## 概要
Power AutomateからTeamsのプライベートチャットにメッセージを送信するために、Junyaさんのチャット識別子が必要です。

## 方法1: Power Automate内での取得（推奨）

### 手順
1. **Power Automate**にアクセス
2. **新しいフロー**を作成（テスト用）
3. **トリガー**として「手動でフローをトリガーする」を選択
4. **アクション**を追加：
   - **Microsoft Teams** → **チャットまたはチャネルでメッセージを投稿する**
5. **チャット**を選択
6. **チャット**のドロップダウンで**Junya**との個人チャットを選択
7. **動的なコンテンツ**で**チャット ID**をメモする

### 確認方法
- フローの実行履歴で、送信先のチャットIDを確認可能
- 通常、個人チャットのIDは `19:` で始まる長い文字列

## 方法2: Teams Web版での取得

### 手順
1. **Teams Web版**（teams.microsoft.com）にアクセス
2. **Junya**との個人チャットを開く
3. **ブラウザのURL**を確認
4. URLに含まれる長い識別子部分をコピー

### URL例
```
https://teams.microsoft.com/l/chat/0/0?users=junya@company.com
```

## 方法3: Microsoft Graph APIを使用（上級者向け）

### 必要なもの
- Microsoft Graph APIへのアクセス権限
- PowerShellまたはHTTPクライアント

### 手順
```powershell
# Microsoft Graph PowerShell使用例
Connect-MgGraph -Scopes "Chat.Read"
Get-MgChat | Where-Object {$_.ChatType -eq "OneOnOne"}
```

## 方法4: Power Automateテストフロー作成（最も確実）

以下のテストフローを作成して、Chat IDを取得することをお勧めします：

### テストフロー手順
1. **Power Automate**で新しいフローを作成
2. **手動トリガー**を設定
3. **Teams: チャットまたはチャネルでメッセージを投稿**アクションを追加
4. **チャット**を選択し、Junyaとの個人チャットを選択
5. **メッセージ**に「テスト」と入力
6. **保存して実行**
7. **実行履歴**でチャットIDを確認

### 取得できるChat IDの形式
```
19:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx@unq.gbl.spaces
```

## 設定への反映

取得したChat IDを `config/settings.json` の以下の部分に設定してください：

```json
"teams": {
  "chat_id": "ここに取得したChat IDを入力"
}
```

## トラブルシューティング

### よくある問題
1. **チャットが表示されない**
   - Junyaさんとの個人チャットが存在するか確認
   - Teams上でメッセージのやり取りがあるか確認

2. **権限エラー**
   - Power AutomateでTeamsコネクタの権限を確認
   - 必要に応じて再認証

3. **Chat IDが無効**
   - IDが正しくコピーされているか確認
   - 特殊文字や改行が含まれていないか確認

## サンプルテストフロー

実際のChat ID取得用のサンプルフローを作成しますか？その場合は以下の情報が必要です：
- Power Automateへのアクセス権限
- Microsoft Teamsへのアクセス権限
- Junyaさんとの既存の個人チャット 