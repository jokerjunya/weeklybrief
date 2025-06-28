# 🚨 Netlify管理者サイト設定問題 - トラブルシューティング

## 📊 **現在の問題**

```
Custom publish path detected. Proceeding with the specified path: 'viewer-app'
No changes detected in base directory. Returning early from build.
```

**❌ 問題**: 管理者サイトが閲覧者サイトの設定でデプロイされている

---

## 🛠️ **Netlify設定の確認・修正手順**

### **Step 1: Netlify管理者サイトの設定確認**

1. [Netlifyダッシュボード](https://app.netlify.com) にログイン
2. **管理者サイト** を選択（admin-weeklyreport.netlify.app）
3. **Site settings** → **Build & deploy** → **Build settings** を確認

### **Step 2: 正しいビルド設定**

```yaml
# 管理者サイトの正しい設定
Base directory: admin-app
Build command: echo 'Admin site ready for deployment'
Publish directory: .
Functions directory: netlify/functions
```

### **Step 3: 設定が間違っている場合**

#### **間違った設定例**:
```yaml
❌ Base directory: (空白) または viewer-app
❌ Publish directory: viewer-app
❌ Functions directory: (空白)
```

#### **修正方法**:
1. **Site settings** → **Build & deploy** → **Build settings**
2. **Edit settings** をクリック
3. 以下に修正:
   - **Base directory**: `admin-app`
   - **Build command**: `echo 'Admin site ready'`
   - **Publish directory**: `.`
   - **Functions directory**: `netlify/functions`
4. **Save** をクリック
5. **Deploy** → **Trigger deploy** → **Deploy site**

---

## 🔍 **設定確認チェックリスト**

### **管理者サイト (admin-weeklyreport.netlify.app)**
- [ ] Base directory: `admin-app`
- [ ] Build command: `echo 'Admin site ready'`
- [ ] Publish directory: `.`
- [ ] Functions directory: `netlify/functions`
- [ ] Branch: `main`

### **閲覧者サイト (weeklyreport.netlify.app)**
- [ ] Base directory: `viewer-app`
- [ ] Build command: `echo 'Viewer site ready'`
- [ ] Publish directory: `.`
- [ ] Functions directory: (空白)
- [ ] Branch: `main`

---

## 📋 **デプロイ後の確認項目**

### **管理者サイト機能確認**
1. **JavaScript読み込み**:
   - [ ] F12 → Console で `✅ Environment configuration loaded successfully`
   - [ ] `✅ Admin App initialized successfully`
   - [ ] エラーメッセージなし

2. **ナビゲーション機能**:
   - [ ] サイドバーの各項目クリックでセクション切り替え
   - [ ] ページタイトルが変更される
   - [ ] アクティブ項目のハイライト移動

3. **ダークモード機能**:
   - [ ] 🌙/☀️ ボタンでテーマ切り替え
   - [ ] 設定がLocalStorageに保存される

4. **5つのセクション表示**:
   - [ ] ダッシュボード: 3つのカード
   - [ ] 売上データ: アップロードエリア
   - [ ] ニュース管理: DeepResearchボタン
   - [ ] イベント編集: イベントフォーム
   - [ ] レポート生成: 生成ボタン

---

## 🚀 **緊急対処法**

### **方法1: Netlify設定リセット**
1. 管理者サイトの **Site settings** → **General**
2. **Change site name** で一時的に名前変更
3. **Build settings** を上記の正しい設定に変更
4. **Trigger deploy** で強制再デプロイ

### **方法2: 新しいサイト作成**
現在のサイトに問題がある場合：
1. Netlify で **New site from Git**
2. 同じリポジトリを選択
3. **管理者サイト用の正しい設定**を最初から入力
4. 古いサイトを削除

---

## 📞 **サポート情報**

- **Netlify ドキュメント**: https://docs.netlify.com/configure-builds/overview/
- **Base directory 設定**: https://docs.netlify.com/configure-builds/overview/#base-directory
- **Functions 設定**: https://docs.netlify.com/functions/overview/

---

**🎯 目標**: 管理者サイトが正しい設定でデプロイされ、全機能が動作すること 