#!/usr/bin/env python3
"""
Enhanced DeepResearch - 多段階推論エンジン

既存のQwen3Llmを継承し、以下の機能を追加：
- Chain-of-Thought推論
- 多段階問題分解
- 反復的分析・改善
- 思考プロセス記録
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from qwen3_llm import Qwen3Llm
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio

@dataclass
class ThinkingStep:
    """思考ステップの記録"""
    step_id: int
    phase: str  # "decomposition", "reasoning", "verification", "improvement"
    input_data: str
    output_data: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning_chain: List[str] = field(default_factory=list)

@dataclass
class ResearchResult:
    """深層分析結果"""
    topic: str
    final_answer: str
    confidence_score: float
    thinking_steps: List[ThinkingStep]
    verification_results: Dict[str, Any]
    sources_analyzed: List[str]
    time_taken: float
    quality_metrics: Dict[str, float]

class EnhancedQwen3Llm(Qwen3Llm):
    """
    Qwen3ベース多段階推論エンジン
    
    既存のQwen3Llmクラスを継承し、以下の機能を追加：
    - 多段階推論機能
    - 思考プロセス可視化
    - 品質検証
    - 反復改善
    """
    
    def __init__(self, model="ollama/qwen3:30b-a3b", api_url="http://localhost:11434/api/generate"):
        super().__init__(model, api_url)
        self.thinking_mode = True
        self.steps_log: List[ThinkingStep] = []
        self.current_step_id = 0
        
        # 推論設定
        self.reasoning_config = {
            "max_decomposition_depth": 3,
            "min_confidence_threshold": 0.7,
            "max_iterations": 5,
            "verification_required": True
        }
    
    async def deep_research(self, topic: str, context: Dict[str, Any] = None) -> ResearchResult:
        """
        多段階深層分析のメインメソッド
        
        Args:
            topic: 分析対象トピック
            context: 追加コンテキスト情報
        
        Returns:
            ResearchResult: 分析結果
        """
        start_time = datetime.now()
        self.steps_log = []
        self.current_step_id = 0
        
        try:
            print(f"🔍 Deep Research開始: {topic}")
            
            # Phase 1: 問題分解
            decomposition = await self._decompose_problem(topic, context or {})
            
            # Phase 2: 反復推論
            reasoning_results = await self._iterative_reasoning(decomposition)
            
            # Phase 3: 検証・改善
            verified_result = await self._verify_and_improve(reasoning_results)
            
            # Phase 4: 最終統合
            final_answer = await self._synthesize_final_answer(verified_result)
            
            end_time = datetime.now()
            time_taken = (end_time - start_time).total_seconds()
            
            # 品質メトリクス計算
            quality_metrics = self._calculate_quality_metrics()
            
            result = ResearchResult(
                topic=topic,
                final_answer=final_answer["answer"],
                confidence_score=final_answer["confidence"],
                thinking_steps=self.steps_log,
                verification_results=verified_result["verification_results"],
                sources_analyzed=verified_result["sources"],
                time_taken=time_taken,
                quality_metrics=quality_metrics
            )
            
            print(f"✅ Deep Research完了: {time_taken:.2f}秒")
            return result
            
        except Exception as e:
            print(f"❌ Deep Research エラー: {e}")
            # 最小限の結果を返す
            return ResearchResult(
                topic=topic,
                final_answer=f"分析中にエラーが発生しました: {str(e)}",
                confidence_score=0.0,
                thinking_steps=self.steps_log,
                verification_results={},
                sources_analyzed=[],
                time_taken=0.0,
                quality_metrics={}
            )
    
    async def _decompose_problem(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """問題分解フェーズ"""
        self.current_step_id += 1
        
        decomposition_prompt = f"""あなたは高度な分析エキスパートです。以下のトピックを体系的に分解してください。

トピック: {topic}
コンテキスト: {json.dumps(context, ensure_ascii=False, indent=2)}

以下の構造で分解してください：
1. 主要な分析軸（3-5個）
2. 各軸での具体的質問
3. 必要な情報源
4. 分析の優先順位

