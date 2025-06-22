#!/usr/bin/env python3
"""
テスト用レポート生成スクリプト
実際のAPIデータを使用してMarkdownレポートを作成
"""

import json
import os
import sys
import asyncio
from datetime import datetime, timedelta

# data_processing.pyから必要な関数をインポート
exec(open('scripts/data-processing.py').read())

async def generate_test_report():
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
    
    # 3. AI駆動ニュースデータ取得
    print("📰 AI駆動ニュースデータ取得中...")
    weekly_summary = ""
    period_description = ""
    
    try:
        # AI駆動ニュースパイプラインを実行
        import sys
        sys.path.append('scripts')
        from ai_news_pipeline import AINewsPipeline
        
        pipeline = AINewsPipeline()
        pipeline_result = await pipeline.run_pipeline(top_n=10)
        
        # パイプライン結果をニュースデータ形式に変換
        if "error" not in pipeline_result:
            news_data = []
            for news in pipeline_result.get("analysis_results", []):
                news_data.append({
                    "title": news.get("title", ""),
                    "url": news.get("url", ""),
                    "keyword": news.get("company_id", "AI業界"),
                    "published_at": news.get("published_at", ""),
                    "summary_jp": news.get("summary_jp", ""),
                    "description": news.get("summary", ""),
                    "score": news.get("score", 5.0)
                })
            
            # AI生成のサマリーと期間情報を取得
            weekly_summary = pipeline_result.get("weekly_summary", "")
            period_info = pipeline_result.get("period_info", {})
            period_description = period_info.get("period_description", "過去1週間")
            
            print(f"   ✅ AI分析記事取得: {len(news_data)}件")
            print(f"   ✅ AI生成サマリー: {len(weekly_summary)}文字")
        else:
            raise Exception(pipeline_result.get("error", "Unknown error"))
            
    except Exception as e:
        print(f"   ⚠️ AI パイプラインエラー: {e}")
        # フォールバック: 従来のニュースAPI
        keywords = processor.config["data_sources"]["news_data"]["keywords"]
        news_data = processor.fetch_news_data(keywords)
        weekly_summary = processor.get_weekly_news_summary(news_data)
        period_description = "過去1週間"
        print(f"   ✅ フォールバック記事取得: {len(news_data)}件")
    
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

### 📊 分析対象期間
**{period_description}**

### 📋 今週のサマリー

{weekly_summary}

---

### 📄 詳細記事

{news_markdown}

---

## 📋 レポート情報

- **生成日時**: {generation_time}
- **分析期間**: {period_description}
- **データソース**: 
  - 売上データ（CSV）
  - Alpha Vantage API（株価）
  - AI駆動ニュース分析（企業別RSS + NewsAPI + AI分析）
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
    
    print(f"✅ レポート生成完了: {filepath}")
    
    # Web用HTML生成
    print("🌐 Web用HTML生成中...")
    web_html_content = generate_web_html(sales_data, valid_stocks, sample_schedule, news_data, weekly_summary, generation_time, period_description)
    
    web_filename = f"週次レポート_web_{timestamp}.html"
    web_filepath = os.path.join("web", web_filename)
    
    with open(web_filepath, 'w', encoding='utf-8') as f:
        f.write(web_html_content)
    
    print(f"✅ Web用HTML生成完了: {web_filepath}")
    
    # Web用JSON更新
    print("📊 Web用JSON更新中...")
    update_web_news_json(news_data)
    print("✅ Web用JSON更新完了")
    
    print("\n" + "=" * 50)
    print("🎉 テストレポート生成完了")
    print("=" * 50)
    print(f"📄 Markdown: {filepath}")
    print(f"🌐 Web HTML: {web_filepath}")
    print(f"📊 Web JSON: web/news-data.json")

def generate_news_markdown(news_data):
    """ニュースデータをMarkdown形式に変換"""
    if not news_data:
        return "今週は重要なニュースはありませんでした。"
    
    markdown = ""
    for i, news in enumerate(news_data, 1):
        # スコア表示（AI分析の場合）
        score_text = ""
        if news.get('score'):
            score_text = f" (重要度: {news['score']:.1f}/10)"
        
        markdown += f"#### {i}. {news['title']}{score_text}\n\n"
        
        # 要約を表示（日本語要約優先）
        summary = news.get('summary_jp', '') or news.get('description', '')
        if summary:
            markdown += f"**要約**: {summary}\n\n"
        
        # URL追加
        if news.get('url'):
            markdown += f"**リンク**: [記事を読む]({news['url']})\n\n"
        
        # 公開日追加（もしあれば）
        if news.get('published_at'):
            try:
                pub_date = datetime.fromisoformat(news['published_at'].replace('Z', '+00:00'))
                formatted_date = pub_date.strftime('%Y年%m月%d日')
                markdown += f"**公開日**: {formatted_date}\n\n"
            except:
                pass
        
        markdown += "---\n\n"
    
    return markdown

def generate_schedule_markdown(schedule_data):
    """スケジュールデータをMarkdown形式に変換"""
    if not schedule_data:
        return "今週の予定はありません。"
    
    markdown = ""
    for event in schedule_data:
        try:
            start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            formatted_date = start_time.strftime('%m月%d日 (%a)')
            formatted_time = start_time.strftime('%H:%M')
            
            markdown += f"- **{formatted_date}** {formatted_time}: {event['subject']}\n"
        except Exception as e:
            markdown += f"- {event['subject']}\n"
    
    return markdown

