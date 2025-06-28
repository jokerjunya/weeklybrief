#!/usr/bin/env python3
"""
Enhanced DeepResearch - 信頼性検証エンジン

既存のEfficientNewsAnalyzerを継承・拡張し、以下の機能を追加：
- クロスリファレンス検証
- ファクトチェック
- 信頼性スコア算出
- 情報源の品質評価
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from news_analyzer import EfficientNewsAnalyzer
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
import hashlib

@dataclass
class VerificationResult:
    """検証結果"""
    claim: str
    verification_status: str  # "verified", "disputed", "unverified", "unknown"
    confidence_score: float
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    information_sources: List[str]
    quality_score: float
    verification_timestamp: datetime = None

    def __post_init__(self):
        if self.verification_timestamp is None:
            self.verification_timestamp = datetime.now()

@dataclass 
class SourceQuality:
    """情報源品質評価"""
    source_name: str
    reliability_score: float  # 0.0-1.0
    expertise_score: float    # 0.0-1.0
    bias_score: float        # 0.0-1.0 (低いほど偏見が少ない)
    freshness_score: float   # 0.0-1.0 (情報の新鮮度)
    overall_quality: float   # 総合品質スコア

class VerificationEngine(EfficientNewsAnalyzer):
    """
    信頼性検証エンジン
    
    既存のEfficientNewsAnalyzerを継承し、以下の機能を追加：
    - 情報の信頼性検証
    - クロスリファレンス分析
    - 情報源品質評価
    - ファクトチェック機能
    """
    
    def __init__(self):
        super().__init__()
        
        # 信頼できる情報源の定義
        self.trusted_sources = {
            "TechCrunch": {"reliability": 0.85, "expertise": 0.9, "bias": 0.8},
            "The Verge": {"reliability": 0.8, "expertise": 0.85, "bias": 0.75},
            "Ars Technica": {"reliability": 0.9, "expertise": 0.95, "bias": 0.85},
            "Reuters": {"reliability": 0.95, "expertise": 0.85, "bias": 0.9},
            "Bloomberg": {"reliability": 0.9, "expertise": 0.9, "bias": 0.8},
            "VentureBeat": {"reliability": 0.75, "expertise": 0.8, "bias": 0.7},
            "MIT Technology Review": {"reliability": 0.95, "expertise": 0.95, "bias": 0.9}
        }
        
        # 検証設定
        self.verification_config = {
            "min_sources_for_verification": 2,
            "cross_reference_threshold": 0.7,
            "fact_check_confidence_threshold": 0.8,
            "max_verification_time": 300  # 5分
        }
        
        # 検証キャッシュ
        self.verification_cache = {}
    
    async def verify_claims(self, claims: List[str], context: Dict[str, Any] = None) -> List[VerificationResult]:
        """
        複数の主張を検証
        
        Args:
            claims: 検証する主張のリスト
            context: 追加のコンテキスト情報
        
        Returns:
            List[VerificationResult]: 検証結果のリスト
        """
        verification_results = []
        
        print(f"🔍 {len(claims)}件の主張を検証中...")
        
        for i, claim in enumerate(claims, 1):
            print(f"📝 検証 {i}/{len(claims)}: {claim[:50]}...")
            
            # キャッシュチェック
            cache_key = self._get_verification_cache_key(claim)
            if cache_key in self.verification_cache:
                print("💾 キャッシュからロード")
                verification_results.append(self.verification_cache[cache_key])
                continue
            
            # 検証実行
            try:
                result = await self._verify_single_claim(claim, context or {})
                verification_results.append(result)
                
                # キャッシュに保存
                self.verification_cache[cache_key] = result
                
            except Exception as e:
                print(f"⚠️ 検証エラー: {e}")
                # エラー時のフォールバック結果
                result = VerificationResult(
                    claim=claim,
                    verification_status="unknown",
                    confidence_score=0.0,
                    supporting_evidence=[],
                    contradicting_evidence=[],
                    information_sources=[],
                    quality_score=0.0
                )
                verification_results.append(result)
        
        print(f"✅ 検証完了: {len(verification_results)}件")
        return verification_results
    
    async def _verify_single_claim(self, claim: str, context: Dict[str, Any]) -> VerificationResult:
        """単一の主張を検証"""
        
        # Step 1: クロスリファレンス分析
        cross_ref_analysis = await self._cross_reference_analysis(claim, context)
        
        # Step 2: ファクトチェック
        fact_check_result = await self._fact_check_claim(claim, cross_ref_analysis)
        
        # Step 3: 情報源品質評価
        source_quality = self._evaluate_source_quality(cross_ref_analysis["sources"])
        
        # Step 4: 総合判定
        verification_status, confidence_score = self._determine_verification_status(
            cross_ref_analysis, fact_check_result, source_quality
        )
        
        return VerificationResult(
            claim=claim,
            verification_status=verification_status,
            confidence_score=confidence_score,
            supporting_evidence=cross_ref_analysis["supporting_evidence"],
            contradicting_evidence=cross_ref_analysis["contradicting_evidence"],
            information_sources=cross_ref_analysis["sources"],
            quality_score=source_quality["overall_quality"]
        )
    
    async def _cross_reference_analysis(self, claim: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """クロスリファレンス分析"""
        
        # AI分析でクロスリファレンス情報を取得
        cross_ref_prompt = f"""以下の主張について、クロスリファレンス分析を実行してください：

