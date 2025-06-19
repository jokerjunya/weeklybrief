#!/usr/bin/env python3
"""
テスト用レポート生成スクリプト
実際のAPIデータを使用してMarkdownレポートを作成
"""

import json
import os
import sys
from datetime import datetime, timedelta

# data_processing.pyから必要な関数をインポート
exec(open('scripts/data-processing.py').read())

def generate_test_report():
    """テスト用週次レポートを生成"""
    
    print("🚀 テストレポート生成開始")
    print("=" * 50)
    
    # データ処理インスタンス作成
    processor = WeeklyReportProcessor()
    
    # 1. 売上データ処理
    print("📊 売上データ処理中...")
    sales_data = processor.process_sales_data("/Users/01062544/Downloads/weekly_sales_report.csv")
    print(f"   ✅ 総売上: ¥{sales_data['total_current_sales']:,}")
    
    # 2. 株価データ取得
    print("📈 株価データ取得中...")
    stock_tickers = processor.config["data_sources"]["stock_data"]["tickers"]
    stock_data = processor.fetch_stock_data(stock_tickers)
    
    # エラーのない株価データのみフィルタ
    valid_stocks = {k: v for k, v in stock_data.items() if "error" not in v}
    print(f"   ✅ 取得成功: {len(valid_stocks)}/{len(stock_tickers)} 銘柄")
    
    # 3. ニュースデータ取得
    print("📰 ニュースデータ取得中...")
    keywords = processor.config["data_sources"]["news_data"]["keywords"]
    news_data = processor.fetch_news_data(keywords)
    print(f"   ✅ 記事取得: {len(news_data)}件")
    
    # 4. HTMLテーブル生成
    print("🔧 HTMLテーブル生成中...")
    tables = processor.generate_html_tables(sales_data, valid_stocks)
    
    # 5. スケジュールデータ（サンプル）
    sample_schedule = [
        {"subject": "月曜定例会議", "start": "2024-01-15T09:00:00Z"},
        {"subject": "プロジェクトレビュー", "start": "2024-01-17T14:00:00Z"},
        {"subject": "週次売上レポート確認", "start": "2024-01-19T10:00:00Z"}
    ]
    
    # 6. レポート生成
    report_date = datetime.now().strftime("%Y年%m月%d日")
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ニュースリストをMarkdown形式に変換
    news_markdown = generate_news_markdown(news_data)
    
    # スケジュールをMarkdown形式に変換
    schedule_markdown = generate_schedule_markdown(sample_schedule)
    
    # レポート内容生成
    report_content = f"""# 週次レポート - {report_date}

## 📊 今週のハイライト

- **総売上**: ¥{sales_data['total_current_sales']:,}
- **前年同期比**: {sales_data['yoy_growth_rate']:+.1f}%
- **前週比**: {sales_data['weekly_change']:+.1f}%
- **監視銘柄**: {len(valid_stocks)}銘柄
- **業界ニュース**: {len(news_data)}件

---

## 💰 売上サマリー

### 全体実績
| 項目 | 値 |
|------|------|
| 今週総売上 | ¥{sales_data['total_current_sales']:,} |
| 前年同週売上 | ¥{sales_data['total_previous_year_sales']:,} |
| 前年同期比 | {sales_data['yoy_growth_rate']:+.1f}% |
| 前週比 | {sales_data['weekly_change']:+.1f}% |

### サービス別実績
| サービス名 | 今週売上 | 前年同期比 | 前週比 |
|------------|----------|------------|--------|"""

    # サービス別データを追加
    for service in sales_data['services']:
        yoy_icon = "📈" if service['yoy_change'] > 0 else "📉"
        weekly_icon = "⬆️" if service['weekly_change'] > 0 else "⬇️"
        
        report_content += f"""
| {service['name']} | ¥{service['current_sales']:,} | {yoy_icon} {service['yoy_change']:+.1f}% | {weekly_icon} {service['weekly_change']:+.1f}% |"""

    report_content += f"""

---

## 📈 株価情報

| 銘柄 | 現在価格 | 前日差 | 前日比 |
|------|----------|--------|--------|"""

    # 株価データを追加
    ticker_names = processor.config["data_sources"]["stock_data"]["ticker_names"]
    for ticker, data in valid_stocks.items():
        name = ticker_names.get(ticker, ticker)
        change_icon = "⬆️" if data['change'] > 0 else "⬇️" if data['change'] < 0 else "➡️"
        
        report_content += f"""
| {name} ({ticker}) | ${data['current_price']:.2f} | {change_icon} ${data['change']:+.2f} | {data['change_percent']:+.2f}% |"""

    report_content += f"""

---

## 📰 業界ニュース

{news_markdown}

---

## 📅 今週のスケジュール

{schedule_markdown}

---

## 📋 レポート情報

- **生成日時**: {generation_time}
- **データソース**: 
  - 売上データ（CSV）
  - Alpha Vantage API（株価）
  - NewsAPI（ニュース）
  - Outlook（スケジュール）

---

*このレポートは自動生成されました*
"""

    # ファイル保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"週次レポート_テスト_{timestamp}.md"
    filepath = os.path.join("reports", filename)
    
    # reportsディレクトリ作成
    os.makedirs("reports", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 レポート生成完了: {filepath}")
    
    # 統計情報表示
    print("\n📊 生成レポート統計:")
    print(f"   ファイルサイズ: {len(report_content):,} 文字")
    print(f"   売上データ: {len(sales_data['services'])} サービス")
    print(f"   株価データ: {len(valid_stocks)} 銘柄")
    print(f"   ニュース: {len(news_data)} 記事")
    print(f"   スケジュール: {len(sample_schedule)} 予定")
    
    return filepath

def generate_news_markdown(news_data):
    """ニュースデータをMarkdown形式に変換"""
    if not news_data:
        return "今週は関連ニュースがありませんでした。"
    
    markdown = ""
    current_keyword = None
    
    # キーワード別にグループ化
    news_by_keyword = {}
    for article in news_data:
        keyword = article.get('keyword', 'その他')
        if keyword not in news_by_keyword:
            news_by_keyword[keyword] = []
        news_by_keyword[keyword].append(article)
    
    for keyword, articles in news_by_keyword.items():
        markdown += f"\n### 🔍 {keyword} 関連\n\n"
        
        for i, article in enumerate(articles[:3], 1):  # 各キーワード最大3件
            # 日付をフォーマット
            pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
            date_str = pub_date.strftime("%m/%d %H:%M")
            
            markdown += f"{i}. **[{article['title']}]({article['url']})**\n"
            
            # 日本語要約を優先表示、なければ元の説明文
            if article.get('summary_jp'):
                markdown += f"   🇯🇵 **要約**: {article['summary_jp']}\n"
            elif article.get('description'):
                description = article['description'][:100] + "..." if len(article['description']) > 100 else article['description']
                markdown += f"   📝 {description}\n"
            
            markdown += f"   *{date_str}*\n\n"
    
    return markdown

def generate_schedule_markdown(schedule_data):
    """スケジュールデータをMarkdown形式に変換"""
    if not schedule_data:
        return "今週はスケジュールがありません。"
    
    markdown = ""
    for item in schedule_data:
        # 日付をフォーマット
        start_time = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
        date_str = start_time.strftime("%m/%d (%a) %H:%M")
        
        markdown += f"- **{item['subject']}**\n"
        markdown += f"  📅 {date_str}\n\n"
    
    return markdown

if __name__ == "__main__":
    try:
        report_path = generate_test_report()
        
        print("\n🎉 テストレポート生成成功！")
        print(f"📁 保存場所: {report_path}")
        print("\n📖 レポートを確認してください:")
        print(f"   open {report_path}")
        print("\n🔄 次回実行時は最新データで更新されます")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc() 