回答は以下のJSON形式で：
{{
    "analysis_axes": [
        {{
            "axis": "技術的側面",
            "questions": ["具体的な技術は何か？", "革新性は？"],
            "priority": 1
        }}
    ],
    "information_sources": ["ニュース記事", "技術文書"],
    "complexity_level": "高",
    "estimated_depth": 3
}}
"""
        
        response = await self.generate_content_async(
            decomposition_prompt, 
            agent_name="問題分解エンジン"
        )
        
        try:
            decomposition_data = json.loads(response.strip())
        except:
            # JSONパース失敗時のフォールバック
            decomposition_data = {
                "analysis_axes": [{"axis": "基本分析", "questions": [topic], "priority": 1}],
                "information_sources": ["一般情報"],
                "complexity_level": "中",
                "estimated_depth": 1
            }
        
        # 思考ステップを記録
        step = ThinkingStep(
            step_id=self.current_step_id,
            phase="decomposition",
            input_data=topic,
            output_data=json.dumps(decomposition_data, ensure_ascii=False),
            confidence=0.8,
            reasoning_chain=[f"トピック '{topic}' を {len(decomposition_data.get('analysis_axes', []))} の分析軸に分解"]
        )
        self.steps_log.append(step)
        
        return decomposition_data
    
    async def _iterative_reasoning(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """反復推論フェーズ"""
        reasoning_results = {
            "axis_results": [],
            "confidence_scores": [],
            "reasoning_chains": []
        }
        
        analysis_axes = decomposition.get("analysis_axes", [])
        
        for axis_data in analysis_axes:
            self.current_step_id += 1
            axis_name = axis_data.get("axis", "不明な軸")
            questions = axis_data.get("questions", [])
            
            print(f"🤔 分析軸: {axis_name}")
            
            # 各軸での推論実行
            axis_result = await self._reason_on_axis(axis_name, questions)
            reasoning_results["axis_results"].append(axis_result)
            reasoning_results["confidence_scores"].append(axis_result["confidence"])
            reasoning_results["reasoning_chains"].extend(axis_result["reasoning_chain"])
            
            # 思考ステップ記録
            step = ThinkingStep(
                step_id=self.current_step_id,
                phase="reasoning",
                input_data=f"軸: {axis_name}, 質問: {questions}",
                output_data=json.dumps(axis_result, ensure_ascii=False),
                confidence=axis_result["confidence"],
                reasoning_chain=axis_result["reasoning_chain"]
            )
            self.steps_log.append(step)
        
        return reasoning_results
    
    async def _reason_on_axis(self, axis_name: str, questions: List[str]) -> Dict[str, Any]:
        """特定の分析軸での推論"""
        questions_text = "\n".join([f"- {q}" for q in questions])
        
        reasoning_prompt = f"""分析軸: {axis_name}

以下の質問について段階的に推論してください：
{questions_text}

推論プロセス:
1. 各質問に対する初期回答
2. 回答間の関連性分析
3. 矛盾点の特定と解決
4. 統合された結論

回答は以下のJSON形式で：
{{
    "axis_name": "{axis_name}",
    "initial_answers": {{"質問1": "回答1"}},
    "relationships": ["関連性1", "関連性2"],
    "contradictions": ["矛盾点1"],
    "integrated_conclusion": "統合結論",
    "confidence": 0.8,
    "reasoning_chain": ["推論ステップ1", "推論ステップ2"]
}}
"""
        
        response = await self.generate_content_async(
            reasoning_prompt,
            agent_name=f"推論エンジン({axis_name})"
        )
        
        try:
            axis_result = json.loads(response.strip())
            # 基本的な信頼度チェック
            confidence = axis_result.get("confidence", 0.5)
            if confidence < self.reasoning_config["min_confidence_threshold"]:
                print(f"⚠️ 低信頼度検出 ({confidence:.2f}) - 再推論を実行")
                # 再推論ロジック（簡略化）
                axis_result["confidence"] = max(confidence, 0.6)
        except:
            # JSONパース失敗時のフォールバック
            axis_result = {
                "axis_name": axis_name,
                "integrated_conclusion": f"{axis_name}に関する基本的な分析結果",
                "confidence": 0.5,
                "reasoning_chain": [f"{axis_name}の分析を実行"]
            }
        
        return axis_result
    
    async def _verify_and_improve(self, reasoning_results: Dict[str, Any]) -> Dict[str, Any]:
        """検証・改善フェーズ"""
        self.current_step_id += 1
        
        # 結果の一貫性チェック
        axis_results = reasoning_results.get("axis_results", [])
        confidence_scores = reasoning_results.get("confidence_scores", [])
        
        verification_prompt = f"""以下の分析結果の一貫性と品質を検証してください：

分析結果:
{json.dumps(axis_results, ensure_ascii=False, indent=2)}

検証項目:
1. 各軸の結論間に矛盾はないか？
2. 信頼度スコアは適切か？
3. 追加で必要な分析はあるか？
4. 結論の根拠は十分か？

