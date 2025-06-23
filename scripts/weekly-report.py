#!/usr/bin/env python3
"""
週次レポート統合スクリプト
データ収集 → レポート生成の一連の流れを実行
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime

# 既存のモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# データ収集とレポート生成のクラスをインポート
exec(open('scripts/data-collector.py').read())
exec(open('scripts/report-generator.py').read())

class WeeklyReportPipeline:
    def __init__(self, cache_hours=6):
        """
        週次レポートパイプライン
        
        Args:
            cache_hours (int): データキャッシュ有効時間
        """
        self.collector = DataCollector(cache_hours=cache_hours)
        self.generator = ReportGenerator()
    
    async def run_full_pipeline(self, force_refresh=False, output_prefix="週次レポート_テスト"):
        """
        完全なパイプラインを実行
        
        Args:
            force_refresh (bool): データ強制更新フラグ
            output_prefix (str): レポートファイル名プレフィックス
        
        Returns:
            dict: 実行結果
        """
        print("🚀 週次レポートパイプライン開始")
        print("="*60)
        
        start_time = datetime.now()
        
        try:
            # Phase 1: データ収集
            print("\n📊 Phase 1: データ収集")
            print("-" * 30)
            
            data = await self.collector.collect_all_data(force_refresh=force_refresh)
            
            # Phase 2: レポート生成
            print("\n📄 Phase 2: レポート生成")
            print("-" * 30)
            
            generated_files = self.generator.generate_all_reports(output_prefix=output_prefix)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 結果サマリー
            print("\n" + "="*60)
            print("✅ 週次レポートパイプライン完了")
            print("="*60)
            print(f"⏱️  実行時間: {duration:.2f}秒")
            print(f"📅 データ期間: {data['metadata']['data_period']}")
            print(f"📊 ビジネスサービス: {len(data['business_data']['services'])}件")
            print(f"📈 株価銘柄: {len(data['stock_data'])}件")
            print(f"📰 ニュース記事: {len(data['news_data']['articles'])}件")
            print(f"📅 スケジュール: {len(data['schedule_data'])}件")
            print("\n📄 生成ファイル:")
            for format_type, file_path in generated_files.items():
                print(f"   ✅ {format_type}: {file_path}")
            print("="*60)
            
            return {
                "success": True,
                "duration": duration,
                "data_summary": {
                    "period": data['metadata']['data_period'],
                    "business_services": len(data['business_data']['services']),
                    "stock_tickers": len(data['stock_data']),
                    "news_articles": len(data['news_data']['articles']),
                    "schedule_items": len(data['schedule_data'])
                },
                "generated_files": generated_files
            }
            
        except Exception as e:
            print(f"\n❌ パイプライン実行エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }

async def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='週次レポート統合パイプライン')
    parser.add_argument('--force', action='store_true', help='データを強制更新')
    parser.add_argument('--cache-hours', type=int, default=6, help='キャッシュ有効時間（時間）')
    parser.add_argument('--prefix', default='週次レポート_テスト', help='レポートファイル名プレフィックス')
    parser.add_argument('--data-only', action='store_true', help='データ収集のみ実行')
    parser.add_argument('--report-only', action='store_true', help='レポート生成のみ実行')
    
    args = parser.parse_args()
    
    if args.data_only and args.report_only:
        print("❌ --data-only と --report-only は同時に指定できません")
        sys.exit(1)
    
    try:
        if args.data_only:
            # データ収集のみ
            print("📊 データ収集のみ実行")
            collector = DataCollector(cache_hours=args.cache_hours)
            data = await collector.collect_all_data(force_refresh=args.force)
            print("✅ データ収集完了")
            
        elif args.report_only:
            # レポート生成のみ
            print("📄 レポート生成のみ実行")
            generator = ReportGenerator()
            generated_files = generator.generate_all_reports(output_prefix=args.prefix)
            print("✅ レポート生成完了")
            
        else:
            # 完全パイプライン
            pipeline = WeeklyReportPipeline(cache_hours=args.cache_hours)
            result = await pipeline.run_full_pipeline(
                force_refresh=args.force,
                output_prefix=args.prefix
            )
            
            if not result["success"]:
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 