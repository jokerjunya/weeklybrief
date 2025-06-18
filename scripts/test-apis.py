#!/usr/bin/env python3
"""
APIキー接続テスト用スクリプト
Alpha VantageとNewsAPIの接続を確認
"""

import json
import requests
from datetime import datetime

def test_alpha_vantage_api():
    """Alpha Vantage API接続テスト"""
    print("=== Alpha Vantage API テスト ===")
    
    # 設定読み込み
    with open('config/settings.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_key = config['data_sources']['stock_data']['api_key']
    
    if api_key == "API_KEY_TO_BE_PROVIDED":
        print("❌ Alpha Vantage APIキーが設定されていません")
        return False
    
    # テスト用にAppleの株価を取得
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "AAPL",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Error Message" in data:
            print(f"❌ APIエラー: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"⚠️  レート制限: {data['Note']}")
            return False
        elif "Time Series (Daily)" in data:
            print("✅ Alpha Vantage API接続成功")
            latest_date = list(data["Time Series (Daily)"].keys())[0]
            latest_price = data["Time Series (Daily)"][latest_date]["4. close"]
            print(f"   📊 AAPL最新価格: ${latest_price} ({latest_date})")
            return True
        else:
            print(f"❌ 予期しないレスポンス: {data}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_news_api():
    """NewsAPI接続テスト"""
    print("\n=== NewsAPI テスト ===")
    
    # 設定読み込み
    with open('config/settings.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_key = config['data_sources']['news_data']['api_key']
    
    if api_key == "API_KEY_TO_BE_PROVIDED":
        print("❌ NewsAPIキーが設定されていません")
        return False
    
    # テスト用にOpenAIのニュースを取得
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "OpenAI",
        "apiKey": api_key,
        "pageSize": 3,
        "sortBy": "publishedAt"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "error":
            print(f"❌ APIエラー: {data.get('message', 'Unknown error')}")
            return False
        elif data.get("status") == "ok":
            articles = data.get("articles", [])
            print(f"✅ NewsAPI接続成功")
            print(f"   📰 OpenAI関連記事: {len(articles)}件取得")
            
            if articles:
                latest_article = articles[0]
                print(f"   📄 最新記事: {latest_article['title'][:50]}...")
                print(f"   📅 投稿日時: {latest_article['publishedAt']}")
            
            return True
        else:
            print(f"❌ 予期しないレスポンス: {data}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_target_stocks():
    """実際の監視対象株式のテスト"""
    print("\n=== 監視対象株式テスト ===")
    
    with open('config/settings.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_key = config['data_sources']['stock_data']['api_key']
    tickers = config['data_sources']['stock_data']['tickers']
    ticker_names = config['data_sources']['stock_data']['ticker_names']
    
    if api_key == "API_KEY_TO_BE_PROVIDED":
        print("❌ Alpha Vantage APIキーが設定されていません")
        return False
    
    success_count = 0
    
    for ticker in tickers:
        print(f"\n📊 {ticker_names.get(ticker, ticker)} ({ticker}) テスト中...")
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "Time Series (Daily)" in data:
                print(f"   ✅ {ticker} データ取得成功")
                success_count += 1
            elif "Note" in data:
                print(f"   ⚠️  {ticker} レート制限中")
            else:
                print(f"   ❌ {ticker} データ取得失敗")
                
        except Exception as e:
            print(f"   ❌ {ticker} エラー: {e}")
    
    print(f"\n📈 株価データ取得結果: {success_count}/{len(tickers)} 成功")
    return success_count > 0

if __name__ == "__main__":
    print(f"🚀 API接続テスト開始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Alpha Vantage テスト
    alpha_vantage_ok = test_alpha_vantage_api()
    
    # NewsAPI テスト  
    news_api_ok = test_news_api()
    
    # 監視対象株式テスト（Alpha Vantage成功時のみ）
    stocks_ok = False
    if alpha_vantage_ok:
        stocks_ok = test_target_stocks()
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("🏁 テスト結果サマリー")
    print(f"   Alpha Vantage API: {'✅ 成功' if alpha_vantage_ok else '❌ 失敗'}")
    print(f"   NewsAPI: {'✅ 成功' if news_api_ok else '❌ 失敗'}")
    print(f"   監視対象株式: {'✅ 成功' if stocks_ok else '❌ 失敗'}")
    
    if alpha_vantage_ok and news_api_ok:
        print("\n🎉 すべてのAPIが正常に動作しています！")
        print("   次のステップ: Teams Chat ID取得")
    else:
        print("\n⚠️  APIキーの設定を確認してください")
        if not alpha_vantage_ok:
            print("   - Alpha Vantage APIキーを config/settings.json に設定")
        if not news_api_ok:
            print("   - NewsAPIキーを config/settings.json に設定") 