主張: {claim}
コンテキスト: {json.dumps(context, ensure_ascii=False)}

分析項目:
1. この主張を支持する証拠・情報源
2. この主張に矛盾する証拠・情報源  
3. 関連する既知の事実
4. 検証に必要な追加情報

回答をJSON形式で：
{{
    "supporting_evidence": ["支持する証拠1", "支持する証拠2"],
    "contradicting_evidence": ["矛盾する証拠1"],
    "related_facts": ["関連事実1", "関連事実2"],
    "sources": ["情報源1", "情報源2"],
    "confidence": 0.8,
    "analysis_summary": "分析の要約"
}}
"""
        
        try:
            response = await self.llm.generate_content_async(
                cross_ref_prompt,
                agent_name="クロスリファレンス分析エンジン"
            )
            
            cross_ref_data = json.loads(response.strip())
            
            # データの正規化
            if "supporting_evidence" not in cross_ref_data:
                cross_ref_data["supporting_evidence"] = []
            if "contradicting_evidence" not in cross_ref_data:
                cross_ref_data["contradicting_evidence"] = []
            if "sources" not in cross_ref_data:
                cross_ref_data["sources"] = ["AI分析"]
                
            return cross_ref_data
            
        except Exception as e:
            print(f"⚠️ クロスリファレンス分析エラー: {e}")
            return {
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "sources": ["分析エラー"],
                "confidence": 0.0
            }
    
    async def _fact_check_claim(self, claim: str, cross_ref_data: Dict[str, Any]) -> Dict[str, Any]:
        """ファクトチェック実行"""
        
        fact_check_prompt = f"""以下の主張のファクトチェックを実行してください：

主張: {claim}

参考情報:
支持する証拠: {cross_ref_data.get('supporting_evidence', [])}
矛盾する証拠: {cross_ref_data.get('contradicting_evidence', [])}

ファクトチェック項目:
1. 主張の具体的な要素の検証
2. 数値・日付・人名・企業名の正確性
3. 論理的整合性
4. 既知の事実との照合

