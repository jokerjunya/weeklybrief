#!/usr/bin/env python3
"""
Enhanced DeepResearch - 統合データ収集エンジン

既存のCompanyNewsCollectorとdata-processing.pyの機能を統合し、以下を提供：
- RSS フィード収集
- ニュースAPI統合
- ソーシャルメディア情報収集
- 論文・技術文書収集
- データ正規化・クリーニング
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from company_news_collector import CompanyNewsCollector
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
import hashlib

@dataclass
class DataSource:
    """データソース定義"""
    name: str
    type: str  # "rss", "api", "social", "academic"
    url: str
    priority: int  # 1-10 (高いほど優先)
    reliability_score: float  # 0.0-1.0
    update_frequency: int  # 更新頻度（分）
    last_updated: datetime = None
    active: bool = True

@dataclass
class CollectedItem:
    """収集されたデータアイテム"""
    id: str
    title: str
    content: str
    source: str
    url: str
    published_at: datetime
    collected_at: datetime
    data_type: str  # "news", "social", "academic", "technical"
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataCollector(CompanyNewsCollector):
    """
    統合データ収集エンジン
    
    既存のCompanyNewsCollectorを継承・拡張し、以下の機能を追加：
    - 多様なデータソース対応
    - リアルタイム収集
    - データ品質評価
    - 重複排除
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        super().__init__(config_path)
        
        # 拡張データソース定義
        self.data_sources = {
            # RSS フィード
            "techcrunch": DataSource(
                name="TechCrunch",
                type="rss",
                url="https://techcrunch.com/feed/",
                priority=8,
                reliability_score=0.85,
                update_frequency=60
            ),
            "ars_technica": DataSource(
                name="Ars Technica",
                type="rss", 
                url="https://feeds.arstechnica.com/arstechnica/index",
                priority=9,
                reliability_score=0.9,
                update_frequency=120
            ),
            "the_verge": DataSource(
                name="The Verge",
                type="rss",
                url="https://www.theverge.com/rss/index.xml",
                priority=7,
                reliability_score=0.8,
                update_frequency=60
            ),
            
            # AI 専門ソース
            "ai_news": DataSource(
                name="AI News",
                type="rss",
                url="https://www.artificialintelligence-news.com/feed/",
                priority=8,
                reliability_score=0.8,
                update_frequency=180
            ),
            
            # 学術ソース
            "arxiv_cs_ai": DataSource(
                name="arXiv CS.AI",
                type="academic",
                url="http://export.arxiv.org/rss/cs.AI",
                priority=6,
                reliability_score=0.95,
                update_frequency=1440  # 1日1回
            )
        }
        
        # 収集設定
        self.collection_config = {
            "max_items_per_source": 50,
            "relevance_threshold": 0.3,
            "deduplication_threshold": 0.8,
            "max_collection_time": 300,  # 5分
            "concurrent_sources": 5
        }
        
        # キャッシュとストレージ
        self.collected_items: List[CollectedItem] = []
        self.item_cache = {}
        self.collection_stats = {
            "total_collected": 0,
            "duplicates_removed": 0,
            "low_relevance_filtered": 0,
            "last_collection": None
        }
    
    async def collect_comprehensive_data(
        self, 
        topics: List[str], 
        time_range: timedelta = timedelta(days=7),
        source_types: List[str] = None
    ) -> List[CollectedItem]:
        """
        包括的データ収集
        
        Args:
            topics: 収集対象トピック
            time_range: 収集対象期間
            source_types: 収集するソースタイプ（None=全て）
        
        Returns:
            List[CollectedItem]: 収集されたデータ
        """
        print(f"🔍 包括的データ収集開始: {len(topics)}トピック, {time_range.days}日間")
        
        # ソースフィルタリング
        active_sources = {
            name: source for name, source in self.data_sources.items()
            if source.active and (source_types is None or source.type in source_types)
        }
        
        print(f"📡 {len(active_sources)}のデータソースから収集中...")
        
        # 並行収集実行
        collection_tasks = []
        semaphore = asyncio.Semaphore(self.collection_config["concurrent_sources"])
        
        for source_name, source in active_sources.items():
            task = self._collect_from_source(source, topics, time_range, semaphore)
            collection_tasks.append(task)
        
        # 全ての収集タスクを実行
        collection_results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # 結果を統合
        all_items = []
        for result in collection_results:
            if isinstance(result, list):
                all_items.extend(result)
            elif isinstance(result, Exception):
                print(f"⚠️ 収集エラー: {result}")
        
        # データクリーニングと重複排除
        cleaned_items = await self._clean_and_deduplicate(all_items)
        
        # 関連性フィルタリング
        relevant_items = self._filter_by_relevance(cleaned_items, topics)
        
        # 収集統計更新
        self._update_collection_stats(all_items, cleaned_items, relevant_items)
        
        print(f"✅ データ収集完了: {len(relevant_items)}件（元: {len(all_items)}件）")
        
        self.collected_items = relevant_items
        return relevant_items
    
    async def _collect_from_source(
        self, 
        source: DataSource, 
        topics: List[str], 
        time_range: timedelta,
        semaphore: asyncio.Semaphore
    ) -> List[CollectedItem]:
        """単一ソースからデータ収集"""
        async with semaphore:
            try:
                print(f"📥 {source.name}から収集中...")
                
                if source.type == "rss":
                    return await self._collect_from_rss(source, topics, time_range)
                elif source.type == "api":
                    return await self._collect_from_api(source, topics, time_range)
                elif source.type == "academic":
                    return await self._collect_from_academic(source, topics, time_range)
                else:
                    print(f"⚠️ 未対応のソースタイプ: {source.type}")
                    return []
                    
            except Exception as e:
                print(f"❌ {source.name}収集エラー: {e}")
                return []
    
    async def _collect_from_rss(
        self, 
        source: DataSource, 
        topics: List[str], 
        time_range: timedelta
    ) -> List[CollectedItem]:
        """RSS フィードからデータ収集"""
        try:
            import feedparser
            
            # RSS フィードを取得
            feed = feedparser.parse(source.url)
            
            if not feed.entries:
                print(f"⚠️ {source.name}: RSSエントリが見つかりません")
                return []
            
            items = []
            cutoff_date = datetime.now() - time_range
            
            for entry in feed.entries[:self.collection_config["max_items_per_source"]]:
                # 日付チェック
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                    if published_at < cutoff_date:
                        continue
                except:
                    published_at = datetime.now()
                
                # アイテム作成
                item = CollectedItem(
                    id=self._generate_item_id(entry.link),
                    title=entry.title,
                    content=entry.get('summary', ''),
                    source=source.name,
                    url=entry.link,
                    published_at=published_at,
                    collected_at=datetime.now(),
                    data_type="news",
                    relevance_score=self._calculate_relevance(entry.title + " " + entry.get('summary', ''), topics),
                    metadata={
                        "author": entry.get('author', ''),
                        "tags": entry.get('tags', []),
                        "rss_source": source.url
                    }
                )
                items.append(item)
            
            print(f"📰 {source.name}: {len(items)}件収集")
            return items
            
        except Exception as e:
            print(f"❌ RSS収集エラー ({source.name}): {e}")
            return []
    
    async def _collect_from_api(
        self, 
        source: DataSource, 
        topics: List[str], 
        time_range: timedelta
    ) -> List[CollectedItem]:
        """API からデータ収集"""
        # 将来の拡張用：News API、Twitter API、GitHub API等
        try:
            async with aiohttp.ClientSession() as session:
                # API実装は具体的なAPIによって変わるため、
                # ここでは基本的な構造のみ実装
                items = []
                
                # API呼び出し例（実際のAPIに合わせて実装）
                # async with session.get(source.url) as response:
                #     data = await response.json()
                #     # データ処理...
                
                print(f"🔌 {source.name}: API収集（未実装）")
                return items
                
        except Exception as e:
            print(f"❌ API収集エラー ({source.name}): {e}")
            return []
    
    async def _collect_from_academic(
        self, 
        source: DataSource, 
        topics: List[str], 
        time_range: timedelta
    ) -> List[CollectedItem]:
        """学術ソースからデータ収集"""
        try:
            import feedparser
            
            feed = feedparser.parse(source.url)
            items = []
            cutoff_date = datetime.now() - time_range
            
            for entry in feed.entries[:self.collection_config["max_items_per_source"]]:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                    if published_at < cutoff_date:
                        continue
                except:
                    published_at = datetime.now()
                
                # 学術論文の場合、アブストラクトを含める
                content = entry.get('summary', '')
                if hasattr(entry, 'arxiv_comment'):
                    content += f"\n\nComment: {entry.arxiv_comment}"
                
                item = CollectedItem(
                    id=self._generate_item_id(entry.link),
                    title=entry.title,
                    content=content,
                    source=source.name,
                    url=entry.link,
                    published_at=published_at,
                    collected_at=datetime.now(),
                    data_type="academic",
                    relevance_score=self._calculate_relevance(entry.title + " " + content, topics),
                    metadata={
                        "authors": entry.get('author', ''),
                        "arxiv_id": entry.get('id', '').split('/')[-1] if 'arxiv' in source.name else '',
                        "categories": entry.get('tags', []),
                        "academic_source": source.url
                    }
                )
                items.append(item)
            
            print(f"🎓 {source.name}: {len(items)}件収集")
            return items
            
        except Exception as e:
            print(f"❌ 学術収集エラー ({source.name}): {e}")
            return []
    
    def _calculate_relevance(self, text: str, topics: List[str]) -> float:
        """テキストの関連性スコアを計算"""
        if not text or not topics:
            return 0.0
        
        text_lower = text.lower()
        topic_matches = 0
        total_weight = 0
        
        for topic in topics:
            topic_lower = topic.lower()
            
            # 完全一致
            if topic_lower in text_lower:
                topic_matches += 2
            
            # 部分一致
            topic_words = topic_lower.split()
            for word in topic_words:
                if len(word) > 2 and word in text_lower:
                    topic_matches += 1
            
            total_weight += 2  # 完全一致の最大スコア
        
        relevance_score = min(topic_matches / max(total_weight, 1), 1.0)
        return relevance_score
    
    async def _clean_and_deduplicate(self, items: List[CollectedItem]) -> List[CollectedItem]:
        """データクリーニングと重複排除"""
        if not items:
            return []
        
        print(f"🧹 データクリーニング開始: {len(items)}件")
        
        # 1. 基本クリーニング
        cleaned_items = []
        for item in items:
            # タイトルと内容の基本チェック
            if len(item.title.strip()) < 10:
                continue
            if len(item.content.strip()) < 20:
                continue
            
            # 不正なURL除外
            if not item.url or not item.url.startswith('http'):
                continue
            
            cleaned_items.append(item)
        
        # 2. 重複排除
        unique_items = []
        seen_hashes = set()
        
        for item in cleaned_items:
            # タイトルと内容の組み合わせでハッシュを計算
            content_hash = self._calculate_content_hash(item.title, item.content)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
        
        duplicates_removed = len(cleaned_items) - len(unique_items)
        if duplicates_removed > 0:
            print(f"🔄 重複除去: {duplicates_removed}件")
        
        return unique_items
    
    def _calculate_content_hash(self, title: str, content: str) -> str:
        """コンテンツのハッシュ値を計算"""
        # タイトルと内容の最初の200文字を使ってハッシュを計算
        content_sample = (title + " " + content)[:200].lower().strip()
        return hashlib.md5(content_sample.encode()).hexdigest()
    
    def _filter_by_relevance(self, items: List[CollectedItem], topics: List[str]) -> List[CollectedItem]:
        """関連性によるフィルタリング"""
        threshold = self.collection_config["relevance_threshold"]
        relevant_items = [item for item in items if item.relevance_score >= threshold]
        
        filtered_count = len(items) - len(relevant_items)
        if filtered_count > 0:
            print(f"🎯 関連性フィルタ: {filtered_count}件除外")
        
        # 関連性スコア順でソート
        relevant_items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_items
    
    def _generate_item_id(self, url: str) -> str:
        """アイテムIDを生成"""
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def _update_collection_stats(
        self, 
        raw_items: List[CollectedItem], 
        cleaned_items: List[CollectedItem], 
        final_items: List[CollectedItem]
    ) -> None:
        """収集統計を更新"""
        self.collection_stats.update({
            "total_collected": len(raw_items),
            "duplicates_removed": len(raw_items) - len(cleaned_items),
            "low_relevance_filtered": len(cleaned_items) - len(final_items),
            "last_collection": datetime.now(),
            "sources_used": len(set(item.source for item in raw_items)),
            "final_items": len(final_items)
        })
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """収集サマリーを取得"""
        if not self.collected_items:
            return {"message": "まだデータが収集されていません"}
        
        # ソース別統計
        source_stats = {}
        type_stats = {}
        
        for item in self.collected_items:
            # ソース別
            if item.source not in source_stats:
                source_stats[item.source] = 0
            source_stats[item.source] += 1
            
            # タイプ別
            if item.data_type not in type_stats:
                type_stats[item.data_type] = 0
            type_stats[item.data_type] += 1
        
        # 関連性スコア統計
        relevance_scores = [item.relevance_score for item in self.collected_items]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        return {
            "collection_stats": self.collection_stats,
            "source_breakdown": source_stats,
            "type_breakdown": type_stats,
            "relevance_stats": {
                "average": avg_relevance,
                "max": max(relevance_scores),
                "min": min(relevance_scores)
            },
            "time_range": {
                "earliest": min(item.published_at for item in self.collected_items).isoformat(),
                "latest": max(item.published_at for item in self.collected_items).isoformat()
            }
        }
    
    async def collect_for_research(self, research_topic: str) -> List[CollectedItem]:
        """
        Enhanced DeepResearch用のデータ収集
        
        Args:
            research_topic: 研究トピック
        
        Returns:
            List[CollectedItem]: 関連データ
        """
        # トピックをキーワードに分解
        topics = [research_topic]
        
        # AI関連のキーワードを追加（コンテキスト拡張）
        ai_keywords = ["artificial intelligence", "machine learning", "AI", "LLM", "neural network"]
        topics.extend(ai_keywords)
        
        # 過去1週間のデータを収集
        time_range = timedelta(days=7)
        
        # ニュースと学術論文を重点的に収集
        source_types = ["rss", "academic"]
        
        collected_data = await self.collect_comprehensive_data(
            topics=topics,
            time_range=time_range,
            source_types=source_types
        )
        
        # トップ20件に絞り込み（品質重視）
        top_items = sorted(collected_data, key=lambda x: x.relevance_score, reverse=True)[:20]
        
        print(f"🎯 研究用データ収集完了: {len(top_items)}件（関連度: {top_items[0].relevance_score:.2f} - {top_items[-1].relevance_score:.2f}）")
        
        return top_items 