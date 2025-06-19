#!/usr/bin/env python3
"""
週次レポート用データ処理スクリプト
Power Automateから呼び出し可能な形式でデータを処理
"""

import json
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
    
    def process_sales_data(self, csv_file_path: str) -> Dict[str, Any]:
        """
        売上CSVデータを処理してサマリーを生成
        """
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            
            # 合計行を除いてサービス別データを取得
            service_data = df[df['サービス名'] != '合計／平均'].copy()
            total_row = df[df['サービス名'] == '合計／平均'].iloc[0]
            
            # 数値データの変換（カンマ区切りの数値を整数に変換）
            def clean_numeric(value):
                if isinstance(value, str):
                    return int(value.replace(',', ''))
                # NumPy型をPython標準型に変換
                if hasattr(value, 'item'):
                    return value.item()
                return int(value) if isinstance(value, (int, float)) else value
            
            # サマリー情報を生成
            summary = {
                "total_current_sales": clean_numeric(total_row['今週売上額 (¥)']),
                "total_previous_year_sales": clean_numeric(total_row['前年同週売上額 (¥)']),
                "yoy_growth_rate": float(total_row['YoY増減率 (%)']),
                "weekly_change": float(total_row['前週比 (%)']),
                "service_count": int(len(service_data)),
                "services": []
            }
            
            # サービス別詳細
            for _, row in service_data.iterrows():
                summary["services"].append({
                    "name": str(row['サービス名']),
                    "current_sales": clean_numeric(row['今週売上額 (¥)']),
                    "yoy_change": float(row['YoY増減率 (%)']),
                    "weekly_change": float(row['前週比 (%)'])
                })
            
            return summary
        except Exception as e:
            return {"error": str(e)}
    
    def fetch_stock_data(self, tickers: List[str]) -> Dict[str, Any]:
        """
        株価データを取得・処理
        """
        api_key = self.config["data_sources"]["stock_data"]["api_key"]
        stock_data = {}
        
        for ticker in tickers:
            try:
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
                        
                        stock_data[ticker] = {
                            "current_price": current_price,
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2)
                        }
                    else:
                        stock_data[ticker] = {"error": "No data available"}
                else:
                    stock_data[ticker] = {"error": f"Unexpected response format: {list(data.keys())}"}
                                         
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                stock_data[ticker] = {"error": str(e)}
        
        return stock_data
    
    def fetch_news_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        ニュースデータを取得・処理（過去1週間以内）
        """
        api_key = self.config["data_sources"]["news_data"]["api_key"]
        all_articles = []
        
        # 過去1週間の日付を計算
        from datetime import datetime, timedelta
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        for keyword in keywords:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": keyword,
                    "apiKey": api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "from": one_week_ago  # 過去1週間以内のニュースのみ
                }
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get("articles"):
                    for article in data["articles"]:
                        all_articles.append({
                            "title": article["title"],
                            "description": article["description"],
                            "url": article["url"],
                            "published_at": article["publishedAt"],
                            "keyword": keyword
                        })
            except Exception as e:
                print(f"Error fetching news for {keyword}: {e}")
        
        # 日付順でソートし、上位10件を取得
        all_articles.sort(key=lambda x: x["published_at"], reverse=True)
        selected_articles = all_articles[:10]
        
        # 日本語要約を追加
        processed_articles = self.news_summarizer.process_news_articles(selected_articles)
        
        return processed_articles
    
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
        # 売上サマリーテーブル
        sales_summary_html = f"""
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;"><th>項目</th><th>値</th></tr>
            <tr><td>今週総売上</td><td>¥{sales_data.get('total_current_sales', 0):,}</td></tr>
            <tr><td>前年同週売上</td><td>¥{sales_data.get('total_previous_year_sales', 0):,}</td></tr>
            <tr><td>前年同期比</td><td>{sales_data.get('yoy_growth_rate', 0)}%</td></tr>
            <tr><td>前週比</td><td>{sales_data.get('weekly_change', 0)}%</td></tr>
        </table>
        """
        
        # サービス別売上テーブル
        if sales_data.get("services"):
            service_rows = []
            for service in sales_data["services"]:
                yoy_color = "green" if service.get('yoy_change', 0) > 0 else "red"
                weekly_color = "green" if service.get('weekly_change', 0) > 0 else "red"
                service_rows.append(f"""
                    <tr>
                        <td>{service['name']}</td>
                        <td>¥{service['current_sales']:,}</td>
                        <td style="color: {yoy_color};">{service['yoy_change']}%</td>
                        <td style="color: {weekly_color};">{service['weekly_change']}%</td>
                    </tr>
                """)
            
            services_html = f"""
            <table border="1" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                <tr style="background-color: #f2f2f2;"><th>サービス名</th><th>今週売上</th><th>前年同期比</th><th>前週比</th></tr>
                {''.join(service_rows)}
            </table>
            """
            sales_table_html = sales_summary_html + services_html
        else:
            sales_table_html = sales_summary_html
        
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
    
    # 売上データ処理テスト
    print("=== 売上データ処理テスト ===")
    sales_data = processor.process_sales_data("/Users/01062544/Downloads/weekly_sales_report.csv")
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