回答をJSON形式で：
{{
    "fact_check_status": "accurate|partially_accurate|inaccurate|unverifiable",
    "accuracy_score": 0.8,
    "verified_facts": ["検証済み事実1"],
    "disputed_facts": ["争点のある事実1"],
    "logical_consistency": 0.9,
    "fact_check_summary": "ファクトチェック要約"
}}
"""
        
        try:
            response = await self.llm.generate_content_async(
                fact_check_prompt,
                agent_name="ファクトチェックエンジン"
            )
            
            fact_check_result = json.loads(response.strip())
            
            # デフォルト値設定
            if "accuracy_score" not in fact_check_result:
                fact_check_result["accuracy_score"] = 0.5
            if "logical_consistency" not in fact_check_result:
                fact_check_result["logical_consistency"] = 0.5
                
            return fact_check_result
            
        except Exception as e:
            print(f"⚠️ ファクトチェックエラー: {e}")
            return {
                "fact_check_status": "unverifiable",
                "accuracy_score": 0.0,
                "logical_consistency": 0.0
            }
    
    def _evaluate_source_quality(self, sources: List[str]) -> Dict[str, float]:
        """情報源の品質評価"""
        if not sources:
            return {"overall_quality": 0.0}
        
        quality_scores = []
        
        for source in sources:
            source_quality = self._get_source_quality(source)
            quality_scores.append(source_quality.overall_quality)
        
        # 平均品質スコア
        overall_quality = sum(quality_scores) / len(quality_scores)
        
        return {
            "overall_quality": overall_quality,
            "source_count": len(sources),
            "max_quality": max(quality_scores) if quality_scores else 0.0,
            "min_quality": min(quality_scores) if quality_scores else 0.0
        }
    
    def _get_source_quality(self, source_name: str) -> SourceQuality:
        """単一の情報源の品質を評価"""
        
        # 既知の信頼できる情報源をチェック
        for trusted_source, scores in self.trusted_sources.items():
            if trusted_source.lower() in source_name.lower():
                overall_quality = (
                    scores["reliability"] * 0.4 +
                    scores["expertise"] * 0.3 + 
                    scores["bias"] * 0.3
                )
                
                return SourceQuality(
                    source_name=source_name,
                    reliability_score=scores["reliability"],
                    expertise_score=scores["expertise"],
                    bias_score=scores["bias"],
                    freshness_score=0.8,  # デフォルト値
                    overall_quality=overall_quality
                )
        
        # 未知の情報源の場合、中程度の品質スコアを設定
        return SourceQuality(
            source_name=source_name,
            reliability_score=0.5,
            expertise_score=0.5,
            bias_score=0.5,
            freshness_score=0.5,
            overall_quality=0.5
        )
    
    def _determine_verification_status(
        self, 
        cross_ref_data: Dict[str, Any], 
        fact_check_result: Dict[str, Any], 
        source_quality: Dict[str, float]
    ) -> tuple[str, float]:
        """総合的な検証ステータスと信頼度を決定"""
        
        # 各要素のスコア
        cross_ref_confidence = cross_ref_data.get("confidence", 0.0)
        fact_check_accuracy = fact_check_result.get("accuracy_score", 0.0)
        logical_consistency = fact_check_result.get("logical_consistency", 0.0)
        source_quality_score = source_quality.get("overall_quality", 0.0)
        
        # 重み付き平均で総合信頼度を計算
        confidence_score = (
            cross_ref_confidence * 0.3 +
            fact_check_accuracy * 0.4 +
            logical_consistency * 0.2 +
            source_quality_score * 0.1
        )
        
        # 検証ステータスの決定
        fact_check_status = fact_check_result.get("fact_check_status", "unverifiable")
        
        if confidence_score >= 0.8 and fact_check_status in ["accurate", "partially_accurate"]:
            verification_status = "verified"
        elif confidence_score >= 0.6 and fact_check_status == "partially_accurate":
            verification_status = "partially_verified"
        elif confidence_score < 0.4 or fact_check_status == "inaccurate":
            verification_status = "disputed"
        else:
            verification_status = "unverified"
        
        return verification_status, confidence_score
    
    def _get_verification_cache_key(self, claim: str) -> str:
        """検証キャッシュキーを生成"""
        return hashlib.md5(claim.encode()).hexdigest()
    
    async def verify_research_result(self, research_result) -> Dict[str, Any]:
        """
        Enhanced DeepResearchの結果を検証
        
        Args:
            research_result: ResearchResultオブジェクト
        
        Returns:
            Dict: 検証結果
        """
        # 主要な主張を抽出
        claims = []
        claims.append(research_result.final_answer)
        
        # 思考ステップからも主張を抽出
        for step in research_result.thinking_steps:
            if step.phase == "reasoning":
                try:
                    step_data = json.loads(step.output_data)
                    conclusion = step_data.get("integrated_conclusion", "")
                    if conclusion and len(conclusion) > 20:
                        claims.append(conclusion)
                except:
                    continue
        
        # 検証実行
        verification_results = await self.verify_claims(claims)
        
        # 検証サマリー作成
        verified_count = sum(1 for vr in verification_results if vr.verification_status == "verified")
        disputed_count = sum(1 for vr in verification_results if vr.verification_status == "disputed")
        avg_confidence = sum(vr.confidence_score for vr in verification_results) / len(verification_results)
        avg_quality = sum(vr.quality_score for vr in verification_results) / len(verification_results)
        
        return {
            "verification_summary": {
                "total_claims": len(verification_results),
                "verified_claims": verified_count,
                "disputed_claims": disputed_count,
                "average_confidence": avg_confidence,
                "average_quality": avg_quality
            },
            "detailed_results": verification_results,
            "overall_trustworthiness": avg_confidence * avg_quality,
            "recommendation": self._generate_trust_recommendation(avg_confidence, avg_quality)
        }
    
    def _generate_trust_recommendation(self, confidence: float, quality: float) -> str:
        """信頼性に基づく推奨事項を生成"""
        trust_score = confidence * quality
        
        if trust_score >= 0.8:
            return "高信頼性：この分析結果は十分に信頼できます。"
        elif trust_score >= 0.6:
            return "中程度の信頼性：追加検証を推奨します。"
        elif trust_score >= 0.4:
            return "低信頼性：慎重な判断が必要です。"
        else:
            return "信頼性不足：再分析を推奨します。" 