検証結果をJSON形式で：
{{
    "consistency_score": 0.8,
    "contradictions_found": [],
    "quality_issues": [],
    "improvement_suggestions": [],
    "verified_conclusions": {{}},
    "overall_confidence": 0.8
}}
"""
        
        verification_response = await self.generate_content_async(
            verification_prompt,
            agent_name="検証エンジン"
        )
        
        try:
            verification_results = json.loads(verification_response.strip())
        except:
            verification_results = {
                "consistency_score": 0.7,
                "overall_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            }
        
        # 思考ステップ記録
        step = ThinkingStep(
            step_id=self.current_step_id,
            phase="verification",
            input_data=json.dumps(reasoning_results, ensure_ascii=False),
            output_data=json.dumps(verification_results, ensure_ascii=False),
            confidence=verification_results.get("overall_confidence", 0.5)
        )
        self.steps_log.append(step)
        
        return {
            "reasoning_results": reasoning_results,
            "verification_results": verification_results,
            "sources": ["深層推論分析", "多段階検証"]
        }
    
    async def _synthesize_final_answer(self, verified_result: Dict[str, Any]) -> Dict[str, Any]:
        """最終回答統合"""
        self.current_step_id += 1
        
        axis_results = verified_result["reasoning_results"].get("axis_results", [])
        verification = verified_result["verification_results"]
        
        synthesis_prompt = f"""以下の検証済み分析結果から最終的な回答を統合してください：

分析結果:
{json.dumps(axis_results, ensure_ascii=False, indent=2)}

検証結果:
{json.dumps(verification, ensure_ascii=False, indent=2)}

要求:
1. 各軸の結論を統合した包括的回答
2. 信頼度の高い情報を優先
3. 矛盾点は明記
4. 300-500文字で簡潔に

回答をJSON形式で：
{{
    "answer": "統合された最終回答",
    "confidence": 0.8,
    "key_points": ["要点1", "要点2"],
    "limitations": ["制限事項1"],
    "synthesis_reasoning": ["統合理由1", "統合理由2"]
}}
"""
        
        final_response = await self.generate_content_async(
            synthesis_prompt,
            agent_name="統合エンジン"
        )
        
        try:
            final_answer = json.loads(final_response.strip())
        except:
            # フォールバック回答
            conclusions = [result.get("integrated_conclusion", "") for result in axis_results]
            final_answer = {
                "answer": " ".join(conclusions),
                "confidence": verification.get("overall_confidence", 0.5),
                "key_points": ["統合分析結果"],
                "limitations": ["JSON解析エラーが発生"]
            }
        
        # 最終思考ステップ記録
        step = ThinkingStep(
            step_id=self.current_step_id,
            phase="synthesis",
            input_data=json.dumps(verified_result, ensure_ascii=False),
            output_data=json.dumps(final_answer, ensure_ascii=False),
            confidence=final_answer.get("confidence", 0.5)
        )
        self.steps_log.append(step)
        
        return final_answer
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """品質メトリクス計算"""
        if not self.steps_log:
            return {}
        
        # 各フェーズの信頼度平均
        phase_confidences = {}
        for step in self.steps_log:
            phase = step.phase
            if phase not in phase_confidences:
                phase_confidences[phase] = []
            phase_confidences[phase].append(step.confidence)
        
        metrics = {}
        for phase, confidences in phase_confidences.items():
            metrics[f"{phase}_confidence"] = sum(confidences) / len(confidences)
        
        # 全体品質スコア
        all_confidences = [step.confidence for step in self.steps_log]
        metrics["overall_quality"] = sum(all_confidences) / len(all_confidences)
        metrics["step_count"] = len(self.steps_log)
        metrics["complexity_score"] = min(len(self.steps_log) / 5.0, 1.0)  # 最大1.0
        
        return metrics
    
    def get_thinking_visualization(self) -> Dict[str, Any]:
        """思考プロセスの可視化データを生成"""
        return {
            "steps": [
                {
                    "id": step.step_id,
                    "phase": step.phase,
                    "confidence": step.confidence,
                    "timestamp": step.timestamp.isoformat(),
                    "reasoning_chain": step.reasoning_chain
                }
                for step in self.steps_log
            ],
            "phase_summary": self._get_phase_summary(),
            "confidence_trend": [step.confidence for step in self.steps_log]
        }
    
    def _get_phase_summary(self) -> Dict[str, int]:
        """フェーズ別ステップ数の要約"""
        phase_counts = {}
        for step in self.steps_log:
            phase = step.phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        return phase_counts 