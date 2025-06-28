#!/usr/bin/env python3
"""
Enhanced DeepResearch - データ管理エンジン

既存のdata-processing.pyの機能を統合し、以下を提供：
- データ正規化・変換
- 分析結果の永続化
- キャッシュ管理
- JSON/CSV エクスポート
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import json
import csv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
import pickle
import hashlib

@dataclass
class AnalysisRecord:
    """分析記録"""
    id: str
    topic: str
    analysis_result: Dict[str, Any]
    verification_result: Dict[str, Any]
    created_at: datetime
    confidence_score: float
    analysis_time: float
    data_sources: List[str]

class DataManager:
    """
    データ管理エンジン
    
    分析結果の保存、管理、エクスポート機能を提供
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "enhanced_deepresearch.db")
        self.cache_dir = os.path.join(data_dir, "cache")
        
        # ディレクトリ作成
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # データベース初期化
        self._init_database()
    
    def _init_database(self):
        """データベース初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_records (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    analysis_result TEXT NOT NULL,
                    verification_result TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    analysis_time REAL NOT NULL,
                    data_sources TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS thinking_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    step_id INTEGER NOT NULL,
                    phase TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_records (id)
                )
            """)
    
    def save_analysis_result(
        self, 
        research_result,
        verification_result: Dict[str, Any] = None
    ) -> str:
        """分析結果を保存"""
        analysis_id = self._generate_analysis_id(research_result.topic)
        
        record = AnalysisRecord(
            id=analysis_id,
            topic=research_result.topic,
            analysis_result=self._serialize_research_result(research_result),
            verification_result=verification_result or {},
            created_at=datetime.now(),
            confidence_score=research_result.confidence_score,
            analysis_time=research_result.time_taken,
            data_sources=research_result.sources_analyzed
        )
        
        # データベースに保存
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analysis_records 
                (id, topic, analysis_result, verification_result, created_at, 
                 confidence_score, analysis_time, data_sources)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.topic,
                json.dumps(record.analysis_result, ensure_ascii=False),
                json.dumps(record.verification_result, ensure_ascii=False),
                record.created_at.isoformat(),
                record.confidence_score,
                record.analysis_time,
                json.dumps(record.data_sources)
            ))
            
            # 思考ステップも保存
            for step in research_result.thinking_steps:
                conn.execute("""
                    INSERT INTO thinking_steps 
                    (analysis_id, step_id, phase, confidence, input_data, output_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    step.step_id,
                    step.phase,
                    step.confidence,
                    step.input_data,
                    step.output_data,
                    step.timestamp.isoformat()
                ))
        
        print(f"💾 分析結果を保存: {analysis_id}")
        return analysis_id
    
    def load_analysis_result(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """分析結果を読み込み"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM analysis_records WHERE id = ?
            """, (analysis_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return AnalysisRecord(
                id=row[0],
                topic=row[1],
                analysis_result=json.loads(row[2]),
                verification_result=json.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                confidence_score=row[5],
                analysis_time=row[6],
                data_sources=json.loads(row[7])
            )
    
    def get_recent_analyses(self, limit: int = 10) -> List[AnalysisRecord]:
        """最近の分析結果を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM analysis_records 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            records = []
            for row in cursor.fetchall():
                record = AnalysisRecord(
                    id=row[0],
                    topic=row[1],
                    analysis_result=json.loads(row[2]),
                    verification_result=json.loads(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    confidence_score=row[5],
                    analysis_time=row[6],
                    data_sources=json.loads(row[7])
                )
                records.append(record)
            
            return records
    
    def export_to_json(self, analysis_id: str, output_path: str) -> bool:
        """JSON形式でエクスポート"""
        try:
            record = self.load_analysis_result(analysis_id)
            if not record:
                return False
            
            export_data = {
                "analysis_record": asdict(record),
                "export_timestamp": datetime.now().isoformat(),
                "format_version": "1.0"
            }
            
            # datetime オブジェクトを文字列に変換
            export_data["analysis_record"]["created_at"] = record.created_at.isoformat()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📤 JSON エクスポート完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ JSON エクスポートエラー: {e}")
            return False
    
    def export_summary_to_csv(self, output_path: str) -> bool:
        """サマリーをCSV形式でエクスポート"""
        try:
            records = self.get_recent_analyses(limit=100)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # ヘッダー
                writer.writerow([
                    "ID", "トピック", "作成日時", "信頼度", "分析時間(秒)",
                    "データソース数", "最終回答"
                ])
                
                # データ
                for record in records:
                    final_answer = record.analysis_result.get("final_answer", "")
                    if len(final_answer) > 100:
                        final_answer = final_answer[:97] + "..."
                    
                    writer.writerow([
                        record.id,
                        record.topic,
                        record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        f"{record.confidence_score:.2f}",
                        f"{record.analysis_time:.2f}",
                        len(record.data_sources),
                        final_answer
                    ])
            
            print(f"📊 CSV エクスポート完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ CSV エクスポートエラー: {e}")
            return False
    
    def cache_data(self, key: str, data: Any, ttl_hours: int = 24) -> bool:
        """データをキャッシュ"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            cache_data = {
                "data": data,
                "cached_at": datetime.now(),
                "ttl_hours": ttl_hours
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            print(f"❌ キャッシュエラー: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """キャッシュからデータを取得"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # TTL チェック
            cached_at = cache_data["cached_at"]
            ttl_hours = cache_data["ttl_hours"]
            expires_at = cached_at.replace(
                hour=cached_at.hour + ttl_hours
            )
            
            if datetime.now() > expires_at:
                os.remove(cache_file)
                return None
            
            return cache_data["data"]
            
        except Exception as e:
            print(f"❌ キャッシュ読み込みエラー: {e}")
            return None
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """分析統計を取得"""
        with sqlite3.connect(self.db_path) as conn:
            # 基本統計
            cursor = conn.execute("SELECT COUNT(*) FROM analysis_records")
            total_analyses = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT AVG(confidence_score) FROM analysis_records")
            avg_confidence = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("SELECT AVG(analysis_time) FROM analysis_records")
            avg_time = cursor.fetchone()[0] or 0
            
            # 最近の活動
            cursor = conn.execute("""
                SELECT COUNT(*) FROM analysis_records 
                WHERE created_at > datetime('now', '-7 days')
            """)
            recent_analyses = cursor.fetchone()[0]
            
            return {
                "total_analyses": total_analyses,
                "average_confidence": avg_confidence,
                "average_analysis_time": avg_time,
                "recent_analyses_7days": recent_analyses,
                "database_path": self.db_path,
                "cache_directory": self.cache_dir
            }
    
    def _generate_analysis_id(self, topic: str) -> str:
        """分析IDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
        return f"analysis_{timestamp}_{topic_hash}"
    
    def _serialize_research_result(self, research_result) -> Dict[str, Any]:
        """ResearchResultを辞書に変換"""
        return {
            "topic": research_result.topic,
            "final_answer": research_result.final_answer,
            "confidence_score": research_result.confidence_score,
            "time_taken": research_result.time_taken,
            "sources_analyzed": research_result.sources_analyzed,
            "quality_metrics": research_result.quality_metrics,
            "thinking_steps_count": len(research_result.thinking_steps)
        } 