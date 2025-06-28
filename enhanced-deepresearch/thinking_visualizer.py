#!/usr/bin/env python3
"""
Enhanced DeepResearch - 思考プロセス可視化エンジン

高度な思考プロセス可視化システム：
- インタラクティブな思考フローダイアグラム
- 詳細な信頼度タイムライン
- 検証プロセスの可視化
- D3.js によるネットワーク図
- フィルタリング・検索機能
- エクスポート機能（PDF、PNG、JSON）
- ズーム・パン機能
- 推論ステップの詳細展開
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid
import base64
from pathlib import Path

@dataclass
class VisualizationNode:
    """拡張可視化ノード"""
    id: str
    label: str
    phase: str
    confidence: float
    timestamp: datetime
    color: str
    # 拡張属性
    detailed_content: str = ""
    reasoning_text: str = ""
    sources: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # 他ノードとの関連
    verification_status: str = "pending"  # verified, rejected, pending
    duration: float = 0.0  # 処理時間（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class ThinkingConnection:
    """思考プロセス間の関連"""
    from_node_id: str
    to_node_id: str
    relationship_type: str  # "leads_to", "supports", "contradicts", "references"
    confidence: float
    description: str = ""

@dataclass
class ConfidencePoint:
    """信頼度ポイント（タイムライン用）"""
    timestamp: datetime
    confidence: float
    phase: str
    reason: str = ""
    change_amount: float = 0.0

class ThinkingVisualizer:
    """高度思考プロセス可視化エンジン"""
    
    def __init__(self):
        self.color_scheme = {
            "decomposition": "#3498db",    # 青 - 問題分解
            "reasoning": "#e74c3c",        # 赤 - 推論
            "verification": "#f39c12",     # オレンジ - 検証
            "synthesis": "#27ae60",        # 緑 - 統合
            "collection": "#9b59b6",       # 紫 - データ収集
            "analysis": "#34495e",         # 濃いグレー - 分析
            "validation": "#e67e22",       # オレンジ系 - 妥当性確認
            "conclusion": "#16a085"        # ティール - 結論
        }
        
        self.confidence_colors = {
            "high": "#27ae60",      # 緑 (0.8-1.0)
            "medium": "#f39c12",    # オレンジ (0.6-0.8)
            "low": "#e74c3c",       # 赤 (0.0-0.6)
            "unknown": "#95a5a6"    # グレー
        }
        
        self.verification_colors = {
            "verified": "#27ae60",
            "rejected": "#e74c3c", 
            "pending": "#f39c12",
            "partial": "#3498db"
        }
        
        # 可視化設定
        self.settings = {
            "enable_animations": True,
            "show_timestamps": True,
            "show_confidence_timeline": True,
            "enable_filtering": True,
            "enable_search": True,
            "layout_type": "force-directed",  # force-directed, hierarchical, circular
            "zoom_enabled": True,
            "pan_enabled": True
        }
    
    def generate_thinking_flow(self, research_result) -> Dict[str, Any]:
        """高度な思考フローの可視化データを生成"""
        nodes = []
        connections = []
        confidence_timeline = []
        
        # ノード生成
        for i, step in enumerate(research_result.thinking_steps):
            # 前のステップからの関連を生成
            if i > 0:
                prev_step = research_result.thinking_steps[i-1]
                connection = ThinkingConnection(
                    from_node_id=f"step_{prev_step.step_id}",
                    to_node_id=f"step_{step.step_id}",
                    relationship_type="leads_to",
                    confidence=min(prev_step.confidence, step.confidence),
                    description=f"{prev_step.phase} から {step.phase} への推移"
                )
                connections.append(connection)
            
            # 拡張ノード作成
            node = VisualizationNode(
                id=f"step_{step.step_id}",
                label=self._generate_enhanced_label(step),
                phase=step.phase,
                confidence=step.confidence,
                timestamp=step.timestamp,
                color=self.color_scheme.get(step.phase, "#95a5a6"),
                detailed_content=getattr(step, 'content', ''),
                reasoning_text=getattr(step, 'reasoning_text', ''),
                sources=getattr(step, 'sources', []),
                verification_status=getattr(step, 'verification_status', 'pending'),
                duration=getattr(step, 'duration', 0.0),
                metadata={
                    "step_number": i + 1,
                    "total_steps": len(research_result.thinking_steps),
                    "phase_icon": self._get_phase_icon(step.phase),
                    "confidence_level": self._get_confidence_level(step.confidence)
                }
            )
            nodes.append(node)
            
            # 信頼度タイムラインポイント
            confidence_point = ConfidencePoint(
                timestamp=step.timestamp,
                confidence=step.confidence,
                phase=step.phase,
                reason=getattr(step, 'confidence_reason', ''),
                change_amount=step.confidence - (research_result.thinking_steps[i-1].confidence if i > 0 else 0.5)
            )
            confidence_timeline.append(confidence_point)
        
        return {
            "nodes": [self._enhanced_node_to_dict(node) for node in nodes],
            "connections": [self._connection_to_dict(conn) for conn in connections],
            "confidence_timeline": [self._confidence_point_to_dict(cp) for cp in confidence_timeline],
            "metadata": self._generate_enhanced_metadata(research_result),
            "visualization_config": self.settings,
            "legend": self._generate_legend(),
            "statistics": self._generate_statistics(nodes, connections)
        }
    
    def _generate_enhanced_label(self, step) -> str:
        """拡張ノードラベルを生成"""
        phase_labels = {
            "decomposition": "🔍 問題分解",
            "reasoning": "🤔 推論", 
            "verification": "✅ 検証",
            "synthesis": "🔗 統合",
            "collection": "📊 収集",
            "analysis": "📈 分析", 
            "validation": "🔬 妥当性",
            "conclusion": "🎯 結論"
        }
        
        confidence_indicator = self._get_confidence_indicator(step.confidence)
        duration_text = f" ({getattr(step, 'duration', 0):.1f}s)" if hasattr(step, 'duration') else ""
        
        return f"{phase_labels.get(step.phase, step.phase)} {confidence_indicator}{duration_text}"
    
    def _get_confidence_indicator(self, confidence: float) -> str:
        """信頼度インジケーターを取得"""
        if confidence >= 0.9: return "🟢"
        elif confidence >= 0.8: return "🔵" 
        elif confidence >= 0.7: return "🟡"
        elif confidence >= 0.6: return "🟠"
        elif confidence >= 0.5: return "🔴"
        else: return "⚫"
    
    def _get_confidence_level(self, confidence: float) -> str:
        """信頼度レベルを取得"""
        if confidence >= 0.8: return "high"
        elif confidence >= 0.6: return "medium" 
        else: return "low"
    
    def _get_phase_icon(self, phase: str) -> str:
        """フェーズアイコンを取得"""
        icons = {
            "decomposition": "🔍", "reasoning": "🤔", "verification": "✅", 
            "synthesis": "🔗", "collection": "📊", "analysis": "📈",
            "validation": "🔬", "conclusion": "🎯"
        }
        return icons.get(phase, "❓")
    
    def _enhanced_node_to_dict(self, node: VisualizationNode) -> Dict[str, Any]:
        """拡張ノードを辞書に変換"""
        return {
            "id": node.id,
            "label": node.label,
            "phase": node.phase,
            "confidence": node.confidence,
            "timestamp": node.timestamp.isoformat(),
            "color": node.color,
            "detailed_content": node.detailed_content,
            "reasoning_text": node.reasoning_text,
            "sources": node.sources,
            "connections": node.connections,
            "verification_status": node.verification_status,
            "verification_color": self.verification_colors.get(node.verification_status, "#95a5a6"),
            "duration": node.duration,
            "metadata": node.metadata,
            "confidence_color": self._get_confidence_color(node.confidence),
            "size": self._calculate_node_size(node.confidence, node.duration)
        }
    
    def _connection_to_dict(self, connection: ThinkingConnection) -> Dict[str, Any]:
        """コネクションを辞書に変換"""
        return {
            "from": connection.from_node_id,
            "to": connection.to_node_id,
            "type": connection.relationship_type,
            "confidence": connection.confidence,
            "description": connection.description,
            "color": self._get_relationship_color(connection.relationship_type),
            "width": max(1, connection.confidence * 5)  # 線の太さ
        }
    
    def _confidence_point_to_dict(self, point: ConfidencePoint) -> Dict[str, Any]:
        """信頼度ポイントを辞書に変換"""
        return {
            "timestamp": point.timestamp.isoformat(),
            "confidence": point.confidence,
            "phase": point.phase,
            "reason": point.reason,
            "change_amount": point.change_amount,
            "color": self.color_scheme.get(point.phase, "#95a5a6"),
            "marker_size": abs(point.change_amount) * 10 + 5
        }
    
    def _get_confidence_color(self, confidence: float) -> str:
        """信頼度に応じた色を取得"""
        if confidence >= 0.8: return self.confidence_colors["high"]
        elif confidence >= 0.6: return self.confidence_colors["medium"]
        else: return self.confidence_colors["low"]
    
    def _get_relationship_color(self, relationship_type: str) -> str:
        """関係性に応じた色を取得"""
        colors = {
            "leads_to": "#3498db",
            "supports": "#27ae60", 
            "contradicts": "#e74c3c",
            "references": "#9b59b6"
        }
        return colors.get(relationship_type, "#95a5a6")
    
    def _calculate_node_size(self, confidence: float, duration: float) -> float:
        """ノードサイズを計算（信頼度と処理時間を考慮）"""
        base_size = 20
        confidence_factor = confidence * 10
        duration_factor = min(duration * 2, 10)  # 最大10まで
        return base_size + confidence_factor + duration_factor
    
    def _generate_enhanced_metadata(self, research_result) -> Dict[str, Any]:
        """拡張メタデータを生成"""
        steps = research_result.thinking_steps
        
        # フェーズ統計
        phase_stats = {}
        total_duration = 0
        confidence_trajectory = []
        
        for step in steps:
            if step.phase not in phase_stats:
                phase_stats[step.phase] = {
                    "count": 0, 
                    "avg_confidence": 0,
                    "total_duration": 0,
                    "avg_duration": 0
                }
            phase_stats[step.phase]["count"] += 1
            step_duration = getattr(step, 'duration', 0)
            phase_stats[step.phase]["total_duration"] += step_duration
            total_duration += step_duration
            confidence_trajectory.append(step.confidence)
        
        # 平均値計算
        for phase in phase_stats:
            phase_steps = [s for s in steps if s.phase == phase]
            phase_confidences = [s.confidence for s in phase_steps]
            phase_stats[phase]["avg_confidence"] = sum(phase_confidences) / len(phase_confidences)
            if phase_stats[phase]["count"] > 0:
                phase_stats[phase]["avg_duration"] = phase_stats[phase]["total_duration"] / phase_stats[phase]["count"]
        
        # 信頼度トレンド分析
        confidence_trend = "stable"
        if len(confidence_trajectory) > 1:
            start_conf = sum(confidence_trajectory[:3]) / min(3, len(confidence_trajectory))
            end_conf = sum(confidence_trajectory[-3:]) / min(3, len(confidence_trajectory))
            if end_conf > start_conf + 0.1:
                confidence_trend = "improving"
            elif end_conf < start_conf - 0.1:
                confidence_trend = "declining"
        
        return {
            "topic": research_result.topic,
            "total_steps": len(steps),
            "analysis_time": research_result.time_taken,
            "total_processing_time": total_duration,
            "overall_confidence": research_result.confidence_score,
            "confidence_trend": confidence_trend,
            "confidence_range": {
                "min": min(confidence_trajectory) if confidence_trajectory else 0,
                "max": max(confidence_trajectory) if confidence_trajectory else 0,
                "variance": self._calculate_variance(confidence_trajectory)
            },
            "phase_statistics": phase_stats,
            "complexity_score": self._calculate_complexity_score(steps),
            "verification_rate": self._calculate_verification_rate(steps),
            "created_at": datetime.now().isoformat(),
            "analysis_quality": self._assess_analysis_quality(research_result)
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """分散を計算"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _calculate_complexity_score(self, steps: List) -> float:
        """分析の複雑度スコアを計算"""
        phase_diversity = len(set(step.phase for step in steps))
        step_count = len(steps)
        avg_confidence = sum(step.confidence for step in steps) / len(steps) if steps else 0
        
        # 複雑度 = フェーズの多様性 + ステップ数 - 平均信頼度
        return min(10.0, phase_diversity * 2 + step_count * 0.1 + (1 - avg_confidence) * 3)
    
    def _calculate_verification_rate(self, steps: List) -> float:
        """検証率を計算"""
        verified_steps = sum(1 for step in steps if getattr(step, 'verification_status', 'pending') == 'verified')
        return verified_steps / len(steps) if steps else 0.0
    
    def _assess_analysis_quality(self, research_result) -> str:
        """分析品質を評価"""
        confidence = research_result.confidence_score
        step_count = len(research_result.thinking_steps)
        
        if confidence >= 0.8 and step_count >= 4:
            return "excellent"
        elif confidence >= 0.7 and step_count >= 3:
            return "good"
        elif confidence >= 0.6:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _generate_legend(self) -> Dict[str, Any]:
        """可視化の凡例を生成"""
        return {
            "phases": {
                phase: {"color": color, "icon": self._get_phase_icon(phase)}
                for phase, color in self.color_scheme.items()
            },
            "confidence_levels": {
                "high": {"color": self.confidence_colors["high"], "range": "0.8-1.0", "icon": "🟢"},
                "medium": {"color": self.confidence_colors["medium"], "range": "0.6-0.8", "icon": "🟡"},
                "low": {"color": self.confidence_colors["low"], "range": "0.0-0.6", "icon": "🔴"}
            },
            "verification_status": {
                status: {"color": color, "description": self._get_verification_description(status)}
                for status, color in self.verification_colors.items()
            },
            "relationship_types": {
                "leads_to": {"color": "#3498db", "description": "論理的な流れ"},
                "supports": {"color": "#27ae60", "description": "証拠・根拠"},
                "contradicts": {"color": "#e74c3c", "description": "矛盾・反証"},
                "references": {"color": "#9b59b6", "description": "参照・引用"}
            }
        }
    
    def _generate_statistics(self, nodes: List[VisualizationNode], connections: List[ThinkingConnection]) -> Dict[str, Any]:
        """統計情報を生成"""
        # ノード統計
        node_stats = {
            "total_nodes": len(nodes),
            "avg_confidence": sum(node.confidence for node in nodes) / len(nodes) if nodes else 0,
            "total_duration": sum(node.duration for node in nodes),
            "phases": {}
        }
        
        # フェーズ別統計
        for node in nodes:
            if node.phase not in node_stats["phases"]:
                node_stats["phases"][node.phase] = {
                    "count": 0,
                    "avg_confidence": 0,
                    "total_duration": 0
                }
            node_stats["phases"][node.phase]["count"] += 1
            node_stats["phases"][node.phase]["total_duration"] += node.duration
        
        # フェーズ別平均信頼度計算
        for phase in node_stats["phases"]:
            phase_nodes = [n for n in nodes if n.phase == phase]
            node_stats["phases"][phase]["avg_confidence"] = sum(n.confidence for n in phase_nodes) / len(phase_nodes)
        
        # コネクション統計
        connection_stats = {
            "total_connections": len(connections),
            "avg_confidence": sum(conn.confidence for conn in connections) / len(connections) if connections else 0,
            "relationship_types": {}
        }
        
        for conn in connections:
            if conn.relationship_type not in connection_stats["relationship_types"]:
                connection_stats["relationship_types"][conn.relationship_type] = 0
            connection_stats["relationship_types"][conn.relationship_type] += 1
        
        return {
            "nodes": node_stats,
            "connections": connection_stats,
            "network_density": len(connections) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0,
            "complexity_indicators": {
                "phase_diversity": len(set(node.phase for node in nodes)),
                "confidence_variance": self._calculate_variance([node.confidence for node in nodes]),
                "temporal_span": self._calculate_temporal_span(nodes)
            }
        }
    
    def _get_verification_description(self, status: str) -> str:
        """検証ステータスの説明を取得"""
        descriptions = {
            "verified": "検証済み・信頼性確認",
            "rejected": "反証・信頼性に問題",
            "pending": "検証待ち",
            "partial": "部分的に検証済み"
        }
        return descriptions.get(status, "不明なステータス")
    
    def _calculate_temporal_span(self, nodes: List[VisualizationNode]) -> float:
        """分析の時間的スパンを計算（秒）"""
        if len(nodes) < 2:
            return 0.0
        timestamps = [node.timestamp for node in nodes]
        return (max(timestamps) - min(timestamps)).total_seconds()
    
    def generate_html_report(self, research_result) -> str:
        """インタラクティブHTML可視化レポートを生成"""
        flow_data = self.generate_thinking_flow(research_result)
        
        # データをJSONとして埋め込み
        flow_data_json = json.dumps(flow_data, ensure_ascii=False, indent=2)
        
        html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced DeepResearch - 思考プロセス可視化</title>
    
    <!-- 外部ライブラリ -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.js"></script>
    
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #2c3e50;
            --border-radius: 12px;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            border-radius: var(--border-radius);
            margin-bottom: 30px;
            box-shadow: var(--shadow);
        }}
        
        .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .header .meta {{ display: flex; gap: 30px; flex-wrap: wrap; margin-top: 20px; }}
        .header .meta-item {{ background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 8px; }}
        
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        
        .card {{
            background: var(--card-background);
            border-radius: var(--border-radius);
            padding: 25px;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15); }}
        
        .card h3 {{ color: var(--primary-color); margin-bottom: 15px; font-size: 1.3rem; }}
        
        .tabs {{
            background: var(--card-background);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            margin-bottom: 30px;
        }}
        
        .tab-header {{
            display: flex;
            border-bottom: 1px solid #dee2e6;
            background: #f8f9fa;
            border-radius: var(--border-radius) var(--border-radius) 0 0;
        }}
        
        .tab-button {{
            padding: 15px 25px;
            border: none;
            background: none;
            cursor: pointer;
            font-weight: 600;
            color: var(--text-color);
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }}
        
        .tab-button.active {{
            background: var(--card-background);
            border-bottom-color: var(--secondary-color);
            color: var(--secondary-color);
        }}
        
        .tab-content {{ padding: 30px; }}
        .tab-content.hidden {{ display: none; }}
        
        /* 可視化関連 */
        .visualization-container {{ position: relative; }}
        #network-viz {{ border: 1px solid #dee2e6; border-radius: 8px; background: white; }}
        #confidence-chart {{ max-height: 400px; }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        
        .control-section {{
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 5px 10px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        
        .controls button, .controls select {{
            padding: 8px 16px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }}
        
        .controls button:hover {{ background: var(--secondary-color); color: white; }}
        
        .search-input {{
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background: white;
            font-size: 14px;
            min-width: 200px;
            transition: border-color 0.3s ease;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }}
        
        .reset-btn {{
            background: var(--warning-color) !important;
            color: white;
        }}
        
        .reset-btn:hover {{
            background: #e67e22 !important;
        }}
        
        .filters-panel {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .filter-row {{
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }}
        
        .filter-column {{
            flex: 1;
            min-width: 200px;
        }}
        
        .filter-group {{
            background: white;
            border-radius: 6px;
            padding: 15px;
            border: 1px solid #e9ecef;
        }}
        
        .filter-group h4 {{
            margin: 0 0 15px 0;
            color: var(--primary-color);
            font-size: 16px;
            font-weight: 600;
        }}
        
        .filter-checkbox {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }}
        
        .filter-checkbox:hover {{
            background-color: #f8f9fa;
        }}
        
        .filter-checkbox input[type="checkbox"] {{
            margin: 0;
            width: 16px;
            height: 16px;
        }}
        
        .checkmark {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 5px;
            border: 2px solid white;
            display: inline-block;
        }}
        
        .confidence-slider {{
            margin-top: 10px;
            height: 40px;
        }}
        
        .filter-checkbox input:checked + .checkmark {{
            border-color: #333;
        }}
        
        .noUi-target {{
            background: #e9ecef;
            border-radius: 6px;
            border: none;
            box-shadow: none;
        }}
        
        .noUi-handle {{
            background: var(--secondary-color);
            border: none;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }}
        
        .noUi-connect {{
            background: var(--secondary-color);
        }}
        
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .stat-value {{ font-size: 2rem; font-weight: bold; color: var(--secondary-color); }}
        .stat-label {{ font-size: 0.9rem; color: #6c757d; margin-top: 5px; }}
        
        .export-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .export-buttons button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            background: var(--secondary-color);
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }}
        
        .export-buttons button:hover {{ background: var(--primary-color); }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .dashboard {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2rem; }}
            .header .meta {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- ヘッダー -->
        <div class="header">
            <h1>🧠 Enhanced DeepResearch 分析結果</h1>
            <div class="meta">
                <div class="meta-item">
                    <strong>📋 トピック:</strong> {research_result.topic}
                </div>
                <div class="meta-item">
                    <strong>⏱️ 分析時間:</strong> {research_result.time_taken:.2f}秒
                </div>
                <div class="meta-item">
                    <strong>📊 信頼度:</strong> {research_result.confidence_score:.2f}
                </div>
                <div class="meta-item">
                    <strong>🎯 品質:</strong> {flow_data['metadata']['analysis_quality']}
                </div>
            </div>
        </div>
        
        <!-- ダッシュボード -->
        <div class="dashboard">
            <div class="card">
                <h3>📈 分析統計</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">{flow_data['metadata']['total_steps']}</div>
                        <div class="stat-label">総ステップ数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{flow_data['metadata']['complexity_score']:.1f}</div>
                        <div class="stat-label">複雑度スコア</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{flow_data['metadata']['verification_rate']:.1%}</div>
                        <div class="stat-label">検証率</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 信頼度トレンド</h3>
                <p><strong>傾向:</strong> {flow_data['metadata']['confidence_trend']}</p>
                <p><strong>範囲:</strong> {flow_data['metadata']['confidence_range']['min']:.2f} - {flow_data['metadata']['confidence_range']['max']:.2f}</p>
                <p><strong>分散:</strong> {flow_data['metadata']['confidence_range']['variance']:.3f}</p>
            </div>
            
            <div class="card">
                <h3>⚡ パフォーマンス</h3>
                <p><strong>総処理時間:</strong> {flow_data['metadata']['total_processing_time']:.2f}秒</p>
                <p><strong>フェーズ多様性:</strong> {flow_data['statistics']['complexity_indicators']['phase_diversity']}</p>
                <p><strong>ネットワーク密度:</strong> {flow_data['statistics']['network_density']:.3f}</p>
            </div>
        </div>
        
        <!-- タブ -->
        <div class="tabs">
            <div class="tab-header">
                <button class="tab-button active" onclick="showTab('network')">🔗 思考ネットワーク</button>
                <button class="tab-button" onclick="showTab('timeline')">📈 信頼度タイムライン</button>
                <button class="tab-button" onclick="showTab('details')">📋 詳細分析</button>
                <button class="tab-button" onclick="showTab('export')">💾 エクスポート</button>
            </div>
            
            <!-- ネットワーク可視化 -->
            <div id="network-tab" class="tab-content">
                <div class="controls">
                    <div class="control-section">
                        <input type="text" id="search-input" placeholder="🔍 思考プロセスを検索..." class="search-input">
                        <button onclick="resetFilters()" class="reset-btn">フィルタリセット</button>
                    </div>
                    <div class="control-section">
                        <select id="layout-select" onchange="changeLayout()">
                            <option value="force-directed">フォースレイアウト</option>
                            <option value="hierarchical">階層レイアウト</option>
                            <option value="circular">円形レイアウト</option>
                            <option value="timeline">タイムライン</option>
                            <option value="confidence-based">信頼度ベース</option>
                        </select>
                        <button onclick="resetZoom()">🔍 ズームリセット</button>
                    </div>
                    <div class="control-section">
                        <button onclick="exportJSON()">JSON</button>
                        <button onclick="exportPDF()">PDF</button>
                        <button onclick="exportNetworkSVG()">SVG</button>
                    </div>
                </div>
                
                <div class="filters-panel">
                    <div class="filter-row">
                        <div id="phase-filters" class="filter-column"></div>
                        <div id="verification-filters" class="filter-column"></div>
                        <div class="filter-column">
                            <div class="filter-group">
                                <h4>信頼度範囲</h4>
                                <div id="confidence-slider" class="confidence-slider"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="visualization-container">
                    <svg id="network-viz" width="100%" height="600"></svg>
                </div>
                <div class="legend" id="phase-legend"></div>
            </div>
            
            <!-- タイムライン -->
            <div id="timeline-tab" class="tab-content hidden">
                <canvas id="confidence-chart"></canvas>
            </div>
            
            <!-- 詳細分析 -->
            <div id="details-tab" class="tab-content hidden">
                <div id="advanced-stats" class="card" style="margin-bottom: 20px;">
                    <h3>📊 高度統計分析</h3>
                </div>
                <div id="detailed-analysis"></div>
            </div>
            
            <!-- エクスポート -->
            <div id="export-tab" class="tab-content hidden">
                <h3>📥 データエクスポート</h3>
                <div class="export-buttons">
                    <button onclick="exportJSON()">JSON形式</button>
                    <button onclick="exportCSV()">CSV形式</button>
                    <button onclick="exportPDF()">PDFレポート</button>
                    <button onclick="exportPNG()">PNG画像</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // データを埋め込み
        const flowData = {flow_data_json};
        
        // 現在の可視化データ
        let currentData = flowData;
        let networkSimulation = null;
        
        // 初期化
        document.addEventListener('DOMContentLoaded', function() {{
            initializeNetworkVisualization();
            initializeConfidenceChart();
            generateDetailedAnalysis();
            generatePhaseLegend();
            initializeAdvancedControls();
        }});
        
        // タブ切り替え
        function showTab(tabName) {{
            // すべてのタブコンテンツを非表示
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.add('hidden');
            }});
            
            // すべてのタブボタンを非アクティブ
            document.querySelectorAll('.tab-button').forEach(button => {{
                button.classList.remove('active');
            }});
            
            // 選択されたタブを表示
            document.getElementById(tabName + '-tab').classList.remove('hidden');
            event.target.classList.add('active');
        }}
        
        // ネットワーク可視化初期化
        function initializeNetworkVisualization() {{
            const svg = d3.select("#network-viz");
            const width = svg.node().getBoundingClientRect().width;
            const height = 600;
            
            svg.selectAll("*").remove(); // クリア
            
            const g = svg.append("g");
            
            // ズーム機能
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});
            
            svg.call(zoom);
            
            // ノードとリンクのデータ準備
            const nodes = currentData.nodes.map(d => ({{...d}}));
            const links = currentData.connections.map(d => ({{
                source: d.from,
                target: d.to,
                ...d
            }}));
            
            // シミュレーション
            networkSimulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(d => d.size + 5));
            
            // リンク描画
            const link = g.append("g")
                .selectAll("line")
                .data(links)
                .enter().append("line")
                .attr("stroke", d => d.color)
                .attr("stroke-width", d => d.width);
            
            // ノード描画
            const node = g.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter().append("circle")
                .attr("r", d => d.size)
                .attr("fill", d => d.color)
                .attr("stroke", "#fff")
                .attr("stroke-width", 2)
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // ノードラベル
            const labels = g.append("g")
                .selectAll("text")
                .data(nodes)
                .enter().append("text")
                .text(d => d.label)
                .attr("font-size", "12px")
                .attr("text-anchor", "middle")
                .attr("dy", ".35em");
            
            // ツールチップ
            node.append("title")
                .text(d => `${{d.label}}\\n信頼度: ${{d.confidence}}\\n検証: ${{d.verification_status}}`);
            
            // シミュレーション更新
            networkSimulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
                labels
                    .attr("x", d => d.x)
                    .attr("y", d => d.y + d.size + 15);
            }});
            
            function dragstarted(event, d) {{
                if (!event.active) networkSimulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) networkSimulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        }}
        
        // 信頼度チャート初期化
        function initializeConfidenceChart() {{
            const ctx = document.getElementById('confidence-chart').getContext('2d');
            
            const timelineData = currentData.confidence_timeline;
            const labels = timelineData.map(d => new Date(d.timestamp).toLocaleTimeString());
            const data = timelineData.map(d => d.confidence);
            const colors = timelineData.map(d => d.color);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '信頼度',
                        data: data,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: colors,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            min: 0,
                            max: 1,
                            title: {{
                                display: true,
                                text: '信頼度'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: '時間'
                            }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                afterLabel: function(context) {{
                                    const point = timelineData[context.dataIndex];
                                    return [`フェーズ: ${{point.phase}}`, `理由: ${{point.reason}}`];
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 詳細分析生成
        function generateDetailedAnalysis() {{
            const container = document.getElementById('detailed-analysis');
            let html = '';
            
            currentData.nodes.forEach((node, index) => {{
                html += `
                    <div class="card" style="margin-bottom: 20px;">
                        <h4>ステップ ${{index + 1}}: ${{node.label}}</h4>
                        <p><strong>フェーズ:</strong> ${{node.phase}}</p>
                        <p><strong>信頼度:</strong> ${{node.confidence.toFixed(3)}}</p>
                        <p><strong>処理時間:</strong> ${{node.duration.toFixed(2)}}秒</p>
                        <p><strong>検証状況:</strong> ${{node.verification_status}}</p>
                        ${{node.detailed_content ? `<p><strong>詳細:</strong> ${{node.detailed_content}}</p>` : ''}}
                        ${{node.reasoning_text ? `<p><strong>推論:</strong> ${{node.reasoning_text}}</p>` : ''}}
                        ${{node.sources.length > 0 ? `<p><strong>ソース:</strong> ${{node.sources.join(', ')}}</p>` : ''}}
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        // フェーズ凡例生成
        function generatePhaseLegend() {{
            const container = document.getElementById('phase-legend');
            const legend = currentData.legend;
            let html = '';
            
            Object.entries(legend.phases).forEach(([phase, info]) => {{
                html += `
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: ${{info.color}}"></div>
                        <span>${{info.icon}} ${{phase}}</span>
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        // エクスポート機能
        function exportJSON() {{
            const dataStr = JSON.stringify(currentData, null, 2);
            const blob = new Blob([dataStr], {{type: "application/json"}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'thinking_process_analysis.json';
            a.click();
        }}
        
        function exportPDF() {{
            const {{ jsPDF }} = window.jspdf;
            const doc = new jsPDF();
            
            doc.setFontSize(20);
            doc.text('Enhanced DeepResearch 分析結果', 20, 30);
            
            doc.setFontSize(12);
            doc.text(`トピック: {research_result.topic}`, 20, 50);
            doc.text(`分析時間: {research_result.time_taken:.2f}秒`, 20, 60);
            doc.text(`信頼度: {research_result.confidence_score:.2f}`, 20, 70);
            
            doc.save('thinking_process_report.pdf');
        }}
        
        // 高度な検索・フィルタリング機能
        let filteredData = currentData;
        let currentFilters = {{
            phases: new Set(),
            confidenceRange: [0, 1],
            verificationStatus: new Set(),
            searchTerm: ''
        }};
        
        function initializeAdvancedControls() {{
            // 検索機能
            const searchInput = document.getElementById('search-input');
            if (searchInput) {{
                searchInput.addEventListener('input', debounce(performSearch, 300));
            }}
            
            // フェーズフィルタ
            initializePhaseFilters();
            
            // 信頼度スライダー
            initializeConfidenceSlider();
            
            // 検証ステータスフィルタ
            initializeVerificationFilters();
        }}
        
        function performSearch(event) {{
            const searchTerm = event.target.value.toLowerCase();
            currentFilters.searchTerm = searchTerm;
            applyFilters();
        }}
        
        function initializePhaseFilters() {{
            const phaseContainer = document.getElementById('phase-filters');
            if (!phaseContainer) return;
            
            const phases = [...new Set(currentData.nodes.map(n => n.phase))];
            let html = '<div class="filter-group"><h4>フェーズフィルタ</h4>';
            
            phases.forEach(phase => {{
                const color = currentData.legend.phases[phase]?.color || '#999';
                html += `
                    <label class="filter-checkbox">
                        <input type="checkbox" value="${{phase}}" checked
                               onchange="togglePhaseFilter('${{phase}}', this.checked)">
                        <span class="checkmark" style="background-color: ${{color}}"></span>
                        ${{phase}}
                    </label>
                `;
            }});
            
            html += '</div>';
            phaseContainer.innerHTML = html;
        }}
        
        function togglePhaseFilter(phase, enabled) {{
            if (enabled) {{
                currentFilters.phases.delete(phase);
            }} else {{
                currentFilters.phases.add(phase);
            }}
            applyFilters();
        }}
        
        function initializeConfidenceSlider() {{
            const slider = document.getElementById('confidence-slider');
            if (!slider) return;
            
            noUiSlider.create(slider, {{
                start: [0, 1],
                connect: true,
                range: {{
                    'min': 0,
                    'max': 1
                }},
                step: 0.01,
                format: {{
                    to: value => value.toFixed(2),
                    from: value => parseFloat(value)
                }}
            }});
            
            slider.noUiSlider.on('update', (values) => {{
                currentFilters.confidenceRange = [parseFloat(values[0]), parseFloat(values[1])];
                applyFilters();
            }});
        }}
        
        function initializeVerificationFilters() {{
            const container = document.getElementById('verification-filters');
            if (!container) return;
            
            const statuses = [...new Set(currentData.nodes.map(n => n.verification_status))];
            let html = '<div class="filter-group"><h4>検証ステータス</h4>';
            
            statuses.forEach(status => {{
                const color = getVerificationColor(status);
                html += `
                    <label class="filter-checkbox">
                        <input type="checkbox" value="${{status}}" checked
                               onchange="toggleVerificationFilter('${{status}}', this.checked)">
                        <span class="checkmark" style="background-color: ${{color}}"></span>
                        ${{status}}
                    </label>
                `;
            }});
            
            html += '</div>';
            container.innerHTML = html;
        }}
        
        function toggleVerificationFilter(status, enabled) {{
            if (enabled) {{
                currentFilters.verificationStatus.delete(status);
            }} else {{
                currentFilters.verificationStatus.add(status);
            }}
            applyFilters();
        }}
        
        function applyFilters() {{
            filteredData = {{
                ...currentData,
                nodes: currentData.nodes.filter(node => {{
                    // フェーズフィルタ
                    if (currentFilters.phases.has(node.phase)) return false;
                    
                    // 信頼度フィルタ
                    if (node.confidence < currentFilters.confidenceRange[0] || 
                        node.confidence > currentFilters.confidenceRange[1]) return false;
                    
                    // 検証ステータスフィルタ
                    if (currentFilters.verificationStatus.has(node.verification_status)) return false;
                    
                    // 検索フィルタ
                    if (currentFilters.searchTerm) {{
                        const searchableText = [
                            node.label,
                            node.detailed_content,
                            node.reasoning_text,
                            ...node.sources
                        ].join(' ').toLowerCase();
                        if (!searchableText.includes(currentFilters.searchTerm)) return false;
                    }}
                    
                    return true;
                }})
            }};
            
            // 接続も更新（フィルタされたノードのみ）
            const filteredNodeIds = new Set(filteredData.nodes.map(n => n.id));
            filteredData.connections = currentData.connections.filter(conn => 
                filteredNodeIds.has(conn.from) && filteredNodeIds.has(conn.to)
            );
            
            updateVisualization();
            updateStatistics();
        }}
        
        function updateVisualization() {{
            // ネットワーク図を再描画
            d3.select("#network-viz").selectAll("*").remove();
            initializeNetworkVisualization();
            
            // タイムライン更新
            updateConfidenceChart();
        }}
        
        function updateConfidenceChart() {{
            const canvas = document.getElementById('confidence-chart');
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {{
                existingChart.destroy();
            }}
            initializeConfidenceChart();
        }}
        
        function updateStatistics() {{
            const stats = calculateAdvancedStatistics(filteredData);
            displayAdvancedStatistics(stats);
        }}
        
        function calculateAdvancedStatistics(data) {{
            const nodes = data.nodes;
            const connections = data.connections;
            
            return {{
                totalNodes: nodes.length,
                averageConfidence: nodes.reduce((sum, n) => sum + n.confidence, 0) / nodes.length,
                confidenceVariance: calculateVariance(nodes.map(n => n.confidence)),
                verificationRate: nodes.filter(n => n.verification_status === 'verified').length / nodes.length,
                averageDuration: nodes.reduce((sum, n) => sum + (n.duration || 0), 0) / nodes.length,
                complexityScore: calculateComplexityScore(nodes, connections),
                phasesDistribution: calculatePhaseDistribution(nodes),
                criticalPath: identifyCriticalPath(nodes, connections)
            }};
        }}
        
        function calculatePhaseDistribution(nodes) {{
            const distribution = {{}};
            nodes.forEach(node => {{
                distribution[node.phase] = (distribution[node.phase] || 0) + 1;
            }});
            return distribution;
        }}
        
        function identifyCriticalPath(nodes, connections) {{
            // 最も信頼度の高いパスを特定
            const graph = buildGraph(nodes, connections);
            return findHighestConfidencePath(graph);
        }}
        
        function buildGraph(nodes, connections) {{
            const graph = {{}};
            nodes.forEach(node => {{
                graph[node.id] = {{ node, connections: [] }};
            }});
            connections.forEach(conn => {{
                if (graph[conn.from]) {{
                    graph[conn.from].connections.push(conn);
                }}
            }});
            return graph;
        }}
        
        function findHighestConfidencePath(graph) {{
            // 簡化されたパス探索アルゴリズム
            let bestPath = [];
            let bestScore = 0;
            
            Object.keys(graph).forEach(startId => {{
                const path = explorePathDFS(graph, startId, [], 0);
                if (path.score > bestScore) {{
                    bestScore = path.score;
                    bestPath = path.nodes;
                }}
            }});
            
            return bestPath;
        }}
        
        function explorePathDFS(graph, nodeId, currentPath, currentScore) {{
            const node = graph[nodeId];
            if (!node || currentPath.includes(nodeId)) {{
                return {{ nodes: currentPath, score: currentScore }};
            }}
            
            const newPath = [...currentPath, nodeId];
            const newScore = currentScore + node.node.confidence;
            
            if (node.connections.length === 0) {{
                return {{ nodes: newPath, score: newScore }};
            }}
            
            let bestSubPath = {{ nodes: newPath, score: newScore }};
            node.connections.forEach(conn => {{
                const subPath = explorePathDFS(graph, conn.to, newPath, newScore);
                if (subPath.score > bestSubPath.score) {{
                    bestSubPath = subPath;
                }}
            }});
            
            return bestSubPath;
        }}
        
        // 高度なレイアウト機能
        function changeLayout() {{
            const layout = document.getElementById('layout-select').value;
            applyLayoutAlgorithm(layout);
        }}
        
                 function applyLayoutAlgorithm(layoutType) {{
             const nodes = filteredData.nodes;
             const connections = filteredData.connections;
             
             // 既存のシミュレーションを停止
             if (networkSimulation) {{
                 networkSimulation.stop();
             }}
             
             // ネットワーク図をクリア
             d3.select("#network-viz").selectAll("*").remove();
             
             switch (layoutType) {{
                 case 'force-directed':
                     initializeForceDirectedLayout();
                     break;
                 case 'hierarchical':
                     initializeHierarchicalLayout();
                     break;
                 case 'circular':
                     initializeCircularLayout();
                     break;
                 case 'timeline':
                     initializeTimelineLayout();
                     break;
                 case 'confidence-based':
                     initializeConfidenceBasedLayout();
                     break;
             }}
         }}
         
         function initializeForceDirectedLayout() {{
             // フォースレイアウトでは固定位置をクリアして自然な配置にする
             filteredData.nodes.forEach(node => {{
                 node.fx = null;
                 node.fy = null;
             }});
             initializeNetworkVisualization();
         }}
         
         function calculateVariance(values) {{
             if (values.length === 0) return 0;
             const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
             const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
             return squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
         }}
         
         function calculateComplexityScore(nodes, connections) {{
             // 複雑度スコアの計算：ノード数、接続数、平均分岐度を考慮
             const nodeCount = nodes.length;
             const connectionCount = connections.length;
             const avgBranching = connectionCount > 0 ? connectionCount / nodeCount : 0;
             
             // 正規化された複雑度スコア (0-1)
             const normalizedNodeCount = Math.min(nodeCount / 50, 1); // 50ノードを最大とする
             const normalizedConnectionCount = Math.min(connectionCount / 100, 1); // 100接続を最大とする
             const normalizedBranching = Math.min(avgBranching / 5, 1); // 平均分岐度5を最大とする
             
             return (normalizedNodeCount + normalizedConnectionCount + normalizedBranching) / 3;
         }}
         
         function displayAdvancedStatistics(stats) {{
             const container = document.getElementById('advanced-stats');
             if (!container) return;
             
             let html = `
                 <div class="stats-grid">
                     <div class="stat-item">
                         <div class="stat-value">${{stats.totalNodes}}</div>
                         <div class="stat-label">総ノード数</div>
                     </div>
                     <div class="stat-item">
                         <div class="stat-value">${{stats.averageConfidence.toFixed(3)}}</div>
                         <div class="stat-label">平均信頼度</div>
                     </div>
                     <div class="stat-item">
                         <div class="stat-value">${{(stats.verificationRate * 100).toFixed(1)}}%</div>
                         <div class="stat-label">検証率</div>
                     </div>
                     <div class="stat-item">
                         <div class="stat-value">${{stats.averageDuration.toFixed(2)}}s</div>
                         <div class="stat-label">平均処理時間</div>
                     </div>
                     <div class="stat-item">
                         <div class="stat-value">${{(stats.complexityScore * 100).toFixed(0)}}</div>
                         <div class="stat-label">複雑度スコア</div>
                     </div>
                 </div>
             `;
             container.innerHTML = html;
         }}
        
        function initializeHierarchicalLayout() {{
            const svg = d3.select("#network-viz");
            const width = svg.node().getBoundingClientRect().width;
            const height = svg.node().getBoundingClientRect().height;
            
            // 階層レベルを計算
            const levels = calculateHierarchicalLevels(filteredData.nodes, filteredData.connections);
            const levelHeight = height / (levels.length + 1);
            
            levels.forEach((levelNodes, levelIndex) => {{
                const y = (levelIndex + 1) * levelHeight;
                const nodeWidth = width / (levelNodes.length + 1);
                
                levelNodes.forEach((node, nodeIndex) => {{
                    node.fx = (nodeIndex + 1) * nodeWidth;
                    node.fy = y;
                }});
            }});
            
            initializeNetworkVisualization();
        }}
        
        function calculateHierarchicalLevels(nodes, connections) {{
            const levels = [];
            const visited = new Set();
            const inDegree = {{}};
            
            // 入次数を計算
            nodes.forEach(node => {{ inDegree[node.id] = 0; }});
            connections.forEach(conn => {{ inDegree[conn.to]++; }});
            
            // レベル0: 入次数0のノード
            let currentLevel = nodes.filter(node => inDegree[node.id] === 0);
            
            while (currentLevel.length > 0) {{
                levels.push([...currentLevel]);
                currentLevel.forEach(node => visited.add(node.id));
                
                const nextLevel = [];
                connections.forEach(conn => {{
                    if (visited.has(conn.from) && !visited.has(conn.to)) {{
                        const targetNode = nodes.find(n => n.id === conn.to);
                        if (targetNode && !nextLevel.includes(targetNode)) {{
                            nextLevel.push(targetNode);
                        }}
                    }}
                }});
                
                currentLevel = nextLevel;
            }}
            
            return levels;
        }}
        
        function initializeCircularLayout() {{
            const nodes = filteredData.nodes;
            const svg = d3.select("#network-viz");
            const width = svg.node().getBoundingClientRect().width;
            const height = svg.node().getBoundingClientRect().height;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) * 0.3;
            
            nodes.forEach((node, index) => {{
                const angle = (2 * Math.PI * index) / nodes.length;
                node.fx = centerX + radius * Math.cos(angle);
                node.fy = centerY + radius * Math.sin(angle);
            }});
            
            initializeNetworkVisualization();
        }}
        
        function initializeTimelineLayout() {{
            const nodes = filteredData.nodes;
            const svg = d3.select("#network-viz");
            const width = svg.node().getBoundingClientRect().width;
            const height = svg.node().getBoundingClientRect().height;
            
            // タイムスタンプでソート
            const sortedNodes = [...nodes].sort((a, b) => 
                new Date(a.timestamp) - new Date(b.timestamp));
            
            sortedNodes.forEach((node, index) => {{
                node.fx = (width / (sortedNodes.length + 1)) * (index + 1);
                node.fy = height / 2;
            }});
            
            initializeNetworkVisualization();
        }}
        
        function initializeConfidenceBasedLayout() {{
            const nodes = filteredData.nodes;
            const svg = d3.select("#network-viz");
            const width = svg.node().getBoundingClientRect().width;
            const height = svg.node().getBoundingClientRect().height;
            
            // 信頼度で垂直位置を決定
            nodes.forEach((node, index) => {{
                node.fx = (width / (nodes.length + 1)) * (index + 1);
                node.fy = height * (1 - node.confidence); // 高信頼度ほど上位
            }});
            
            initializeNetworkVisualization();
        }}
        
        // その他のユーティリティ関数
        function resetZoom() {{
            d3.select("#network-viz").transition().call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
        }}
        
        function resetFilters() {{
            currentFilters = {{
                phases: new Set(),
                confidenceRange: [0, 1],
                verificationStatus: new Set(),
                searchTerm: ''
            }};
            
            // UIをリセット
            document.getElementById('search-input').value = '';
            document.querySelectorAll('.filter-checkbox input').forEach(cb => cb.checked = true);
            
            filteredData = currentData;
            updateVisualization();
            updateStatistics();
        }}
        
        function exportNetworkSVG() {{
            const svgElement = document.getElementById('network-viz');
            const serializer = new XMLSerializer();
            const svgString = serializer.serializeToString(svgElement);
            const blob = new Blob([svgString], {{type: "image/svg+xml"}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'network_visualization.svg';
            a.click();
        }}
        
        function debounce(func, wait) {{
            let timeout;
            return function executedFunction(...args) {{
                const later = () => {{
                    clearTimeout(timeout);
                    func(...args);
                }};
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            }};
        }}
        
        function getVerificationColor(status) {{
            const colors = {{
                'verified': '#27ae60',
                'rejected': '#e74c3c',
                'pending': '#f39c12',
                'partial': '#3498db'
            }};
            return colors[status] || '#95a5a6';
        }}
    </script>
</body>
</html>"""
        
        return html
    
    def export_data(self, research_result, format_type: str = "json") -> str:
        """分析データをエクスポート"""
        flow_data = self.generate_thinking_flow(research_result)
        
        if format_type == "json":
            return json.dumps(flow_data, ensure_ascii=False, indent=2)
        elif format_type == "csv":
            return self._export_to_csv(flow_data)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_to_csv(self, flow_data: Dict[str, Any]) -> str:
        """CSV形式でエクスポート"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー
        writer.writerow(['Step', 'Phase', 'Confidence', 'Duration', 'Verification', 'Timestamp'])
        
        # データ行
        for i, node in enumerate(flow_data['nodes']):
            writer.writerow([
                i + 1,
                node['phase'],
                node['confidence'],
                node['duration'],
                node['verification_status'],
                node['timestamp']
            ])
        
        return output.getvalue() 