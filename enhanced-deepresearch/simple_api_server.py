#!/usr/bin/env python3
"""
簡易版Enhanced DeepResearch API Server
統合テスト用 - 基本的なエンドポイントのモック実装
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import random
import time

app = Flask(__name__)
CORS(app)

# 設定読み込み
settings = {
    "system": {
        "api_port": 5001,
        "host": "127.0.0.1",
        "debug": True
    }
}

try:
    if os.path.exists('config/settings.json'):
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings.update(json.load(f))
        print("✅ 設定ファイル読み込み完了")
except Exception as e:
    print(f"⚠️ 設定読み込み警告: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-simple",
        "components": {
            "reasoning_engine": "mock",
            "verification_engine": "mock", 
            "data_collector": "mock",
            "thinking_visualizer": "mock",
            "data_manager": "mock"
        },
        "message": "Simple API Server for Integration Testing"
    })

@app.route('/api/deepresearch/analyze', methods=['POST'])
def analyze_topic():
    """トピック分析API（モック版）"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        context = data.get('context', {})
        
        if not topic:
            return jsonify({"error": "トピックが指定されていません"}), 400
        
        # モック分析結果を生成
        analysis_id = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        confidence_score = round(0.7 + random.random() * 0.25, 2)
        
        # 簡単な分析プロセスをシミュレート
        time.sleep(1)  # 分析時間をシミュレート
        
        mock_result = {
            "analysis_id": analysis_id,
            "topic": topic,
            "final_answer": f"モック分析結果: {topic}に関する包括的な分析を実施しました。",
            "confidence_score": confidence_score,
            "analysis_time": "1.2秒",
            "verification": {
                "verified": True,
                "verification_score": confidence_score + 0.1,
                "cross_references": 3
            },
            "visualization": {
                "thinking_steps": 4,
                "confidence_trend": [0.3, 0.5, 0.7, confidence_score],
                "phases": ["分解", "推論", "検証", "統合"]
            },
            "status": "completed"
        }
        
        return jsonify(mock_result)
        
    except Exception as e:
        return jsonify({"error": f"分析エラー: {str(e)}"}), 500

@app.route('/api/deepresearch/status', methods=['GET'])
def get_deepresearch_status():
    """DeepResearchシステムステータス（モック版）"""
    return jsonify({
        "system_status": "running",
        "qwen3_engine": "mock_active",
        "last_analysis": 5,
        "total_analyses": 42,
        "average_confidence": 0.82,
        "average_time": 1.5,
        "mock_mode": True
    })

@app.route('/api/news/collect', methods=['POST'])
def collect_news():
    """ニュース収集API（モック版）"""
    try:
        data = request.get_json()
        topics = data.get('topics', ['AI', 'artificial intelligence'])
        
        # モックニュースデータを生成
        mock_news = []
        for i in range(5):
            news_item = {
                "id": f"mock_news_{i+1}",
                "title": f"AI技術の最新動向 #{i+1}",
                "content": f"OpenAIやGoogleが発表した最新の人工知能技術について詳細に解説します... (モックコンテンツ {i+1})",
                "source": random.choice(["TechCrunch", "Reuters", "The Verge", "ArsTechnica"]),
                "url": f"https://example.com/news/{i+1}",
                "published_at": datetime.now().isoformat(),
                "relevance_score": round(0.6 + random.random() * 0.4, 2),
                "data_type": "news",
                "priority": random.choice(["high", "medium", "low"]),
                "review_status": "pending"
            }
            mock_news.append(news_item)
        
        return jsonify({
            "collected_count": len(mock_news),
            "news_data": mock_news,
            "collection_summary": {
                "total_sources": 4,
                "successful_requests": 4,
                "failed_requests": 0,
                "processing_time": "2.3秒"
            },
            "status": "completed"
        })
        
    except Exception as e:
        return jsonify({"error": f"ニュース収集エラー: {str(e)}"}), 500

