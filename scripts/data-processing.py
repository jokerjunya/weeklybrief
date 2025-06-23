#!/usr/bin/env python3
"""
週次レポート用データ処理スクリプト
Power Automateから呼び出し可能な形式でデータを処理
"""

import json
import os
import sys
import requests
import pandas as pd
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from news_summarizer import NewsSummarizer
from local_llm_summarizer import LocalLLMSummarizer
import yfinance as yf

class WeeklyReportProcessor:
    def __init__(self, config_path: str = "config/settings.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        # ニュース要約機能を初期化（ローカルLLM優先）
        local_llm_config = self.config["data_sources"].get("local_llm", {})
        if local_llm_config.get("enabled", False):
            self.news_summarizer = LocalLLMSummarizer(config_path)
            print("📱 ローカルLLM（Qwen3）要約機能を使用")
        else:
            self.news_summarizer = NewsSummarizer(config_path)
            print("☁️  クラウドAPI要約機能を使用")
    
    def process_sales_data(self, csv_file_path: str = None) -> Dict[str, Any]:
        """
        ビジネスデータを処理（Placement: 内定数、Online Platform: 売上）
        """
        # Online Platform（サービスB）の実データパス
        online_platform_csv = "data/revenue_data.csv"
        
        # Placement（サービスA）の内定数データ - 実データに更新
        placement_current = 2739    # 今週の内定数
        placement_previous_week = 2550    # 先週の内定数
        placement_previous_year = 2916    # 昨年同期の内定数
        
        # 前年同期比と前週比を計算
        placement_yoy_change = ((placement_current - placement_previous_year) / placement_previous_year) * 100
        placement_weekly_change = ((placement_current - placement_previous_week) / placement_previous_week) * 100
        
        placement_data = {
            "name": "Placement",
            "metric_type": "内定数",
            "period": "2025/06/09-2025/06/13",
            "current_value": placement_current,
            "previous_year_value": placement_previous_year,
            "previous_week_value": placement_previous_week,
            "yoy_change": round(placement_yoy_change, 1),  # 前年同期比
            "weekly_change": round(placement_weekly_change, 1)  # 前週比
        }
        
        # Online Platform（サービスB）の売上実データを読み込み
        online_platform_data = self._load_online_platform_data(online_platform_csv)
        
        # サービス別データリスト
        services = [
            placement_data,
            {
                "name": "Online Platform",
                "metric_type": "売上",
                "period": "2025/06/15-2025/06/22",
                "current_value": online_platform_data["current_sales"],
                "previous_week_value": online_platform_data.get("previous_week_sales"),
                "previous_year_value": online_platform_data["previous_year_sales"],
                "yoy_change": online_platform_data["yoy_change"],
                "weekly_change": online_platform_data["weekly_change"]
            }
        ]
        
        return {
            "service_count": len(services),
            "services": services
        }
    
    def _load_online_platform_data(self, csv_path: str) -> Dict[str, Any]:
        """
        Online Platform（サービスB）の実データを読み込み
        """
        try:
            if not os.path.exists(csv_path):
                print(f"⚠️  Online Platformデータが見つかりません: {csv_path}")
                return self._get_dummy_online_platform_data()
            
            df = pd.read_csv(csv_path)
            
            # 新しいCSVファイルの構造: last_week_revenue_jpy,two_weeks_ago_revenue_jpy,last_year_last_week_revenue_jpy,wow_pct,yoy_pct
            row = df.iloc[0]  # 最初の行を取得
            
            current_sales = int(row['last_week_revenue_jpy'])  # 今週の売上（last_week_revenue_jpy）
            previous_week_sales = int(row['two_weeks_ago_revenue_jpy'])  # 前週の売上（two_weeks_ago_revenue_jpy）
            previous_year_sales = int(row['last_year_last_week_revenue_jpy'])  # 前年同週の売上
            wow_pct = float(row['wow_pct'].replace('%', '')) if isinstance(row['wow_pct'], str) else float(row['wow_pct'])
            yoy_pct = float(row['yoy_pct'].replace('%', '')) if isinstance(row['yoy_pct'], str) else float(row['yoy_pct'])
            
            return {
                "name": "Online Platform",
                "current_sales": current_sales,
                "previous_week_sales": previous_week_sales,
                "previous_year_sales": previous_year_sales,
                "yoy_change": yoy_pct,
                "weekly_change": wow_pct
            }
            
        except Exception as e:
            print(f"❌ Online Platformデータ読み込みエラー: {e}")
            return self._get_dummy_online_platform_data()
    
    def _get_dummy_online_platform_data(self) -> Dict[str, Any]:
        """
        Online Platformのダミーデータ（フォールバック用）
        """
        return {
            "name": "Online Platform",
            "current_sales": 8765432,
            "previous_week_sales": 8987654,
            "previous_year_sales": 9876543,
            "yoy_change": -11.2,
            "weekly_change": -2.5
        }
    
    def fetch_stock_data(self, tickers: List[str]) -> Dict[str, Any]:
        """
        yfinanceを使用して株価データを取得・処理
        """
        stock_data = {}
        
        # ティッカーシンボルのマッピング（yfinance用）
        ticker_mapping = {
            "N225": "^N225",     # 日経平均株価
            "SPY": "^GSPC",      # S&P 500 Index
            "RECRUIT": "6098.T"  # リクルートHD（東証）
        }
        
        for ticker in tickers:
            yf_ticker = ticker_mapping.get(ticker, ticker)
            stock_data[ticker] = self._fetch_stock_from_yfinance(yf_ticker, ticker)
        
        return stock_data
    
    def _fetch_stock_from_yfinance(self, yf_ticker: str, original_ticker: str) -> Dict[str, Any]:
        """
        yfinanceから株価データを取得
        
        Args:
            yf_ticker: yfinance用のティッカーシンボル
            original_ticker: 元のティッカーシンボル
        """
        try:
            # yfinanceでデータ取得
            stock = yf.Ticker(yf_ticker)
            
            # 基本情報取得
            info = stock.info
            
            # 当日のデータを取得（1分間隔で当日分）
            hist = stock.history(period="1d", interval="1m")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[0]  # 当日始値
                
                change = current_price - open_price
                change_percent = (change / open_price) * 100 if open_price != 0 else 0
                
                # 通貨情報を取得
                currency = info.get("currency", "JPY")
                
                # 全て日本円表示に統一
                return {
                    "current_price": round(float(current_price), 2),
                    "change": round(float(change), 2),
                    "change_percent": round(float(change_percent), 2),
                    "currency": "JPY",
                    "status": "success"
                }
            else:
                return {
                    "error": "履歴データが取得できませんでした",
                    "status": "failed"
                }
                
        except Exception as e:
            print(f"Error fetching {yf_ticker}: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def fetch_news_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        ニュースデータを取得・処理（過去1週間以内、複数データソース使用）
        """
        all_articles = []
        
        # 過去1週間の日付を計算（6/16以降確実に取得）
        from datetime import datetime, timedelta
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        target_date = max(one_week_ago, '2025-06-16')  # 6/16以降を確実に取得
        
        print(f"📰 ニュース取得開始 - 対象期間: {target_date}以降")
        
        # NewsAPI（メインソース）
        newsapi_articles = self._fetch_from_newsapi(keywords, target_date)
        all_articles.extend(newsapi_articles)
        
        # GNews API（追加ソース）
        gnews_articles = self._fetch_from_gnews(keywords, target_date)
        all_articles.extend(gnews_articles)
        
        # 重複記事を除去（URLベース）
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 日付順でソートし、上位15件を取得
        unique_articles.sort(key=lambda x: x["published_at"], reverse=True)
        selected_articles = unique_articles[:15]
        
        print(f"✅ ニュース取得完了 - 合計{len(unique_articles)}件（重複除去後）、選択{len(selected_articles)}件")
        
        # 日本語要約を追加
        processed_articles = self.news_summarizer.process_news_articles(selected_articles)
        
        return processed_articles
    
    def _fetch_from_newsapi(self, keywords: List[str], from_date: str) -> List[Dict[str, Any]]:
        """NewsAPIからニュースを取得"""
        api_key = self.config["data_sources"]["news_data"]["api_key"]
        articles = []
        
        for keyword in keywords:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": keyword,
                    "apiKey": api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "from": from_date
                }
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get("articles"):
                    for article in data["articles"]:
                        # より多くの情報を収集（title + description + content）
                        title = article.get("title", "")
                        description = article.get("description", "") or ""
                        content = article.get("content", "") or ""
                        
                        # contentからHTMLタグやノイズを除去
                        import re
                        if content:
                            # 一般的なノイズパターンを除去
                            content = re.sub(r'[{}\[\]"\'\\]', '', content)
                            content = re.sub(r'window\.open.*?return false;', '', content)
                            content = re.sub(r'https?://[^\s]+', '', content)  # URLを除去
                            content = re.sub(r'\s+', ' ', content).strip()  # 空白を正規化
                        
                        articles.append({
                            "title": title,
                            "description": description,
                            "content": content,
                            "url": article["url"],
                            "published_at": article["publishedAt"],
                            "keyword": keyword,
                            "source": "NewsAPI"
                        })
            except Exception as e:
                print(f"Error fetching news from NewsAPI for {keyword}: {e}")
        
        return articles
    
    def _fetch_from_gnews(self, keywords: List[str], from_date: str) -> List[Dict[str, Any]]:
        """GNews APIからニュースを取得"""
        articles = []
        
        # 設定ファイルからGNews APIキーを取得
        gnews_api_key = self.config["data_sources"]["news_data"].get("gnews_api_key")
        
        if not gnews_api_key:
            print("⚠️ GNews APIキーが設定されていません")
            return articles
        
        for keyword in keywords:
            try:
                url = "https://gnews.io/api/v4/search"
                params = {
                    "q": keyword,
                    "token": gnews_api_key,
                    "lang": "en",
                    "country": "us",
                    "max": 5,
                    "from": from_date + "T00:00:00Z"
                }
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("articles"):
                        for article in data["articles"]:
                            articles.append({
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "content": article.get("content", ""),  # GNewsでは制限あり
                                "url": article.get("url", ""),
                                "published_at": article.get("publishedAt", ""),
                                "keyword": keyword,
                                "source": "GNews"
                            })
                else:
                    print(f"GNews API error for {keyword}: {response.status_code}")
                    
            except Exception as e:
                print(f"Error fetching news from GNews for {keyword}: {e}")
        
        return articles
    
    def get_weekly_news_summary(self, articles: List[Dict[str, Any]]) -> str:
        """
        週間ニュースサマリーを生成
        
        Args:
            articles (List[Dict]): 処理済みニュース記事リスト
        
        Returns:
            str: 週間ニュースサマリー（300文字程度）
        """
        return self.news_summarizer.generate_weekly_news_summary(articles)
    
    def format_schedule_data(self, outlook_events: List[Dict]) -> str:
        """
        Outlookスケジュールを整形
        """
        if not outlook_events:
            return "今週はスケジュールがありません。"
        
        formatted_schedule = []
        for event in outlook_events:
            # TODO: 実際のOutlookイベント構造に応じて実装
            formatted_schedule.append(f"• {event.get('subject', 'タイトル未設定')}")
        
        return "\n".join(formatted_schedule)
    
    def generate_html_tables(self, sales_data: Dict, stock_data: Dict) -> Dict[str, str]:
        """
        HTMLテーブルを生成
        """
        # サービス別ビジネスメトリクステーブル
        if sales_data.get("services"):
            service_rows = []
            for service in sales_data["services"]:
                yoy_color = "green" if service.get('yoy_change', 0) > 0 else "red"
                weekly_color = "green" if service.get('weekly_change', 0) > 0 else "red"
                
                # メトリックタイプに応じて値をフォーマット
                if service.get('metric_type') == '内定数':
                    current_display = f"{service['current_value']:,}件"
                else:  # 売上
                    current_display = f"¥{service['current_value']:,}"
                
                service_rows.append(f"""
                    <tr>
                        <td>{service['name']}</td>
                        <td>{service.get('metric_type', 'N/A')}</td>
                        <td>{current_display}</td>
                        <td style="color: {yoy_color};">{service['yoy_change']}%</td>
                        <td style="color: {weekly_color};">{service['weekly_change']}%</td>
                    </tr>
                """)
            
            sales_table_html = f"""
            <table border="1" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                <tr style="background-color: #f2f2f2;"><th>サービス名</th><th>指標</th><th>今週実績</th><th>前年同期比</th><th>前週比</th></tr>
                {''.join(service_rows)}
            </table>
            """
        else:
            sales_table_html = "<p>ビジネスデータがありません。</p>"
        
        # 株価テーブル
        stock_rows = []
        ticker_names = self.config["data_sources"]["stock_data"]["ticker_names"]
        
        for ticker, data in stock_data.items():
            if "error" not in data:
                name = ticker_names.get(ticker, ticker)
                change_color = "green" if data.get('change_percent', 0) > 0 else "red"
                
                # 円表示に統一
                if data.get('currency') == 'JPY':
                    # 日経平均（JPY）
                    price_display = f"¥{data['current_price']:,.0f}"
                    change_display = f"{data['change']:+,.0f}"
                elif 'current_price_jpy' in data:
                    # USD銘柄は円換算値を使用
                    price_display = f"¥{data['current_price_jpy']:,.0f}"
                    change_display = f"{data['change_jpy']:+,.0f}"
                else:
                    # フォールバック：USD表示
                    price_display = f"${data['current_price']:.2f}"
                    change_display = f"{data['change']:+.2f}"
                
                stock_rows.append(f"""
                    <tr>
                        <td>{name} ({ticker})</td>
                        <td>{price_display}</td>
                        <td style="color: {change_color};">{change_display}</td>
                        <td style="color: {change_color};">{data.get('change_percent', 'N/A')}%</td>
                    </tr>
                """)
        
        stock_html = f"""
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;"><th>銘柄</th><th>現在価格</th><th>前日差</th><th>前日比</th></tr>
            {''.join(stock_rows)}
        </table>
        """
        
        return {
            "sales_table": sales_table_html,
            "stock_table": stock_html
        }
    
    def format_japanese_currency(self, amount: int, detailed: bool = False) -> str:
        """
        日本円を日本式表記（億円、万円）でフォーマット
        
        Args:
            amount (int): 金額（円）
            detailed (bool): 詳細表示（万円まで表示）
        
        Returns:
            str: フォーマットされた金額文字列
        """
        if amount >= 100000000:  # 1億円以上
            oku = amount / 100000000
            if detailed:
                # 詳細表示：37億7,244万円のような形式
                oku_part = int(amount // 100000000)
                man_part = int((amount % 100000000) // 10000)
                if man_part > 0:
                    return f"{oku_part}億{man_part:,}万円"
                else:
                    return f"{oku_part}億円"
            else:
                # 通常表示
                if oku >= 10:
                    return f"{oku:.0f}億円"
                else:
                    return f"{oku:.1f}億円"
        elif amount >= 10000:  # 1万円以上
            man = amount / 10000
            if man >= 100:
                return f"{man:.0f}万円"
            else:
                return f"{man:.1f}万円"
        else:
            return f"{amount:,}円"

if __name__ == "__main__":
    # テスト実行用
    processor = WeeklyReportProcessor()
    
    # ビジネスデータ処理テスト（事業別メトリクス）
    print("=== ビジネスデータ処理テスト ===")
    print("📊 Placement（内定数）+ Online Platform（売上）の事業別データを生成")
    sales_data = processor.process_sales_data()
    print(json.dumps(sales_data, indent=2, ensure_ascii=False))
    
    # サンプル株価データでテスト（実際のAPIキーが設定されていない場合）
    print("\n=== HTMLテーブル生成テスト ===")
    sample_stock_data = {
        "AAPL": {"current_price": 195.64, "change": 2.34, "change_percent": 1.21},
        "GOOGL": {"current_price": 2750.80, "change": -15.20, "change_percent": -0.55},
        "MSFT": {"current_price": 378.91, "change": 5.67, "change_percent": 1.52}
    }
    
    tables = processor.generate_html_tables(sales_data, sample_stock_data)
    print("売上テーブル:")
    print(tables["sales_table"])
    print("\n株価テーブル:")
    print(tables["stock_table"])
    
    # ニュースデータ取得テスト（APIキーが設定されている場合のみ）
    if processor.config["data_sources"]["news_data"]["api_key"] != "API_KEY_TO_BE_PROVIDED":
        print("\n=== ニュースデータ取得テスト ===")
        sample_keywords = ["OpenAI", "Anthropic"]
        news_data = processor.fetch_news_data(sample_keywords)
        print(f"取得記事数: {len(news_data)}")
    else:
        print("\n=== ニュースAPIキーが未設定のためスキップ ===")
    
    if processor.config["data_sources"]["stock_data"]["api_key"] != "API_KEY_TO_BE_PROVIDED":
        print("\n=== 株価データ取得テスト ===")
        tickers = processor.config["data_sources"]["stock_data"]["tickers"]
        stock_data = processor.fetch_stock_data(tickers)
        print(json.dumps(stock_data, indent=2))
    else:
        print("\n=== 株価APIキーが未設定のためスキップ ===") 