def generate_web_html(sales_data, stock_data, schedule_data, news_data, weekly_summary, generation_time, period_description="過去1週間"):
    """Web表示用HTML生成"""
    
    # スケジュールHTML生成
    schedule_html = generate_schedule_html(schedule_data)
    
    # ニュースHTML生成（重要度スコア付き）
    news_html = ""
    for i, news in enumerate(news_data, 1):
        score_badge = ""
        if news.get('score'):
            score_badge = f'<span class="score-badge">重要度: {news["score"]:.1f}</span>'
        
        # 要約を表示（80-120文字程度に調整）
        summary = news.get('summary_jp', '') or news.get('description', '')
        if len(summary) > 120:
            summary = summary[:117] + "..."
        
        news_html += f"""
        <div class="news-item">
            <h4>{news['title']} {score_badge}</h4>
            <p class="news-summary">{summary}</p>
            <a href="{news.get('url', '#')}" target="_blank" class="news-link">記事を読む →</a>
        </div>
        """
    
    # 売上データHTML生成
    sales_html = ""
    for service in sales_data['services']:
        yoy_class = "positive" if service['yoy_change'] > 0 else "negative"
        weekly_class = "positive" if service['weekly_change'] > 0 else "negative"
        
        if service.get('metric_type') == '内定数':
            current_display = f"{service['current_value']:,}件"
        else:
            current_display = f"¥{service['current_value']:.1f}億円"
        
        sales_html += f"""
        <div class="metric-card">
            <h3>{service['name']}</h3>
            <p class="metric-type">{service['metric_type']}</p>
            <p class="metric-value">{current_display}</p>
            <div class="metric-changes">
                <span class="change {yoy_class}">前年同期比: {service['yoy_change']:+.1f}%</span>
                <span class="change {weekly_class}">前週比: {service['weekly_change']:+.1f}%</span>
            </div>
        </div>
        """
    
    # 株価データHTML生成
    stock_html = ""
    ticker_names = {
        "N225": "日経平均株価",
        "SPY": "S&P 500 ETF", 
        "RCRUY": "リクルートHD (ADR)"
    }
    
    for ticker, data in stock_data.items():
        name = ticker_names.get(ticker, ticker)
        change_class = "positive" if data['change'] > 0 else "negative" if data['change'] < 0 else "neutral"
        
        stock_html += f"""
        <div class="stock-card">
            <h3>{name}</h3>
            <p class="stock-symbol">{ticker}</p>
            <p class="stock-price">${data['current_price']:.2f}</p>
            <span class="stock-change {change_class}">{data['change']:+.2f} ({data['change_percent']:+.2f}%)</span>
        </div>
        """
    
    # HTML全体を生成
    html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>週次レポート - AI駆動分析</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .change.positive {{ color: #27ae60; }}
        .change.negative {{ color: #e74c3c; }}
        .stock-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .stock-card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }}
        .news-item {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #e74c3c; }}
        .news-summary {{ color: #555; line-height: 1.6; margin: 10px 0; }}
        .news-link {{ color: #3498db; text-decoration: none; font-weight: bold; }}
        .news-link:hover {{ text-decoration: underline; }}
        .score-badge {{ background: #f39c12; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }}
        .summary-box {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60; }}
        .period-info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center; font-weight: bold; color: #1976d2; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 14px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 週次レポート - AI駆動分析</h1>
        
        <div class="period-info">
            📅 分析対象期間: {period_description}
        </div>
        
        <h2>💼 ビジネス実績</h2>
        <div class="metrics-grid">
            {sales_html}
        </div>
        
        <h2>📈 株価情報</h2>
        <div class="stock-grid">
            {stock_html}
        </div>
        
        <h2>📅 今週のスケジュール</h2>
        {schedule_html}
        
        <h2>📰 AI業界ニュース</h2>
        
        <div class="summary-box">
            <h3>📋 今週のサマリー</h3>
            <p>{weekly_summary}</p>
        </div>
        
        <h3>📄 詳細記事</h3>
        {news_html}
        
        <div class="footer">
            <p>🤖 生成日時: {generation_time} | AI駆動ニュース分析システム</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content

def update_web_news_json(news_data):
    """Web用のニュースJSONファイルを更新"""
    web_news_data = []
    
    for news in news_data:
        web_news_data.append({
            "title": news.get('title', ''),
            "description": news.get('summary_jp', '') or news.get('description', ''),
            "url": news.get('url', ''),
            "company": news.get('keyword', 'unknown'),
            "publishedAt": news.get('published_at', ''),
            "score": news.get('score', 0)
        })
    
    # web/news-data.jsonに保存
    web_dir = "web"
    os.makedirs(web_dir, exist_ok=True)
    
    json_path = os.path.join(web_dir, "news-data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(web_news_data, f, ensure_ascii=False, indent=2)

def generate_schedule_html(schedule_data):
    """スケジュールをHTML形式に変換"""
    if not schedule_data:
        return "<p>今週の予定はありません。</p>"
    
    html = "<div class='schedule-list'>"
    for event in schedule_data:
        try:
            start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            formatted_date = start_time.strftime('%m月%d日 (%a)')
            formatted_time = start_time.strftime('%H:%M')
            
            html += f"""
            <div class="schedule-item" style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #9b59b6;">
                <strong>{formatted_date} {formatted_time}</strong>: {event['subject']}
            </div>
            """
        except Exception as e:
            html += f"""
            <div class="schedule-item" style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px;">
                {event['subject']}
            </div>
            """
    
    html += "</div>"
    return html

def main():
    """メイン実行関数"""
    asyncio.run(generate_test_report())

if __name__ == "__main__":
    main() 