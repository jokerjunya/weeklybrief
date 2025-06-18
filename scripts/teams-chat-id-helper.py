#!/usr/bin/env python3
"""
Teams Chat ID取得ヘルパー
Power Automateでのテストフロー作成をガイド
"""

def print_teams_guide():
    """Teams Chat ID取得ガイドを表示"""
    
    print("🔍 Teams Chat ID 取得ガイド")
    print("=" * 50)
    
    print("\n📋 **最も簡単な方法（推奨）**")
    print("1. Power Automate (make.powerautomate.com) にアクセス")
    print("2. 「新しいフロー」→「手動でトリガーされるクラウドフロー」")
    print("3. フロー名: 「Chat ID取得テスト」")
    print("4. 「新しいステップ」→「Microsoft Teams」")
    print("5. 「チャットまたはチャネルでメッセージを投稿」を選択")
    print("6. 設定:")
    print("   - 投稿者: フロー ボット")
    print("   - 投稿先: チャット")
    print("   - 受信者: Junya（個人チャットを選択）")
    print("   - メッセージ: 「Chat ID取得テスト」")
    print("7. 「保存」→「テスト」→「手動」→「保存してテスト」")
    print("8. 「実行」ボタンをクリック")
    print("9. 実行後、「実行の履歴」を確認")
    print("10. 実行ログで「チャットID」をコピー")
    
    print("\n🔍 **取得できるChat IDの形式例**:")
    print("19:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx@unq.gbl.spaces")
    
    print("\n⚙️ **設定方法**:")
    print("取得したChat IDを以下に設定:")
    print("ファイル: config/settings.json")
    print("場所: 行番号 約55行目")
    print('   "chat_id": "ここに取得したChat IDを貼り付け"')
    
    print("\n🧪 **設定確認方法**:")
    print("python scripts/teams-chat-id-helper.py --test")
    
    print("\n❓ **トラブルシューティング**:")
    print("- Junyaとの個人チャットが見つからない場合:")
    print("  → Teams でまず直接メッセージを送信してチャットを作成")
    print("- 権限エラーが発生する場合:")
    print("  → Power Automate でTeamsコネクタに再認証")
    print("- Chat IDが無効な場合:")
    print("  → IDが正しくコピーされているか確認（改行や空白なし）")

def test_chat_id():
    """設定されたChat IDをテスト"""
    import json
    
    try:
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        chat_id = config['output']['teams']['chat_id']
        
        if chat_id == "CHAT_ID_TO_BE_PROVIDED":
            print("❌ Chat IDが設定されていません")
            print("   → 上記のガイドに従ってChat IDを取得・設定してください")
            return False
        
        # Chat IDの形式チェック
        if chat_id.startswith("19:") and "@unq.gbl.spaces" in chat_id:
            print("✅ Chat ID形式: 正常")
            print(f"   設定済みID: {chat_id[:30]}...{chat_id[-20:]}")
            return True
        else:
            print("⚠️  Chat ID形式が一般的でない形式です")
            print(f"   設定済みID: {chat_id}")
            print("   → 正しくコピーされているか確認してください")
            return False
            
    except FileNotFoundError:
        print("❌ 設定ファイルが見つかりません: config/settings.json")
        return False
    except json.JSONDecodeError:
        print("❌ 設定ファイルのJSON形式が無効です")
        return False
    except KeyError as e:
        print(f"❌ 設定ファイルに必要なキーがありません: {e}")
        return False

def create_test_flow_template():
    """Power Automateテストフロー用のJSONテンプレートを生成"""
    
    template = {
        "flow_name": "Chat ID取得テスト",
        "trigger": {
            "type": "手動でトリガーされるクラウドフロー",
            "description": "手動実行でChat IDを取得"
        },
        "actions": [
            {
                "name": "Teams_メッセージ投稿",
                "type": "Microsoft Teams - チャットまたはチャネルでメッセージを投稿",
                "settings": {
                    "投稿者": "フロー ボット",
                    "投稿先": "チャット",
                    "受信者": "Junya（個人チャット）",
                    "メッセージ": "Chat ID取得テスト - @{utcNow()}"
                }
            }
        ],
        "note": "実行後、実行履歴でチャットIDを確認してください"
    }
    
    print("📄 Power Automate テストフロー設定")
    print("=" * 40)
    print(json.dumps(template, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Chat ID設定テスト")
        print("=" * 30)
        test_chat_id()
    elif len(sys.argv) > 1 and sys.argv[1] == "--template":
        create_test_flow_template()
    else:
        print_teams_guide()
        
        print("\n🎯 **次のアクション**:")
        print("1. 上記の手順でChat IDを取得")
        print("2. config/settings.json に設定")
        print("3. python scripts/teams-chat-id-helper.py --test で確認")
        print("4. 次のタスク（Power Automate基本フロー作成）に進む") 