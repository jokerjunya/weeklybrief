#!/usr/bin/env python3
"""
レポート生成専用スクリプト
統合JSONファイルからMarkdown・HTML・Webインターフェースを生成
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 既存のモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
exec(open('scripts/data-processing.py').read())

class ReportGenerator:
    def __init__(self):
        """レポート生成クラス"""
        self.integrated_data_file = "data/integrated_data.json"
        self.processor = None  # 遅延初期化
        
    def _get_processor(self):
        """WeeklyReportProcessorの遅延初期化"""
        if self.processor is None:
            self.processor = WeeklyReportProcessor()
        return self.processor
    
    def load_integrated_data(self):
        """統合データを読み込み"""
        if not os.path.exists(self.integrated_data_file):
            raise FileNotFoundError(f"統合データファイルが見つかりません: {self.integrated_data_file}")
        
        with open(self.integrated_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_all_reports(self, output_prefix="週次レポート_テスト"):
        """
        全フォーマットのレポートを生成
        
        Args:
            output_prefix (str): 出力ファイル名のプレフィックス
        
        Returns:
            dict: 生成されたファイルパス
        """
        print("📊 統合データを読み込み中...")
        data = self.load_integrated_data()
        
        # タイムスタンプ生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        generated_files = {}
        
        # 1. Markdownレポート生成
        print("📝 Markdownレポート生成中...")
        md_content = self._generate_markdown_report(data)
        md_filename = f"reports/{output_prefix}_{timestamp}.md"
        os.makedirs("reports", exist_ok=True)
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        generated_files['markdown'] = md_filename
        print(f"   ✅ {md_filename}")
        
        # 2. Web用HTMLレポート生成
        print("🌐 Web用HTMLレポート生成中...")
        html_content = self._generate_web_html_report(data)
        html_filename = f"web/{output_prefix}_web_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        generated_files['web_html'] = html_filename
        print(f"   ✅ {html_filename}")
        
        # 3. Web用JSONデータ更新
        print("📊 Web用JSONデータ更新中...")
        json_data = self._generate_web_json_data(data)
        json_filename = "web/news-data.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        generated_files['web_json'] = json_filename
        print(f"   ✅ {json_filename}")
        
        return generated_files
    
    def _generate_markdown_report(self, data):
        """Markdownレポート生成"""
        content = []
        
        # ヘッダー
        period = data['metadata']['data_period']
        content.append(f"# PresidentOffice Weekly Brief")
        content.append(f"**期間**: {period}")
        content.append(f"**生成日時**: {data['metadata']['generated_at']}")
        content.append("")
        
        # ビジネス実績セクション
        content.append("## 📊 ビジネス実績")
        content.append("")
        
        for service in data['business_data']['services']:
            name = service['name']
            metric_type = service['metric_type']
            current_value = service['current_value']
            yoy_change = service['yoy_change']
            weekly_change = service['weekly_change']
            
            content.append(f"### {name}")
            
            # 期間情報を追加
            if 'period' in service:
                content.append(f"*期間: {service['period']}*")
                content.append("")
            
            if metric_type == '内定数':
                current_display = f"{current_value:,}件"
            else:
                # Online Platformの場合は詳細表示（万円まで）
                detailed = (name == "Online Platform")
                current_display = self._get_processor().format_japanese_currency(current_value, detailed=detailed)
                if name == "Online Platform":
                    current_display += " ※グロスレベニュー"
            
            content.append(f"- **今週の{metric_type}**: {current_display}")
            
            # 前年同期比
            yoy_icon = "📈" if yoy_change > 0 else "📉" if yoy_change < 0 else "➡️"
            yoy_note = " ※昨年のPPCと比較" if name == "Online Platform" else ""
            content.append(f"- **前年同期比**: {yoy_icon} {yoy_change:+.1f}%{yoy_note}")
            
            # 前週比
            weekly_icon = "📈" if weekly_change > 0 else "📉" if weekly_change < 0 else "➡️"
            content.append(f"- **前週比**: {weekly_icon} {weekly_change:+.1f}%")
            
            # Online Platformの場合はデータリンクを追加
            if name == "Online Platform":
                content.append("")
                content.append("*データを見る: https://idash.sandbox.indeed.net/workspace/88687/queries/2/visualizations/1*")
            
            content.append("")
        
        # 株価情報セクション
        content.append("## 📈 株価情報")
        content.append("")
        
        for ticker, stock_info in data['stock_data'].items():
            if stock_info['status'] == 'success':
                if ticker == 'N225':
                    name = "日経平均株価"
                elif ticker == 'SPY':
                    name = "S&P 500"
                elif ticker == 'RECRUIT':
                    name = "リクルートHD"
                
                if ticker == 'SPY':
                    # S&P 500はポイント表示
                    price_display = f"{stock_info['current_price']:,.0f}"
                else:
                    # その他は円表示
                    price_display = f"¥{stock_info['current_price']:,.0f}"
                
                change_icon = "📈" if stock_info['change'] > 0 else "📉" if stock_info['change'] < 0 else "➡️"
                content.append(f"### {name}")
                content.append(f"- **現在価格**: {price_display}")
                content.append(f"- **変動**: {change_icon} {stock_info['change_percent']:+.2f}%")
                content.append("")
        
        # 業界ニュースセクション
        content.append("## 📰 業界ニュース（まだ試験中）")
        content.append("")
        content.append(f"**週次サマリー**: {data['news_data']['summary']}")
        content.append("")
        
        content.append("### 主要ニュース")
        content.append("")
        
        for i, article in enumerate(data['news_data']['articles'][:8], 1):
            content.append(f"#### {i}. {article['title']}")
            content.append(f"**企業**: {article['company'].title()} | **日付**: {article['published_at']} | **重要度**: {article['score']:.1f}/5.0")
            content.append("")
            content.append(article['summary_jp'])
            content.append("")
            content.append(f"[記事を読む]({article['url']})")
            content.append("")
        
        # スケジュールセクション
        content.append("## 📅 今週のスケジュール")
        content.append("")
        
        for schedule in data['schedule_data']:
            content.append(f"- **{schedule['date']} ({schedule['weekday']}) {schedule['time']}**: {schedule['title']}")
        
        content.append("")
        
        return "\n".join(content)
    
    def _generate_web_html_report(self, data):
        """Web用HTMLレポート生成"""
        # 既存のHTMLテンプレートを使用
        template_path = "templates/weekly-report-template.html"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            # 簡易HTMLテンプレート
            template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>週次レポート</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .positive { color: green; }
        .negative { color: red; }
        .news-item { border-bottom: 1px solid #eee; padding: 10px 0; }
    </style>
</head>
<body>
    <h1>週次レポート</h1>
    <p><strong>期間</strong>: {{PERIOD}}</p>
    <p><strong>生成日時</strong>: {{GENERATED_AT}}</p>
    
    <h2>📊 ビジネス実績</h2>
    {{BUSINESS_DATA}}
    
    <h2>📈 株価情報</h2>
    {{STOCK_DATA}}
    
    <h2>📰 業界ニュース（まだ試験中）</h2>
    <p><strong>週次サマリー</strong>: {{NEWS_SUMMARY}}</p>
    {{NEWS_DATA}}
    
    <h2>📅 今週のスケジュール</h2>
    {{SCHEDULE_DATA}}
</body>
</html>
            """
        
        # テンプレート置換
        period = data['metadata']['data_period']
        generated_at = data['metadata']['generated_at']
        
        # ビジネスデータ
        business_html = []
        for service in data['business_data']['services']:
            name = service['name']
            metric_type = service['metric_type']
            current_value = service['current_value']
            yoy_change = service['yoy_change']
            weekly_change = service['weekly_change']
            
            if metric_type == '内定数':
                current_display = f"{current_value:,}件"
            else:
                # Online Platformの場合は詳細表示（万円まで）
                detailed = (name == "Online Platform")
                current_display = self._get_processor().format_japanese_currency(current_value, detailed=detailed)
                if name == "Online Platform":
                    current_display += " ※グロスレベニュー"
            
            yoy_class = "positive" if yoy_change > 0 else "negative" if yoy_change < 0 else ""
            weekly_class = "positive" if weekly_change > 0 else "negative" if weekly_change < 0 else ""
            yoy_note = " ※昨年のPPCと比較" if name == "Online Platform" else ""
            
            # Online Platformの場合はデータリンクを追加
            data_link = ""
            if name == "Online Platform":
                data_link = '<p style="font-size: 0.9em; color: #666; margin-top: 10px;"><a href="https://idash.sandbox.indeed.net/workspace/88687/queries/2/visualizations/1" target="_blank">データを見る</a></p>'
            
            # 期間情報を追加
            period_info = ""
            if 'period' in service:
                period_info = f'<p style="font-size: 0.9em; color: #666; font-style: italic;">期間: {service["period"]}</p>'
            
            business_html.append(f"""
            <div class="metric">
                <h3>{name}</h3>
                {period_info}
                <p><strong>今週の{metric_type}</strong>: {current_display}</p>
                <p><strong>前年同期比</strong>: <span class="{yoy_class}">{yoy_change:+.1f}%{yoy_note}</span></p>
                <p><strong>前週比</strong>: <span class="{weekly_class}">{weekly_change:+.1f}%</span></p>
                {data_link}
            </div>
            """)
        
        # 株価データ
        stock_html = []
        for ticker, stock_info in data['stock_data'].items():
            if stock_info['status'] == 'success':
                if ticker == 'N225':
                    name = "日経平均株価"
                elif ticker == 'SPY':
                    name = "S&P 500"
                elif ticker == 'RECRUIT':
                    name = "リクルートHD"
                
                if ticker == 'SPY':
                    # S&P 500はポイント表示
                    price_display = f"{stock_info['current_price']:,.0f}"
                else:
                    # その他は円表示
                    price_display = f"¥{stock_info['current_price']:,.0f}"
                
                change_class = "positive" if stock_info['change'] > 0 else "negative" if stock_info['change'] < 0 else ""
                
                stock_html.append(f"""
                <div class="metric">
                    <h3>{name}</h3>
                    <p><strong>現在価格</strong>: {price_display}</p>
                    <p><strong>変動</strong>: <span class="{change_class}">{stock_info['change_percent']:+.2f}%</span></p>
                </div>
                """)
        
        # ニュースデータ
        news_html = []
        for i, article in enumerate(data['news_data']['articles'][:8], 1):
            news_html.append(f"""
            <div class="news-item">
                <h4>{i}. {article['title']}</h4>
                <p><strong>企業</strong>: {article['company'].title()} | 
                   <strong>日付</strong>: {article['published_at']} | 
                   <strong>重要度</strong>: {article['score']:.1f}/5.0</p>
                <p>{article['summary_jp']}</p>
                <p><a href="{article['url']}" target="_blank">記事を読む</a></p>
            </div>
            """)
        
        # スケジュールデータ
        schedule_html = []
        for schedule in data['schedule_data']:
            schedule_html.append(f"<p><strong>{schedule['date']} ({schedule['weekday']}) {schedule['time']}</strong>: {schedule['title']}</p>")
        
        # テンプレート置換
        html_content = template.replace("{{PERIOD}}", period)
        html_content = html_content.replace("{{GENERATED_AT}}", generated_at)
        html_content = html_content.replace("{{BUSINESS_DATA}}", "".join(business_html))
        html_content = html_content.replace("{{STOCK_DATA}}", "".join(stock_html))
        html_content = html_content.replace("{{NEWS_SUMMARY}}", data['news_data']['summary'])
        html_content = html_content.replace("{{NEWS_DATA}}", "".join(news_html))
        html_content = html_content.replace("{{SCHEDULE_DATA}}", "".join(schedule_html))
        
        return html_content
    
    def _generate_web_json_data(self, data):
        """Web用JSONデータ生成"""
        # ローカルサーバー用のJSONデータ形式に変換
        web_data = {
            "metadata": data['metadata'],
            "businessData": {
                "services": []
            },
            "stockData": data['stock_data'],
            "newsData": {
                "summary": data['news_data']['summary'],
                "articles": data['news_data']['articles']
            },
            "scheduleData": data['schedule_data']
        }
        
        # ビジネスデータの変換
        for service in data['business_data']['services']:
            web_service = {
                "name": service['name'],
                "metricType": service['metric_type'],
                "period": service.get('period', ''),
                "currentValue": service['current_value'],
                "yoyChange": service['yoy_change'],
                "weeklyChange": service['weekly_change'],
                "yoyNote": " ※昨年のPPCと比較" if service['name'] == "Online Platform" else ""
            }
            
            if service['metric_type'] == '内定数':
                web_service["displayValue"] = f"{service['current_value']:,}件"
            else:
                # Online Platformの場合は詳細表示（万円まで）
                detailed = (service['name'] == "Online Platform")
                display_value = self._get_processor().format_japanese_currency(service['current_value'], detailed=detailed)
                if service['name'] == "Online Platform":
                    display_value += " ※グロスレベニュー"
                web_service["displayValue"] = display_value
            
            web_data["businessData"]["services"].append(web_service)
        
        return web_data

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='レポート生成スクリプト')
    parser.add_argument('--prefix', default='週次レポート_テスト', help='出力ファイル名のプレフィックス')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    try:
        generated_files = generator.generate_all_reports(output_prefix=args.prefix)
        
        print("\n" + "="*50)
        print("📄 レポート生成完了")
        print("="*50)
        
        for format_type, file_path in generated_files.items():
            print(f"✅ {format_type}: {file_path}")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ レポート生成エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 