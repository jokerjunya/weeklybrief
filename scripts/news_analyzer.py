#!/usr/bin/env python3
"""
ニュース分析・重要度判定・日本語要約システム（無料版）
ローカルLLM（Ollama）を使用してAI分析を実行
"""

import json
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from qwen3_llm import Qwen3Llm
import hashlib
import os
import asyncio
import aiohttp

@dataclass
class NewsItem:
    title: str
    url: str
    published_at: str
    summary: str
    content: str
    company_id: str
    source_type: str
    importance_score: float = 0.0
    japanese_summary: str = ""
    tags: List[str] = None

class EfficientNewsAnalyzer:
    """効率化されたニュース分析器"""
    
    def __init__(self):
        self.llm = Qwen3Llm(model="ollama/qwen3:30b-a3b", api_url="http://localhost:11434/api/generate")
        self.cache_file = "cache/news_analysis_cache.json"
        self.cache = self.load_cache()
        
        # 段階的フィルタリング設定
        self.quick_filters = {
            'min_title_length': 20,
            'max_title_length': 200,
            'exclude_keywords': [
                'crypto', 'bitcoin', 'ethereum', 'nft', 'blockchain',
                'stock price', '株価', 'market close', 'earnings',
                'covid', 'coronavirus', 'pandemic'
            ],
            'priority_keywords': [
                'ai', 'artificial intelligence', 'machine learning', 'llm',
                'gpt', 'gemini', 'claude', 'chatbot', 'neural network',
                'deep learning', 'generative', '人工知能', 'AI'
            ]
        }
        
        # 企業別重要度乗数
        self.company_multipliers = {
            "OpenAI": 1.5,
            "Google AI": 1.4,
            "Anthropic": 1.3,
            "Meta AI": 1.2,
            "Microsoft AI": 1.2,
            "ElevenLabs": 1.1,
            "Perplexity": 1.1,
            "Genspark": 1.0,
            "Lovable": 1.0,
            "Stability AI": 1.0
        }

    def get_analysis_period(self) -> Dict[str, str]:
        """分析対象期間を取得"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        return {
            "start_date": start_date.strftime("%Y年%m月%d日"),
            "end_date": end_date.strftime("%Y年%m月%d日"),
            "period_description": f"{start_date.strftime('%m/%d')}〜{end_date.strftime('%m/%d')}（過去1週間）"
        }

    async def generate_weekly_summary(self, analyzed_news: List[Dict]) -> str:
        """週次サマリーを生成（300-400文字）"""
        if not analyzed_news:
            return "今週はAI・テクノロジー関連の重要なニュースは確認されませんでした。"
        
        # 上位5件のニュースを抽出
        top_news = sorted(analyzed_news, key=lambda x: x.get('score', 0), reverse=True)[:5]
        
        # 企業別統計
        company_stats = {}
        for news in top_news:
            company = news.get('company_id', 'unknown')
            if company not in company_stats:
                company_stats[company] = 0
            company_stats[company] += 1
        
        # サマリー生成プロンプト
        prompt = f"""以下のAI・テクノロジーニュースから週次サマリーを300-400文字で生成してください。

要求：
- 全体的なトレンドや傾向を分析
- 主要企業の動向を含める
- ビジネスへの影響を考慮
- 読みやすく簡潔に
- 必ず300-400文字以内

