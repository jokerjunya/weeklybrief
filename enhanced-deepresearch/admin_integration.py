#!/usr/bin/env python3
"""
Enhanced DeepResearch - 管理者サイト連携API

管理者サイトとEnhanced DeepResearchシステムを連携するAPIエンドポイント群
Flask ベースのRESTful API として実装
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Enhanced DeepResearch コンポーネントのインポート
from reasoning_engine import EnhancedQwen3Llm, ResearchResult
from verification_engine import VerificationEngine
from data_collector import DataCollector
from thinking_visualizer import ThinkingVisualizer
from data_manager import DataManager

# 設定ファイル読み込み
settings = {}
try:
    with open('config/settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    print("✅ 設定ファイル読み込み完了")
except FileNotFoundError:
    print("❌ 設定ファイルが見つかりません: config/settings.json")
    settings = {"system": {"api_port": 5001, "host": "127.0.0.1", "debug": True}}
except Exception as e:
    print(f"❌ 設定読み込みエラー: {e}")
    settings = {"system": {"api_port": 5001, "host": "127.0.0.1", "debug": True}}

app = Flask(__name__)
CORS(app)  # CORS設定（管理者サイトからのアクセス許可）

# Enhanced DeepResearch インスタンス
deepresearch_engine = EnhancedQwen3Llm()
verification_engine = VerificationEngine()
data_collector = DataCollector()
thinking_visualizer = ThinkingVisualizer()
data_manager = DataManager()

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components": {
            "reasoning_engine": "ready",
            "verification_engine": "ready", 
            "data_collector": "ready",
            "thinking_visualizer": "ready",
            "data_manager": "ready"
        }
    })

@app.route('/api/deepresearch/analyze', methods=['POST'])
def analyze_topic():
    """トピック分析API"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        context = data.get('context', {})
        
        if not topic:
            return jsonify({"error": "トピックが指定されていません"}), 400
        
        # 非同期実行をsyncラッパーで実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Deep Research実行
            research_result = loop.run_until_complete(
                deepresearch_engine.deep_research(topic, context)
            )
            
            # 検証実行
            verification_result = loop.run_until_complete(
                verification_engine.verify_research_result(research_result)
            )
            
            # 結果保存
            analysis_id = data_manager.save_analysis_result(research_result, verification_result)
            
            # 思考プロセス可視化
            visualization_data = thinking_visualizer.generate_thinking_flow(research_result)
            
            return jsonify({
                "analysis_id": analysis_id,
                "topic": research_result.topic,
                "final_answer": research_result.final_answer,
                "confidence_score": research_result.confidence_score,
                "analysis_time": research_result.time_taken,
                "verification": verification_result,
                "visualization": visualization_data,
                "status": "completed"
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"error": f"分析エラー: {str(e)}"}), 500

@app.route('/api/deepresearch/status', methods=['GET'])
def get_deepresearch_status():
    """DeepResearchシステムステータス"""
    try:
        # システム統計取得
        stats = data_manager.get_analysis_statistics()
        
        return jsonify({
            "system_status": "running",
            "qwen3_engine": "active",
            "last_analysis": stats.get("recent_analyses_7days", 0),
            "total_analyses": stats.get("total_analyses", 0),
            "average_confidence": stats.get("average_confidence", 0),
            "average_time": stats.get("average_analysis_time", 0)
        })
        
    except Exception as e:
        return jsonify({"error": f"ステータス取得エラー: {str(e)}"}), 500

@app.route('/api/news/collect', methods=['POST'])
def collect_news():
    """ニュース収集API"""
    try:
        data = request.get_json()
        topics = data.get('topics', ['AI', 'artificial intelligence'])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # データ収集実行
            collected_items = loop.run_until_complete(
                data_collector.collect_for_research(topics[0] if topics else "AI news")
            )
            
            # データを管理者向け形式に変換
            news_data = []
            for item in collected_items:
                news_data.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:500] + "..." if len(item.content) > 500 else item.content,
                    "source": item.source,
                    "url": item.url,
                    "published_at": item.published_at.isoformat(),
                    "relevance_score": item.relevance_score,
                    "data_type": item.data_type,
                    "priority": "high" if item.relevance_score > 0.8 else "medium" if item.relevance_score > 0.5 else "low",
                    "review_status": "pending"
                })
            
            return jsonify({
                "collected_count": len(news_data),
                "news_data": news_data,
                "collection_summary": data_collector.get_collection_summary(),
                "status": "completed"
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"error": f"ニュース収集エラー: {str(e)}"}), 500

