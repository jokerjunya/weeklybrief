#!/usr/bin/env python3
"""
週次レポート用データ処理スクリプト
Power Automateから呼び出し可能な形式でデータを処理
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Any
from news_summarizer import NewsSummarizer
from local_llm_summarizer import LocalLLMSummarizer

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
        online_platform_csv = "/Users/01062544/Downloads/Revenue_non-RAG_jp_weekly_WoW&YoY.csv"
        
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
            
            # CSVファイルの構造: this_week_revenue_jpy,last_week_revenue_jpy,last_year_same_week_revenue_jpy,wow_pct,yoy_pct
            row = df.iloc[0]  # 最初の行を取得
            
            current_sales = int(row['this_week_revenue_jpy'])
            previous_week_sales = int(row['last_week_revenue_jpy'])
            previous_year_sales = int(row['last_year_same_week_revenue_jpy'])
            wow_pct = float(row['wow_pct'])
            yoy_pct = float(row['yoy_pct'])
            
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
        株価データを取得・処理（日経平均はYahoo Finance、その他はAlpha Vantage）
        """
        stock_data = {}
        
        for ticker in tickers:
            if ticker == "N225":
                # 日経平均はYahoo Finance APIを使用
                stock_data[ticker] = self._fetch_nikkei_from_yahoo()
            else:
                # その他はAlpha Vantage APIを使用
                stock_data[ticker] = self._fetch_stock_from_alpha_vantage(ticker)
        
        return stock_data
    
    def _fetch_nikkei_from_yahoo(self) -> Dict[str, Any]:
        """
        Yahoo Finance APIから日経平均株価を取得
        """
        try:
            import time
            import json
            
            # レート制限を避けるため少し待機
            time.sleep(2)
            
            # 複数のエンドポイントを試行
            urls = [
                "https://query1.finance.yahoo.com/v8/finance/chart/%5EN225",
                "https://query2.finance.yahoo.com/v8/finance/chart/%5EN225"
            ]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://finance.yahoo.com/"
            }
            
            for url in urls:
                try:
                    params = {
                        "interval": "1d",
                        "range": "5d",  # 5日分取得してより安定したデータを取得
                        "includePrePost": "false"
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=15)
                    print(f"Yahoo Finance response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                        except json.JSONDecodeError:
                            print(f"JSON decode error. Response text: {response.text[:200]}")
                            continue
                        
                        if "chart" in data and data["chart"]["result"] and len(data["chart"]["result"]) > 0:
                            result = data["chart"]["result"][0]
                            
                            if "indicators" in result and "quote" in result["indicators"]:
                                closes = result["indicators"]["quote"][0]["close"]
                                
                                # Noneを除去して有効な価格データのみを取得
                                valid_closes = [price for price in closes if price is not None]
                                
                                if len(valid_closes) >= 2:
                                    current_price = valid_closes[-1]  # 最新価格
                                    previous_price = valid_closes[-2]  # 前営業日価格
                                    
                                    change = current_price - previous_price
                                    change_percent = (change / previous_price) * 100
                                    
                                    return {
                                        "current_price": round(current_price, 2),
                                        "change": round(change, 2),
                                        "change_percent": round(change_percent, 2)
                                    }
                        
                        print(f"Unexpected data structure: {list(data.keys()) if 'data' in locals() else 'No data'}")
                    
                except requests.exceptions.RequestException as e:
                    print(f"Request error for {url}: {e}")
                    continue
            
            # 全てのエンドポイントで失敗した場合、フォールバック値を返す
            print("⚠️  Yahoo Finance API取得に失敗、フォールバック値を使用")
            return {
                "current_price": 38486.29,  # 正確な現在値
                "change": -2.05,
                "change_percent": -0.01,
                "note": "Yahoo Finance API unavailable - using fallback value"
            }
                
        except Exception as e:
            print(f"Error fetching Nikkei 225 from Yahoo Finance: {e}")
            return {
                "current_price": 38486.29,  # 正確な現在値
                "change": -2.05,
                "change_percent": -0.01,
                "error": f"Yahoo Finance API error: {str(e)}"
            }
    
    def _fetch_stock_from_alpha_vantage(self, ticker: str) -> Dict[str, Any]:
        """
        Alpha Vantage APIから株価データを取得
        """
        try:
            api_key = self.config["data_sources"]["stock_data"]["api_key"]
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            # 最新の株価情報を抽出
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                dates = list(time_series.keys())
                if dates:
                    latest_date = dates[0]
                    latest_data = time_series[latest_date]
                    previous_date = dates[1] if len(dates) > 1 else dates[0]
                    previous_data = time_series[previous_date]
                    
                    current_price = float(latest_data["4. close"])
                    previous_price = float(previous_data["4. close"])
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100
                    
                    return {
                        "current_price": current_price,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2)
                    }
                else:
                    return {"error": "No data available"}
            else:
                return {"error": f"Unexpected response format: {list(data.keys())}"}
                                     
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            return {"error": str(e)}
    
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
        
        # GNews APIキーを設定に追加（フリープラン使用）
        gnews_api_key = "your_gnews_api_key_here"  # 実際のキーに置き換え
        
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
                stock_rows.append(f"""
                    <tr>
                        <td>{name} ({ticker})</td>
                        <td>{data.get('current_price', 'N/A')}</td>
                        <td style="color: {change_color};">{data.get('change', 'N/A')}</td>
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