今週の主要ニュース：
"""
        
        for i, news in enumerate(top_news, 1):
            prompt += f"{i}. {news.get('title', '')} (重要度: {news.get('score', 0):.1f})\n"
            prompt += f"   要約: {news.get('summary_jp', '')}\n\n"
        
        prompt += f"\n企業別ニュース数: {dict(sorted(company_stats.items(), key=lambda x: x[1], reverse=True))}"
        
        try:
            print("📝 週次サマリー生成中...")
            summary = await self.llm.generate_content_async(prompt)
            
            # 文字数調整
            if len(summary) > 400:
                summary = summary[:397] + "..."
            elif len(summary) < 250:
                summary += "引き続きAI・テクノロジー分野の動向に注目していきます。"
            
            return summary.strip()
            
        except Exception as e:
            print(f"⚠️ サマリー生成エラー: {e}")
            # フォールバック サマリー
            main_companies = list(company_stats.keys())[:3]
            return f"今週は{', '.join(main_companies)}などを中心としたAI・テクノロジー関連の発表が相次ぎました。特に{top_news[0].get('title', '')[:50]}などの動向が注目されます。AI技術の実用化と企業間の戦略的提携が加速しており、業界全体の競争が激化しています。"

    def load_cache(self) -> Dict:
        """キャッシュファイルを読み込み"""
        os.makedirs("cache", exist_ok=True)
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        """キャッシュファイルを保存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get_cache_key(self, news_item: Dict) -> str:
        """ニュース記事のキャッシュキーを生成"""
        content = f"{news_item['title']}{news_item['url']}"
        return hashlib.md5(content.encode()).hexdigest()

    def apply_quick_filters(self, news_list: List[Dict]) -> List[Dict]:
        """段階的フィルタリングを適用"""
        filtered_news = []
        
        for news in news_list:
            title = news.get('title', '').lower()
            
            # 基本フィルタ
            if (len(title) < self.quick_filters['min_title_length'] or 
                len(title) > self.quick_filters['max_title_length']):
                continue
            
            # 除外キーワードチェック
            if any(keyword in title for keyword in self.quick_filters['exclude_keywords']):
                continue
            
            # 優先キーワードボーナス
            priority_score = sum(2 for keyword in self.quick_filters['priority_keywords'] 
                                if keyword in title)
            
            # 企業関連度チェック
            company_relevance = 0
            for company in self.company_multipliers.keys():
                if company.lower() in title or company.lower() in news.get('description', '').lower():
                    company_relevance += 3
                    break
            
            # 基本スコア計算（ルールベース）
            base_score = 3.0 + priority_score + company_relevance
            
            # 最低スコア以上のもののみ通す
            if base_score >= 4.0:  # AI判定対象を絞り込み
                news['base_score'] = base_score
                filtered_news.append(news)
        
        # スコア順でソート、上位50件のみAI分析対象
        filtered_news.sort(key=lambda x: x['base_score'], reverse=True)
        return filtered_news[:50]  # AI分析対象を50件に制限

    async def batch_analyze_with_ai(self, news_batch: List[Dict]) -> List[Dict]:
        """バッチでAI分析を実行"""
        if not news_batch:
            return []
        
        # バッチプロンプト作成
        batch_prompt = """以下のニュース記事群を分析し、各記事について以下の形式でJSONで回答してください：

{
  "analyses": [
    {
      "index": 0,
      "importance_score": 5.5,
      "japanese_summary": "記事の詳細要約（80-120文字程度）"
    }
  ]
}

評価基準：
- AI/機械学習の技術革新: +2点
- 大手企業の重要発表: +1.5点
- 業界への影響度: +1点
- 実用性・商用化: +1点

記事一覧：
"""
        
        for i, news in enumerate(news_batch):
            batch_prompt += f"\n{i}. タイトル: {news['title']}\n"
            batch_prompt += f"   説明: {news.get('description', '')[:100]}...\n"
        
        try:
            print(f"🤖 AI分析中... ({len(news_batch)}件をバッチ処理)")
            response = await self.llm.generate_content_async(batch_prompt)
            
            # JSON解析
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                analyses = result.get('analyses', [])
                
                # 結果をニュースに適用
                for analysis in analyses:
                    idx = analysis.get('index', 0)
                    if 0 <= idx < len(news_batch):
                        news_batch[idx]['ai_score'] = analysis.get('importance_score', 5.0)
                        news_batch[idx]['summary_jp'] = analysis.get('japanese_summary', '')
                
                return news_batch
            
        except Exception as e:
            print(f"⚠️ バッチAI分析エラー: {e}")
            # フォールバック: 基本スコアを使用
            for news in news_batch:
                news['ai_score'] = news.get('base_score', 5.0)
                news['summary_jp'] = f"{news['title'][:30]}..."
        
        return news_batch

    async def analyze_news_efficient(self, news_list: List[Dict]) -> List[Dict]:
        """効率化されたニュース分析"""
        print(f"📊 効率化分析開始: {len(news_list)}件")
        
        # 1. 段階的フィルタリング
        print("🔍 段階的フィルタリング実行中...")
        filtered_news = self.apply_quick_filters(news_list)
        print(f"   ✅ フィルタリング後: {len(filtered_news)}件 (削減率: {((len(news_list)-len(filtered_news))/len(news_list)*100):.1f}%)")
        
        # 2. キャッシュチェック
        print("💾 キャッシュチェック中...")
        cache_hits = 0
        ai_analysis_needed = []
        
        for news in filtered_news:
            cache_key = self.get_cache_key(news)
            if cache_key in self.cache:
                # キャッシュヒット
                cached_data = self.cache[cache_key]
                news.update(cached_data)
                cache_hits += 1
            else:
                ai_analysis_needed.append(news)
        
        print(f"   ✅ キャッシュヒット: {cache_hits}件, AI分析必要: {len(ai_analysis_needed)}件")
        
        # 3. バッチAI分析
        if ai_analysis_needed:
            print("🤖 バッチAI分析実行中...")
            batch_size = 10  # 10件ずつバッチ処理
            
            for i in range(0, len(ai_analysis_needed), batch_size):
                batch = ai_analysis_needed[i:i+batch_size]
                analyzed_batch = await self.batch_analyze_with_ai(batch)
                
                # キャッシュに保存
                for news in analyzed_batch:
                    cache_key = self.get_cache_key(news)
                    self.cache[cache_key] = {
                        'ai_score': news.get('ai_score', 5.0),
                        'summary_jp': news.get('summary_jp', '')
                    }
        
        # 4. 最終スコア計算
        print("📊 最終スコア計算中...")
        for news in filtered_news:
            base_score = news.get('base_score', 5.0)
            ai_score = news.get('ai_score', 5.0)
            
            # 企業別乗数適用
            company = news.get('company', 'その他')
            multiplier = self.company_multipliers.get(company, 1.0)
            
            # 最終スコア = (基本スコア + AI スコア) / 2 * 企業乗数
            final_score = ((base_score + ai_score) / 2) * multiplier
            news['score'] = round(final_score, 1)
        
        # 5. キャッシュ保存
        self.save_cache()
        
        # 6. スコア順ソート
        filtered_news.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ 効率化分析完了: 最高スコア {filtered_news[0]['score']:.1f}")
        return filtered_news

