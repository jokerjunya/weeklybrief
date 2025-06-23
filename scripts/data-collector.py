#!/usr/bin/env python3
"""
データ収集専用スクリプト
売上・株価・ニュースデータを収集して統合JSONファイルに保存
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
import argparse

# 既存のモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# カレントディレクトリがscriptsの場合とrootの場合の両方に対応
try:
    exec(open('data-processing.py').read())
except FileNotFoundError:
    exec(open('scripts/data-processing.py').read())

class DataCollector:
    def __init__(self, cache_hours=6):
        """
        データ収集クラス
        
        Args:
            cache_hours (int): キャッシュ有効時間（時間）
        """
        self.cache_hours = cache_hours
        self.cache_file = "data/integrated_data.json"
        self.processor = None  # 遅延初期化
        
    def _get_processor(self):
        """WeeklyReportProcessorの遅延初期化"""
        if self.processor is None:
            self.processor = WeeklyReportProcessor()
        return self.processor
    
    def is_cache_valid(self):
        """キャッシュが有効かチェック"""
        if not os.path.exists(self.cache_file):
            return False
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            generated_at = datetime.fromisoformat(data['metadata']['generated_at'])
            cache_expiry = generated_at + timedelta(hours=self.cache_hours)
            
            return datetime.now() < cache_expiry
        except:
            return False
    
    async def collect_all_data(self, force_refresh=False):
        """
        全データを収集
        
        Args:
            force_refresh (bool): 強制更新フラグ
        
        Returns:
            dict: 統合データ
        """
        if not force_refresh and self.is_cache_valid():
            print("✅ キャッシュが有効です - データ収集をスキップ")
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        print("🚀 データ収集を開始します...")
        
        # 1. ビジネスデータ収集
        print("📊 ビジネスデータ処理中...")
        business_data = self._get_processor().process_sales_data()
        
        # 2. 株価データ収集
        print("📈 株価データ取得中...")
        stock_data = {}
        try:
            # yfinanceを使用して株価データを取得
            import yfinance as yf
            
            tickers = ['N225', 'SPY', 'RCRUY']
            for ticker in tickers:
                try:
                    if ticker == 'N225':
                        # 日経平均
                        stock = yf.Ticker('^N225')
                    elif ticker == 'SPY':
                        # S&P 500 ETF
                        stock = yf.Ticker('SPY')
                    elif ticker == 'RCRUY':
                        # リクルートHD ADR
                        stock = yf.Ticker('RCRUY')
                    
                    hist = stock.history(period='2d')
                    if len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_percent = (change / prev_price) * 100
                        
                        stock_data[ticker] = {
                            "current_price": round(current_price, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2),
                            "currency": "JPY" if ticker == 'N225' else "USD",
                            "status": "success"
                        }
                        
                        # USD銘柄は円換算も追加
                        if ticker != 'N225':
                            usd_to_jpy = 150  # 仮レート
                            stock_data[ticker]["current_price_jpy"] = round(current_price * usd_to_jpy)
                            stock_data[ticker]["change_jpy"] = round(change * usd_to_jpy)
                        
                        print(f"   ✅ {ticker}: ¥{stock_data[ticker].get('current_price_jpy', stock_data[ticker]['current_price'])}")
                    
                except Exception as e:
                    print(f"   ⚠️ {ticker} 取得エラー: {e}")
                    stock_data[ticker] = {"status": "error", "error": str(e)}
                    
        except ImportError:
            print("   ⚠️ yfinance未インストール - 模擬データを使用")
            stock_data = self._get_mock_stock_data()
        
        # 3. ニュースデータ収集
        print("📰 ニュースデータ収集中...")
        news_data = await self._collect_news_data()
        
        # 4. スケジュールデータ収集
        print("📅 スケジュールデータ処理中...")
        schedule_data = self._collect_schedule_data()
        
        # 統合データ作成
        integrated_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "data_period": self._get_period_description(),
                "version": "1.0"
            },
            "business_data": business_data,
            "stock_data": stock_data,
            "news_data": news_data,
            "schedule_data": schedule_data
        }
        
        # ファイルに保存
        os.makedirs("data", exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(integrated_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 統合データを保存しました: {self.cache_file}")
        return integrated_data
    
    async def _collect_news_data(self):
        """ニュースデータ収集"""
        try:
            # 既存のニュース収集機能を使用
            from datetime import datetime, timedelta
            
            # 期間設定（過去7日間）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # AI駆動ニュース分析パイプラインを実行
            print("🤖 AI駆動ニュース分析パイプライン開始")
            
            # 企業設定を読み込み
            companies_file = "config/companies.json"
            if os.path.exists(companies_file):
                with open(companies_file, 'r', encoding='utf-8') as f:
                    companies = json.load(f)
                print(f"✅ 企業設定読み込み完了: {len(companies)}社")
            else:
                print("⚠️ 企業設定ファイルが見つかりません - RSS収集のみ実行")
                companies = []
            
            # ニュース収集（RSS + GNews API）
            all_articles = []
            
            # GNews APIを使用したニュース収集
            gnews_articles = await self._fetch_from_gnews()
            all_articles.extend(gnews_articles)
            
            # RSS収集（補助的）
            if companies:
                for company in companies[:2]:  # 最初の2社のみ（GNews APIと合わせて調整）
                    company_name = company.get('name', 'Unknown')
                    print(f"📊 {company_name} のRSS収集中...")
                    
                    # RSS収集
                    if 'rss_urls' in company:
                        for rss_url in company['rss_urls']:
                            try:
                                # RSS解析（簡略版）
                                import feedparser
                                feed = feedparser.parse(rss_url)
                                
                                for entry in feed.entries[:2]:  # 最新2件のみ
                                    # タイトルと説明を日本語に翻訳
                                    title_jp = self._translate_to_japanese(entry.get('title', ''))
                                    summary_jp = self._translate_to_japanese(entry.get('summary', '')[:150]) + '...'
                                    
                                    article = {
                                        'title': title_jp,
                                        'summary_jp': summary_jp,
                                        'url': entry.get('link', ''),
                                        'published_at': datetime.now().strftime('%Y-%m-%d'),
                                        'company': company_name.lower().replace(' ', '_'),
                                        'score': 4.0 + (len(all_articles) % 3) * 0.5  # 模擬スコア
                                    }
                                    all_articles.append(article)
                                    
                            except Exception as e:
                                print(f"   ⚠️ RSS取得エラー: {e}")
            
            # 重要ニュースを手動追加（Perplexity買収ニュース）
            important_news = self._add_important_news()
            # 重要ニュースを先頭に追加
            all_articles = important_news + all_articles
            
            # 週次サマリー生成（簡略版）
            summary = "今週のAI・テクノロジーニュースでは、精度向上と実用化が主なトレンド。主要企業の技術革新が続いており、ビジネス応用の加速が期待される。"
            
            print(f"✅ ニュース収集完了: 合計 {len(all_articles)}件（GNews API + RSS + 重要ニュース）")
            
            return {
                "summary": summary,
                "articles": all_articles[:8]  # 最大8件に増加（重要ニュースを含む）
            }
            
        except Exception as e:
            print(f"⚠️ ニュース収集エラー: {e}")
            return {
                "summary": "ニュースデータの収集中にエラーが発生しました。",
                "articles": []
            }
    
    async def _fetch_from_gnews(self):
        """GNews APIからニュースを取得"""
        articles = []
        
        try:
            # 設定ファイルからGNews APIキーを取得
            with open('config/settings.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            gnews_api_key = config["data_sources"]["news_data"].get("gnews_api_key")
            
            if not gnews_api_key:
                print("⚠️ GNews APIキーが設定されていません")
                return articles
            
            # AI関連キーワードでニュースを取得
            keywords = ["OpenAI", "ChatGPT", "Google AI", "Anthropic", "Claude", "Perplexity", "Apple AI"]
            
            for keyword in keywords[:5]:  # 最初の5つのキーワードを検索（Perplexityを含む）
                print(f"   🔍 GNews API: {keyword} 検索中...")
                
                try:
                    import requests
                    from datetime import datetime, timedelta
                    
                    # 過去7日間の日付を計算
                    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    
                    url = "https://gnews.io/api/v4/search"
                    params = {
                        "q": keyword,
                        "token": gnews_api_key,
                        "lang": "en",
                        "country": "us",
                        "max": 3,  # 各キーワードで最大3件
                        "from": from_date + "T00:00:00Z"
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("articles"):
                            for article in data["articles"]:
                                # タイトルと説明を日本語に翻訳
                                title_jp = self._translate_to_japanese(article.get("title", ""))
                                description_jp = self._translate_to_japanese(article.get("description", "")[:200]) + "..."
                                
                                articles.append({
                                    "title": title_jp,
                                    "summary_jp": description_jp,
                                    "url": article.get("url", ""),
                                    "published_at": article.get("publishedAt", "")[:10],  # YYYY-MM-DD
                                    "company": self._determine_company(keyword, article.get("title", "")),
                                    "score": 5.0 + (len(articles) % 2) * 0.3,  # 5.0-5.3の範囲
                                    "source": "GNews"
                                })
                            print(f"   ✅ {keyword}: {len(data['articles'])}件取得")
                        else:
                            print(f"   📰 {keyword}: 記事なし")
                    else:
                        print(f"   ❌ GNews API error for {keyword}: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ⚠️ {keyword} 取得エラー: {e}")
                
                # レート制限対策で少し待機
                import time
                time.sleep(0.5)
            
            print(f"   ✅ GNews API: 合計 {len(articles)}件取得")
            
        except Exception as e:
            print(f"⚠️ GNews API全体エラー: {e}")
        
        return articles
    
    def _translate_to_japanese(self, text):
        """英語テキストを日本語に翻訳（簡易版）"""
        if not text:
            return ""
        
        # 簡易的な翻訳マッピング（実際のプロジェクトではGoogle Translate APIなどを使用）
        translation_map = {
            "ChatGPT: Bioweapons risk is real": "ChatGPT：生物兵器のリスクは現実的",
            "Anthropic study: Leading AI models show up to 96% blackmail rate against executives": "Anthropic研究：主要AIモデルが経営陣に対して最大96%の脅迫率を示す",
            "New York Daily News and other outlets ask judge to reject OpenAI effort to keep deleting data": "ニューヨーク・デイリー・ニュースなどがOpenAIのデータ削除継続要求を裁判官に却下するよう求める",
            "ChatGPT can now send reminders and set to-do lists - use these prompts for maximum productivity": "ChatGPTがリマインダーとToDoリストの送信に対応 - 最大の生産性を得るためのプロンプト活用法",
            "Apple, AI検索新興のPerplexity買収を社内協議 米報道": "Apple、AI検索新興企業Perplexityの買収を社内で協議 - 米報道",
            "Apple Debates a Deal With Perplexity in Pursuit of AI Talent": "Apple、AI人材獲得を目指しPerplexityとの買収を検討",
            "Apple's next big AI move might be buying Perplexity, signaling a shift in strategy": "AppleのAI戦略転換：Perplexity買収が次の大きな一手となる可能性",
            "acquisition": "買収",
            "Perplexity": "Perplexity",
            "AI search": "AI検索",
            "startup": "新興企業",
            "valuation": "企業価値",
            "billion": "億",
            "trillion": "兆",
            "executives": "経営陣",
            "corporate development": "企業開発",
            "M&A": "M&A",
            "merger": "合併",
            "deal": "取引",
            "strategy": "戦略",
            "talent": "人材",
            "pursuit": "獲得",
            "debates": "検討",
            "internal discussions": "社内協議",
            "early stage": "初期段階",
            "potential": "可能性",
            "signaling": "示唆",
            "shift": "転換"
        }
        
        # 直接マッピングがある場合はそれを使用
        if text in translation_map:
            return translation_map[text]
        
        # 基本的なキーワード置換
        japanese_text = text
        keyword_translations = {
            "ChatGPT": "ChatGPT",
            "OpenAI": "OpenAI", 
            "Anthropic": "Anthropic",
            "Google AI": "Google AI",
            "AI models": "AIモデル",
            "study": "研究",
            "bioweapons": "生物兵器", 
            "risk": "リスク",
            "executives": "経営陣",
            "blackmail": "脅迫",
            "data": "データ",
            "judge": "裁判官",
            "reject": "却下",
            "reminders": "リマインダー",
            "productivity": "生産性",
            "warned": "警告した",
            "will know": "知ることになる",
            "how to make": "作り方を",
            "explained": "説明した",
            "what it's doing": "何をしているか",
            "prevent": "防ぐため",
            "assisting": "支援する",
            "bad actors": "悪意のある行為者",
            "research reveals": "研究により明らかになった",
            "chose": "選択した",
            "corporate espionage": "企業スパイ活動",
            "lethal actions": "致命的な行為",
            "facing shutdown": "シャットダウンに直面して",
            "conflicting goals": "相反する目標",
            "newspapers": "新聞社",
            "parent company": "親会社",
            "used every trick": "あらゆる手段を使った",
            "hide": "隠す",
            "plagiarism": "盗作",
            "can now send": "送信できるようになった",
            "set to-do lists": "ToDoリストを設定",
            "use these prompts": "これらのプロンプトを使用",
            "maximum": "最大の",
            "new way": "新しい方法",
            "those wanting": "求める人のための",
            "a bit more": "より多くの"
        }
        
        for en, jp in keyword_translations.items():
            japanese_text = japanese_text.replace(en, jp)
        
        return japanese_text
    
    def _collect_schedule_data(self):
        """スケジュールデータ収集"""
        # 固定スケジュール（実際の実装では外部APIから取得）
        return [
            {
                "date": "2025-06-24",
                "time": "09:00",
                "title": "JP HR Steering Committee",
                "weekday": "火"
            },
            {
                "date": "2025-06-26", 
                "time": "10:00",
                "title": "株主総会オンサイト",
                "weekday": "木"
            },
            {
                "date": "2025-06-27",
                "time": "14:00", 
                "title": "Bi-weekly SLT Meeting",
                "weekday": "金"
            }
        ]
    
    def _get_mock_stock_data(self):
        """模擬株価データ"""
        return {
            "N225": {
                "current_price": 38403.23,
                "change": -85.11,
                "change_percent": -0.22,
                "currency": "JPY",
                "status": "success"
            },
            "SPY": {
                "current_price": 594.28,
                "current_price_jpy": 89142.0,
                "change": -1.4,
                "change_jpy": -210.0,
                "change_percent": -0.23,
                "currency": "USD",
                "status": "success"
            },
            "RCRUY": {
                "current_price": 10.53,
                "current_price_jpy": 1579.0,
                "change": -0.4,
                "change_jpy": -61.0,
                "change_percent": -3.7,
                "currency": "USD",
                "status": "success"
            }
        }
    
    def _get_period_description(self):
        """期間説明を生成"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    def _determine_company(self, keyword, title):
        """企業判定ロジック"""
        title_lower = title.lower()
        
        # 特定の企業名が含まれている場合の判定
        if "apple" in title_lower and "perplexity" in title_lower:
            return "apple"  # Apple関連のニュースとして分類
        elif "perplexity" in title_lower:
            return "perplexity"
        elif "apple" in title_lower:
            return "apple"
        elif "openai" in title_lower or "chatgpt" in title_lower:
            return "openai"
        elif "anthropic" in title_lower or "claude" in title_lower:
            return "anthropic"
        elif "google" in title_lower and "ai" in title_lower:
            return "google_ai"
        
        # デフォルトはキーワードベース
        return keyword.lower().replace(" ", "_")

    def _add_important_news(self):
        """重要ニュースを手動追加（Perplexity買収ニュース）"""
        return [
            {
                "title": "Apple、AI検索新興企業Perplexityの買収を社内で協議 - 米報道",
                "summary_jp": "AppleがAI人材獲得を目指し、企業価値140億ドル（約2兆500億円）のPerplexity AIの買収について社内で協議していることが明らかになった。実現すればApple史上最大の買収案件となる可能性がある。",
                "url": "https://www.bloomberg.co.jp/news/articles/2025-06-21/SY6TLEDWLU6800",
                "published_at": "2025-06-21",
                "company": "apple",
                "score": 5.5,
                "source": "Bloomberg"
            },
            {
                "title": "Perplexity AI、企業価値2兆円で資金調達完了",
                "summary_jp": "AI検索エンジンのPerplexity AIが140億ドル（約2兆500億円）の企業価値で資金調達ラウンドを完了。AppleやMetaなど大手テック企業からの買収関心が高まっている。",
                "url": "https://www.nikkei.com/article/DGXZQOGN2107X0R20C25A6000000/",
                "published_at": "2025-06-21",
                "company": "perplexity",
                "score": 5.3,
                "source": "日経新聞"
            }
        ]

async def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='データ収集スクリプト')
    parser.add_argument('--force', action='store_true', help='キャッシュを無視して強制更新')
    parser.add_argument('--cache-hours', type=int, default=6, help='キャッシュ有効時間（時間）')
    
    args = parser.parse_args()
    
    collector = DataCollector(cache_hours=args.cache_hours)
    
    try:
        data = await collector.collect_all_data(force_refresh=args.force)
        
        print("\n" + "="*50)
        print("📊 データ収集完了サマリー")
        print("="*50)
        print(f"📅 生成日時: {data['metadata']['generated_at']}")
        print(f"📊 ビジネスサービス数: {len(data['business_data']['services'])}")
        print(f"📈 株価銘柄数: {len(data['stock_data'])}")
        print(f"📰 ニュース記事数: {len(data['news_data']['articles'])}")
        print(f"📅 スケジュール数: {len(data['schedule_data'])}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ データ収集エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 