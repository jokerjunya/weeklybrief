#!/usr/bin/env python3
"""
AI駆動ニュースパイプライン統合スクリプト
企業ニュース収集 → AI分析 → 日本語要約 → レポート生成
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from company_news_collector import CompanyNewsCollector
from news_analyzer import analyze_company_news, NewsAnalyzer, EfficientNewsAnalyzer

class AINewsPipeline:
    def __init__(self, config_path="config/target_companies.yaml"):
        """
        パイプライン初期化
        
        Args:
            config_path: 企業設定ファイルのパス
        """
        self.config_path = config_path
        self.collector = CompanyNewsCollector(config_path)
        self.analyzer = EfficientNewsAnalyzer()
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        
    async def run_pipeline(self, top_n: int = 10) -> dict:
        """パイプライン実行"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            print("🚀 AI駆動ニュースパイプライン開始")
            print("=" * 50)
            
            # 1. ニュース収集
            print("📰 企業別ニュース収集中...")
            raw_news = self.collector.collect_all_company_news(days_back=7)
            print(f"✅ 収集完了: {len(raw_news)}件")
            
            if not raw_news:
                print("❌ ニュースが収集できませんでした")
                return {"error": "No news collected"}
            
            # 2. AI分析・重要度判定
            print("\n🤖 AI分析・重要度判定中...")
            analyzed_news = await self.analyzer.analyze_news_efficient(raw_news)
            
            # 3. 上位ニュース選出
            top_news = sorted(analyzed_news, key=lambda x: x.get('score', 0), reverse=True)[:top_n]
            
            # 4. 対象期間情報取得
            period_info = self.analyzer.get_analysis_period()
            
            # 5. 週次サマリー生成
            print("\n📝 週次サマリー生成中...")
            weekly_summary = await self.analyzer.generate_weekly_summary(top_news)
            
            # 6. 統計情報計算
            stats = self.calculate_stats(analyzed_news, top_news)
            
            # 7. 結果構造化
            result = {
                "generated_at": datetime.now().isoformat(),
                "period_info": period_info,
                "weekly_summary": weekly_summary,
                "total_items": len(analyzed_news),
                "top_items": len(top_news),
                "statistics": stats,
                "analysis_results": top_news
            }
            
            # 8. ファイル出力
            await self.save_results(result, timestamp)
            
            # 9. 結果表示
            self.display_results(result)
            
            return result
            
        except Exception as e:
            print(f"❌ パイプライン実行エラー: {e}")
            return {"error": str(e)}

    def calculate_stats(self, all_news: list, top_news: list) -> dict:
        """統計情報を計算"""
        if not all_news:
            return {}
        
        # 企業別統計
        company_stats = {}
        source_stats = {}
        
        for news in all_news:
            company = news.get('company_id', 'unknown')
            source = news.get('source_type', 'unknown')
            
            company_stats[company] = company_stats.get(company, 0) + 1
            source_stats[source] = source_stats.get(source, 0) + 1
        
        # スコア統計
        scores = [news.get('score', 0) for news in all_news if news.get('score')]
        avg_score = sum(scores) / len(scores) if scores else 0
        top_avg_score = sum(news.get('score', 0) for news in top_news) / len(top_news) if top_news else 0
        
        return {
            "selection_rate": f"{(len(top_news)/len(all_news)*100):.1f}%" if all_news else "0%",
            "average_score": round(avg_score, 2),
            "top_average_score": round(top_avg_score, 2),
            "company_distribution": dict(sorted(company_stats.items(), key=lambda x: x[1], reverse=True)),
            "source_distribution": dict(sorted(source_stats.items(), key=lambda x: x[1], reverse=True))
        }

    async def save_results(self, result: dict, timestamp: str):
        """結果をファイルに保存"""
        # JSON形式で保存
        json_file = self.output_dir / f"ai_news_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON保存: {json_file}")
        
        # Markdown形式で保存
        md_file = self.output_dir / f"ai_news_report_{timestamp}.md"
        markdown_content = self.generate_markdown_report(result)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"📄 Markdown保存: {md_file}")
        
        # Web用JSON更新
        web_json = Path("web/news-data.json")
        web_data = []
        for news in result.get('analysis_results', []):
            web_data.append({
                "title": news.get('title', ''),
                "description": news.get('summary_jp', ''),
                "url": news.get('url', ''),
                "company": news.get('company_id', 'unknown'),
                "publishedAt": news.get('published_at', ''),
                "score": news.get('score', 0)
            })
        
        with open(web_json, 'w', encoding='utf-8') as f:
            json.dump(web_data, f, ensure_ascii=False, indent=2)
        print(f"🌐 Web用JSON更新: {web_json}")

    def generate_markdown_report(self, result: dict) -> str:
        """Markdownレポートを生成"""
        period_info = result.get('period_info', {})
        content = f"""# AI駆動ニュース分析レポート

## 基本情報
- **生成日時**: {result.get('generated_at', '')}
- **分析対象期間**: {period_info.get('period_description', '過去1週間')}
- **収集件数**: {result.get('total_items', 0)}件
- **選出件数**: {result.get('top_items', 0)}件

## 今週のサマリー

{result.get('weekly_summary', '今週のサマリーは生成されませんでした。')}

## 統計情報

### 全体統計
- **選出率**: {result.get('statistics', {}).get('selection_rate', 'N/A')}
- **平均重要度**: {result.get('statistics', {}).get('average_score', 'N/A')}/10
- **上位平均重要度**: {result.get('statistics', {}).get('top_average_score', 'N/A')}/10

### 企業別分布
"""
        
        # 企業別統計
        company_dist = result.get('statistics', {}).get('company_distribution', {})
        for company, count in company_dist.items():
            content += f"- **{company}**: {count}件\n"
        
        content += "\n### 情報源別分布\n"
        source_dist = result.get('statistics', {}).get('source_distribution', {})
        for source, count in source_dist.items():
            content += f"- **{source}**: {count}件\n"
        
        content += "\n## 重要ニュース\n\n"
        
        # トップニュース
        for i, news in enumerate(result.get('analysis_results', []), 1):
            content += f"### {i}. {news.get('title', '')}\n\n"
            content += f"- **重要度**: {news.get('score', 0):.1f}/10\n"
            content += f"- **企業**: {news.get('company_id', 'unknown')}\n"
            content += f"- **情報源**: {news.get('source_type', 'unknown')}\n"
            content += f"- **URL**: {news.get('url', '')}\n"
            content += f"- **要約**: {news.get('summary_jp', '')}\n\n"
            if news.get('summary'):
                content += f"**詳細**: {news.get('summary', '')}\n\n"
            content += "---\n\n"
        
        return content

    def display_results(self, result: dict):
        """結果を表示"""
        print("\n" + "=" * 50)
        print("📊 AI分析結果サマリー")
        print("=" * 50)
        
        period_info = result.get('period_info', {})
        print(f"📅 分析期間: {period_info.get('period_description', '過去1週間')}")
        print(f"📰 総収集数: {result.get('total_items', 0)}件")
        print(f"⭐ 選出数: {result.get('top_items', 0)}件")
        
        stats = result.get('statistics', {})
        print(f"📈 選出率: {stats.get('selection_rate', 'N/A')}")
        print(f"🎯 平均重要度: {stats.get('top_average_score', 'N/A')}/10")
        
        print(f"\n📝 今週のサマリー:")
        print(f"{result.get('weekly_summary', '')}")
        
        print(f"\n🏆 トップ{len(result.get('analysis_results', []))}ニュース:")
        for i, news in enumerate(result.get('analysis_results', []), 1):
            print(f"{i}. {news.get('title', '')} (重要度: {news.get('score', 0):.1f})")
            print(f"   企業: {news.get('company_id', '')} | 要約: {news.get('summary_jp', '')}")
        
        print("\n✅ パイプライン完了")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="AI駆動ニュースパイプライン")
    parser.add_argument("--top", type=int, default=10, help="上位何件を選出するか")
    parser.add_argument("--config", type=str, default="config/target_companies.yaml", help="設定ファイルパス")
    
    args = parser.parse_args()
    
    # パイプライン実行
    pipeline = AINewsPipeline(config_path=args.config)
    result = asyncio.run(pipeline.run_pipeline(top_n=args.top))
    
    # 終了コード
    exit_code = 0 if result["status"] == "success" else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 