# 従来のNewsAnalyzerクラスも残す（互換性のため）
class NewsAnalyzer:
    """従来のニュース分析器（互換性維持）"""
    
    def __init__(self):
        self.efficient_analyzer = EfficientNewsAnalyzer()
    
    async def analyze_news(self, news_list: List[Dict], progress_callback=None) -> List[Dict]:
        """効率化分析器に転送"""
        return await self.efficient_analyzer.analyze_news_efficient(news_list)

def analyze_company_news(news_data: List[Dict[str, Any]], top_n: int = 10) -> List[NewsItem]:
    """
    企業ニュースの分析（メイン関数）
    
    Args:
        news_data: 収集したニュースデータ
        top_n: 上位何件を返すか
        
    Returns:
        分析済みニュース記事のリスト
    """
    analyzer = NewsAnalyzer()
    
    # Qwen3の利用可能性をチェック
    if analyzer.is_qwen3_available():
        print("🤖 Qwen3 LLM を使用して分析を実行します")
    else:
        print("⚠️ Qwen3 LLM が利用できません。ルールベース分析のみ実行します")
    
    # 分析実行
    analyzed_items = analyzer.analyze_news(news_data, top_n)
    
    return analyzed_items

if __name__ == "__main__":
    # テスト用のサンプルデータ
    sample_news = [
        {
            "title": "OpenAI Announces GPT-5 with Revolutionary Capabilities",
            "url": "https://example.com/gpt5",
            "published_at": "2025-06-22T10:00:00Z",
            "summary": "OpenAI unveils GPT-5 with groundbreaking multimodal capabilities",
            "content": "OpenAI today announced GPT-5, featuring advanced reasoning and multimodal processing...",
            "company_id": "openai",
            "source_type": "rss"
        }
    ]
    
    # 分析テスト
    results = analyze_company_news(sample_news, top_n=5)
    
    print(f"\n📊 分析結果:")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item.title}")
        print(f"   重要度: {item.importance_score:.1f}")
        print(f"   企業: {item.company_id}")
        if item.japanese_summary:
            print(f"   要約: {item.japanese_summary[:100]}...")
        print() 