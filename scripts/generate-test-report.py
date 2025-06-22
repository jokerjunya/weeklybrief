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
    
    # 1. ビジネスデータ処理（事業別メトリクス）
    print("📊 ビジネスデータ処理中...")
    print("   📋 Placement（内定数）+ Online Platform（売上）を統合")
    sales_data = processor.process_sales_data()
    
    online_platform = next((s for s in sales_data['services'] if s['name'] == 'Online Platform'), None)
    placement = next((s for s in sales_data['services'] if s['name'] == 'Placement'), None)
    
    if online_platform:
        print(f"   ✅ Online Platform売上: ¥{online_platform['current_value']:,}")
    if placement:
        print(f"   ✅ Placement内定数: {placement['current_value']:,}件")
    
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
    
    # 3.5. 週間ニュースサマリー生成
    print("📋 週間ニュースサマリー生成中...")
    weekly_summary = processor.get_weekly_news_summary(news_data)
    print(f"   ✅ サマリー生成完了: {len(weekly_summary)}文字")
    
    # 4. HTMLテーブル生成
    print("🔧 HTMLテーブル生成中...")
    tables = processor.generate_html_tables(sales_data, valid_stocks)
    
    # 5. スケジュールデータ（6月実スケジュール）
    sample_schedule = [
        {"subject": "JP HR Steering Committee", "start": "2025-06-24T09:00:00Z"},
        {"subject": "株主総会オンサイト", "start": "2025-06-26T10:00:00Z"},
        {"subject": "Bi-weekly SLT Meeting", "start": "2025-06-27T14:00:00Z"}
    ]
    
    # 6. レポート生成
    report_date = datetime.now().strftime("%Y年%m月%d日")
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ニュースリストをMarkdown形式に変換
    news_markdown = generate_news_markdown(news_data)
    
    # スケジュールをMarkdown形式に変換
    schedule_markdown = generate_schedule_markdown(sample_schedule)
    
    # ハイライト計算（Online Platformのみ）
    online_platform = next((s for s in sales_data['services'] if s['name'] == 'Online Platform'), None)
    placement = next((s for s in sales_data['services'] if s['name'] == 'Placement'), None)
    
    # レポート内容生成
    report_content = f"""# 週次レポート - {report_date}

## 💼 ビジネス実績

| サービス名 | 指標 | 今週実績 | 前年同期比 | 前週比 |
|------------|------|----------|------------|--------|"""

    # サービス別データを追加
    for service in sales_data['services']:
        yoy_icon = "📈" if service['yoy_change'] > 0 else "📉"
        weekly_icon = "⬆️" if service['weekly_change'] > 0 else "⬇️"
        
        # メトリックタイプに応じて値をフォーマット
        if service.get('metric_type') == '内定数':
            current_display = f"{service['current_value']:,}件"
        else:  # 売上 - 億円表示を使用
            current_display = processor.format_japanese_currency(service['current_value'])
        
        report_content += f"""
| {service['name']} | {service['metric_type']} | {current_display} | {yoy_icon} {service['yoy_change']:+.1f}% | {weekly_icon} {service['weekly_change']:+.1f}% |"""

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

## 📅 今週のスケジュール

{schedule_markdown}

---

## 📰 業界ニュース

### 📋 今週のサマリー

{weekly_summary}

---

### 📄 詳細記事

{news_markdown}

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
    
    # 7. Web HTML生成
    print("🌐 Web HTML生成中...")
    web_filepath = generate_web_html(sales_data, valid_stocks, sample_schedule, news_data, weekly_summary, generation_time)
    print(f"🌐 Web HTML生成完了: {web_filepath}")
    
    # 統計情報表示
    print("\n📊 生成レポート統計:")
    print(f"   ファイルサイズ: {len(report_content):,} 文字")
    print(f"   売上データ: {len(sales_data['services'])} サービス")
    print(f"   株価データ: {len(valid_stocks)} 銘柄")
    print(f"   ニュース: {len(news_data)} 記事")
    print(f"   スケジュール: {len(sample_schedule)} 予定")
    
    return filepath, web_filepath

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
    """スケジュールデータをMarkdown形式に変換（時間なし）"""
    if not schedule_data:
        return "今週はスケジュールがありません。"
    
    markdown = ""
    for item in schedule_data:
        # 日付のみフォーマット（時間は削除）
        start_time = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
        date_str = start_time.strftime("%m/%d (%a)")
        
        markdown += f"- **{item['subject']}**\n"
        markdown += f"  📅 {date_str}\n\n"
    
    return markdown

def generate_web_html(sales_data, stock_data, schedule_data, news_data, weekly_summary, generation_time):
    """Web HTML ファイルを生成（履歴管理対応）"""
    
    # 現在のindex.htmlをベースとして読み込み
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 日付を更新
    today = datetime.now().strftime("%Y年%m月%d日")
    html_content = html_content.replace('2025年06月22日', today)
    
    # スケジュール部分を更新（曜日優先表示に変更）
    schedule_html = generate_schedule_html(schedule_data)
    
    # スケジュール部分を置換
    import re
    schedule_pattern = r'(<div class="schedule-list">)(.*?)(</div>\s*</section>)'
    html_content = re.sub(schedule_pattern, f'\\1{schedule_html}\\3', html_content, flags=re.DOTALL)
    
    # 履歴ファイル生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    web_filename = f"週次レポート_web_{timestamp}.html"
    web_filepath = os.path.join("web", web_filename)
    
    # webディレクトリ作成
    os.makedirs("web", exist_ok=True)
    
    # 履歴ファイル保存
    with open(web_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 最新版のindex.htmlも更新
    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return web_filepath

def generate_schedule_html(schedule_data):
    """スケジュールデータをHTML形式に変換（曜日優先表示）"""
    if not schedule_data:
        return '<p>今週はスケジュールがありません。</p>'
    
    html = ""
    weekday_jp = {
        'Monday': '月', 'Tuesday': '火', 'Wednesday': '水', 
        'Thursday': '木', 'Friday': '金', 'Saturday': '土', 'Sunday': '日'
    }
    
    for item in schedule_data:
        start_time = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
        weekday = weekday_jp.get(start_time.strftime('%A'), start_time.strftime('%a'))
        date_str = start_time.strftime('%-m/%-d')  # 6/24 形式
        
        # 重要度に応じてステータスを設定
        status_class = "important" if "株主総会" in item['subject'] else "upcoming"
        status_icon = "fa-star" if "株主総会" in item['subject'] else "fa-circle"
        
        html += f'''
                        <div class="schedule-item">
                            <div class="schedule-date">
                                <span class="date-weekday-large">{weekday}</span>
                                <span class="date-small">{date_str}</span>
                            </div>
                            <div class="schedule-content">
                                <h3>{item['subject']}</h3>
                            </div>
                            <div class="schedule-status {status_class}">
                                <i class="fas {status_icon}"></i>
                            </div>
                        </div>'''
    
    return html

if __name__ == "__main__":
    try:
        report_path, web_path = generate_test_report()
        
        print("\n🎉 テストレポート生成成功！")
        print(f"📁 Markdownレポート: {report_path}")
        print(f"🌐 Webレポート: {web_path}")
        print("\n📖 レポートを確認してください:")
        print(f"   open {report_path}")
        print(f"   open {web_path}")
        print("\n🔄 次回実行時は最新データで更新されます")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc() 