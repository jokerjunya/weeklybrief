#!/usr/bin/env python3
"""
詳細データ確認テストスクリプト
"""

exec(open('scripts/data-processing.py').read())

def detailed_data_test():
    """各データソースの詳細確認"""
    processor = WeeklyReportProcessor()
    
    print("📊 詳細データ確認テスト")
    print("=" * 50)
    
    # 1. 株価データの詳細確認
    print("\n📈 株価データ詳細:")
    stock_data = processor.fetch_stock_data(["AAPL", "GOOGL", "MSFT"])
    for ticker, data in stock_data.items():
        if "error" not in data:
            print(f"   {ticker}: ${data['current_price']:.2f} ({data['change_percent']:+.2f}%)")
    
    # 2. ニュースデータの詳細確認
    print("\n📰 ニュースデータ詳細:")
    news_data = processor.fetch_news_data(["OpenAI"])
    for i, article in enumerate(news_data[:3], 1):
        print(f"   {i}. {article['title'][:60]}...")
        print(f"      URL: {article['url']}")
        print(f"      日時: {article['published_at']}")
    
    # 3. 設定ファイル確認
    print("\n⚙️ 設定確認:")
    print(f"   Alpha Vantage API: {'✅ 設定済み' if processor.config['data_sources']['stock_data']['api_key'] != 'API_KEY_TO_BE_PROVIDED' else '❌ 未設定'}")
    print(f"   NewsAPI: {'✅ 設定済み' if processor.config['data_sources']['news_data']['api_key'] != 'API_KEY_TO_BE_PROVIDED' else '❌ 未設定'}")
    print(f"   Teams Chat ID: {'✅ 設定済み' if processor.config['output']['teams']['chat_id'] != 'CHAT_ID_TO_BE_PROVIDED' else '❌ 未設定'}")

if __name__ == "__main__":
    detailed_data_test() 