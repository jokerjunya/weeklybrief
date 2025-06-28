"""
Enhanced DeepResearch - AI駆動深層分析システム

Qwen3:30bローカルLLMを核とした高度な情報分析システム
- 多段階推論エンジン（Chain-of-Thought）
- 信頼性検証システム
- 思考プロセス可視化
- 反復的分析・改善

既存資産の継承:
- Qwen3Llm (scripts/qwen3_llm.py) → reasoning_engine.py
- LocalLLMSummarizer (scripts/local_llm_summarizer.py) → 統合
- EfficientNewsAnalyzer (scripts/news_analyzer.py) → verification_engine.py
"""

from .reasoning_engine import EnhancedQwen3Llm, ResearchResult
from .verification_engine import VerificationEngine
from .data_collector import DataCollector
from .thinking_visualizer import ThinkingVisualizer
from .data_manager import DataManager

__version__ = "2.0.0"
__author__ = "WeeklyReport Team"

__all__ = [
    "EnhancedQwen3Llm",
    "ResearchResult", 
    "VerificationEngine",
    "DataCollector",
    "ThinkingVisualizer",
    "DataManager"
] 