@app.route('/api/news/analyze', methods=['POST'])
def analyze_news():
    """ニュース分析API（モック版）"""
    try:
        data = request.get_json()
        news_items = data.get('news_items', [])
        
        if not news_items:
            return jsonify({"error": "分析対象のニュースが指定されていません"}), 400
        
        analyzed_results = []
        for news_item in news_items:
            result = {
                "news_id": news_item.get('id', ''),
                "analysis_summary": f"モック分析: {news_item.get('title', '')}の重要度と影響を評価しました。",
                "confidence": round(0.7 + random.random() * 0.25, 2),
                "key_points": [
                    "技術革新への影響度: 高",
                    "市場への影響度: 中",
                    "長期的な重要性: 高"
                ],
                "recommended_priority": random.choice(["high", "medium"])
            }
            analyzed_results.append(result)
        
        return jsonify({
            "analyzed_count": len(analyzed_results),
            "analyses": analyzed_results,
            "status": "completed"
        })
        
    except Exception as e:
        return jsonify({"error": f"ニュース分析エラー: {str(e)}"}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """レポート生成API（モック版）"""
    try:
        data = request.get_json()
        report_config = data.get('config', {})
        
        # レポート生成をシミュレート
        report_id = f"mock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        time.sleep(2)  # レポート生成時間をシミュレート
        
        return jsonify({
            "report_id": report_id,
            "report_path": f"data/{report_id}.html",
            "generation_time": "2.1秒",
            "confidence": 0.88,
            "sections": ["売上分析", "ニュース分析", "イベント情報", "総合評価"],
            "status": "completed",
            "preview_url": f"http://localhost:8002/preview/{report_id}"
        })
        
    except Exception as e:
        return jsonify({"error": f"レポート生成エラー: {str(e)}"}), 500

@app.route('/api/sales/upload', methods=['POST'])
def upload_sales_data():
    """売上データアップロードAPI（モック版）"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "ファイルが指定されていません"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "ファイル名が空です"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "CSVファイルを指定してください"}), 400
        
        # モックアップロード処理
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sales_{timestamp}_{file.filename}"
        
        # モック統計データ
        mock_summary = {
            "rows": random.randint(100, 1000),
            "columns": 8,
            "column_names": ["サービス", "売上", "前年比", "前週比", "地域", "チャネル", "顧客数", "備考"],
            "upload_time": datetime.now().isoformat(),
            "file_size": random.randint(10000, 50000),
            "sales_total": random.randint(1000000, 5000000),
            "growth_rate": round(-10 + random.random() * 20, 1)
        }
        
        return jsonify({
            "upload_id": timestamp,
            "filename": filename,
            "filepath": f"data/uploads/{filename}",
            "data_summary": mock_summary,
            "analysis_preview": {
                "top_service": "Placement",
                "fastest_growth": "Online Platform",
                "total_revenue": f"¥{mock_summary['sales_total']:,}"
            },
            "status": "uploaded"
        })
        
    except Exception as e:
        return jsonify({"error": f"アップロードエラー: {str(e)}"}), 500

@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    """分析履歴取得API（モック版）"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # モック履歴データ
        mock_history = []
        for i in range(min(limit, 8)):
            record = {
                "id": f"analysis_{i+1}",
                "topic": f"AI業界分析 #{i+1}",
                "created_at": datetime.now().isoformat(),
                "confidence_score": round(0.7 + random.random() * 0.25, 2),
                "analysis_time": round(1 + random.random() * 3, 1),
                "data_sources": random.randint(3, 8)
            }
            mock_history.append(record)
        
        return jsonify({
            "history": mock_history,
            "total_count": len(mock_history),
            "mock_mode": True
        })
        
    except Exception as e:
        return jsonify({"error": f"履歴取得エラー: {str(e)}"}), 500

@app.route('/api/analysis/<analysis_id>/visualization', methods=['GET'])
def get_analysis_visualization(analysis_id):
    """分析結果の可視化データ取得（モック版）"""
    try:
        # モック可視化データ
        visualization_data = {
            "analysis_id": analysis_id,
            "topic": "AI業界トレンド分析",
            "confidence_trend": [0.3, 0.5, 0.7, 0.85],
            "phases": ["decomposition", "reasoning", "verification", "synthesis"],
            "final_confidence": 0.85,
            "analysis_time": 2.1,
            "network_data": {
                "nodes": [
                    {"id": "start", "label": "開始", "confidence": 1.0},
                    {"id": "analysis", "label": "分析", "confidence": 0.7},
                    {"id": "verification", "label": "検証", "confidence": 0.8},
                    {"id": "result", "label": "結果", "confidence": 0.85}
                ],
                "links": [
                    {"source": "start", "target": "analysis"},
                    {"source": "analysis", "target": "verification"},
                    {"source": "verification", "target": "result"}
                ]
            },
            "mock_mode": True
        }
        
        return jsonify(visualization_data)
        
    except Exception as e:
        return jsonify({"error": f"可視化データ取得エラー: {str(e)}"}), 500

if __name__ == '__main__':
    port = settings.get('system', {}).get('api_port', 5001)
    host = settings.get('system', {}).get('host', '127.0.0.1')
    debug = settings.get('system', {}).get('debug', True)
    
    print("🚀 Simple Enhanced DeepResearch API Server Starting...")
    print("📡 統合テスト用APIサーバー が起動します")
    print("🔗 エンドポイント:")
    print("   - GET  /api/health               - ヘルスチェック")
    print("   - POST /api/deepresearch/analyze - トピック分析")
    print("   - GET  /api/deepresearch/status  - システムステータス")
    print("   - POST /api/news/collect         - ニュース収集")
    print("   - POST /api/news/analyze         - ニュース分析")
    print("   - POST /api/reports/generate     - レポート生成")
    print("   - POST /api/sales/upload         - 売上データアップロード")
    print("   - GET  /api/analysis/history     - 分析履歴取得")
    print(f"🌐 Server URL: http://{host}:{port}")
    print("🧪 モック実装 - 統合テスト用")
    
    app.run(host=host, port=port, debug=debug) 