@app.route('/api/news/analyze', methods=['POST'])
def analyze_news():
    """ニュース分析API"""
    try:
        data = request.get_json()
        news_items = data.get('news_items', [])
        
        if not news_items:
            return jsonify({"error": "分析対象のニュースが指定されていません"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analyzed_results = []
            
            for news_item in news_items:
                # Enhanced DeepResearch で各ニュースを分析
                analysis_topic = f"ニュース分析: {news_item.get('title', '')}"
                context = {
                    "news_content": news_item.get('content', ''),
                    "source": news_item.get('source', ''),
                    "published_at": news_item.get('published_at', '')
                }
                
                research_result = loop.run_until_complete(
                    deepresearch_engine.deep_research(analysis_topic, context)
                )
                
                analyzed_results.append({
                    "news_id": news_item.get('id', ''),
                    "analysis_summary": research_result.final_answer,
                    "confidence": research_result.confidence_score,
                    "key_points": research_result.quality_metrics,
                    "recommended_priority": "high" if research_result.confidence_score > 0.8 else "medium"
                })
            
            return jsonify({
                "analyzed_count": len(analyzed_results),
                "analyses": analyzed_results,
                "status": "completed"
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"error": f"ニュース分析エラー: {str(e)}"}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """レポート生成API"""
    try:
        data = request.get_json()
        report_config = data.get('config', {})
        
        # レポート生成のためのトピック設定
        report_topic = "週次ビジネスレポート生成"
        context = {
            "report_type": "weekly_business",
            "include_sales": report_config.get('include_sales', True),
            "include_news": report_config.get('include_news', True),
            "include_events": report_config.get('include_events', True),
            "target_date": report_config.get('target_date', datetime.now().isoformat())
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # レポート内容を Deep Research で生成
            research_result = loop.run_until_complete(
                deepresearch_engine.deep_research(report_topic, context)
            )
            
            # 思考プロセス可視化レポート生成
            html_report = thinking_visualizer.generate_html_report(research_result)
            
            # レポートファイル保存
            report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            report_path = f"data/{report_id}.html"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            return jsonify({
                "report_id": report_id,
                "report_path": report_path,
                "generation_time": research_result.time_taken,
                "confidence": research_result.confidence_score,
                "status": "completed"
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"error": f"レポート生成エラー: {str(e)}"}), 500

@app.route('/api/sales/upload', methods=['POST'])
def upload_sales_data():
    """売上データアップロードAPI"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "ファイルが指定されていません"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "ファイル名が空です"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "CSVファイルを指定してください"}), 400
        
        # ファイル保存
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sales_{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        
        file.save(filepath)
        
        # CSVデータの基本分析
        import pandas as pd
        try:
            df = pd.read_csv(filepath)
            data_summary = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "upload_time": datetime.now().isoformat(),
                "file_size": os.path.getsize(filepath)
            }
        except Exception as csv_error:
            data_summary = {
                "error": f"CSVファイル解析エラー: {str(csv_error)}",
                "upload_time": datetime.now().isoformat(),
                "file_size": os.path.getsize(filepath)
            }
        
        return jsonify({
            "upload_id": timestamp,
            "filename": filename,
            "filepath": filepath,
            "data_summary": data_summary,
            "status": "uploaded"
        })
        
    except Exception as e:
        return jsonify({"error": f"アップロードエラー: {str(e)}"}), 500

@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    """分析履歴取得API"""
    try:
        limit = request.args.get('limit', 10, type=int)
        records = data_manager.get_recent_analyses(limit)
        
        history_data = []
        for record in records:
            history_data.append({
                "id": record.id,
                "topic": record.topic,
                "created_at": record.created_at.isoformat(),
                "confidence_score": record.confidence_score,
                "analysis_time": record.analysis_time,
                "data_sources": record.data_sources
            })
        
        return jsonify({
            "history": history_data,
            "total_count": len(history_data)
        })
        
    except Exception as e:
        return jsonify({"error": f"履歴取得エラー: {str(e)}"}), 500

@app.route('/api/analysis/<analysis_id>/visualization', methods=['GET'])
def get_analysis_visualization(analysis_id):
    """分析結果の可視化データ取得"""
    try:
        record = data_manager.load_analysis_result(analysis_id)
        if not record:
            return jsonify({"error": "分析結果が見つかりません"}), 404
        
        # 可視化データを再生成（簡略版）
        visualization_data = {
            "analysis_id": analysis_id,
            "topic": record.topic,
            "confidence_trend": [0.3, 0.5, 0.7, record.confidence_score],
            "phases": ["decomposition", "reasoning", "verification", "synthesis"],
            "final_confidence": record.confidence_score,
            "analysis_time": record.analysis_time
        }
        
        return jsonify(visualization_data)
        
    except Exception as e:
        return jsonify({"error": f"可視化データ取得エラー: {str(e)}"}), 500

if __name__ == '__main__':
    import argparse
    
    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='Enhanced DeepResearch API Server')
    parser.add_argument('--port', type=int, default=None, help='APIサーバーのポート番号')
    parser.add_argument('--host', type=str, default=None, help='APIサーバーのホスト')
    args = parser.parse_args()
    
    print("🚀 Enhanced DeepResearch API Server Starting...")
    print("📡 管理者サイト連携API が起動します")
    print("🔗 エンドポイント:")
    print("   - POST /api/deepresearch/analyze - トピック分析")
    print("   - GET  /api/deepresearch/status  - システムステータス")
    print("   - POST /api/news/collect        - ニュース収集")
    print("   - POST /api/news/analyze        - ニュース分析")
    print("   - POST /api/reports/generate    - レポート生成")
    print("   - POST /api/sales/upload        - 売上データアップロード")
    
    # 設定の優先順位: コマンドライン引数 > 設定ファイル > デフォルト値
    port = args.port or settings.get('system', {}).get('api_port', 5001)
    host = args.host or settings.get('system', {}).get('host', '127.0.0.1')
    debug = settings.get('system', {}).get('debug', True)
    
    print(f"🌐 サーバー起動: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug) 