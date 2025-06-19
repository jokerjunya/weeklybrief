#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ローカルLLM（Qwen3）ニュース要約機能

このモジュールはOllamaを使用してQwen3モデルで
英語のニュース記事を日本語に要約します。
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class LocalLLMSummarizer:
    """
    ローカルLLM（Qwen3）を使用したニュース要約機能
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.llm_config = self.config["data_sources"].get("local_llm", {})
        self.enabled = self.llm_config.get("enabled", False)
        self.ollama_url = self.llm_config.get("ollama_url", "http://localhost:11434")
        self.model_name = self.llm_config.get("model_name", "qwen3:8b")
        self.thinking_mode = self.llm_config.get("thinking_mode", False)
        
        # 接続テスト
        self.available = self._test_ollama_connection()
    
    def _test_ollama_connection(self) -> bool:
        """
        Ollamaサーバーとの接続をテスト
        
        Returns:
            bool: 接続成功の場合True
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                # 指定されたモデルが利用可能かチェック
                model_names = [model['name'] for model in models]
                return any(self.model_name in name for name in model_names)
            return False
        except Exception as e:
            print(f"Ollama接続テストエラー: {e}")
            return False
    
    def generate_summary_japanese(self, title: str, description: str, url: str = "") -> Optional[str]:
        """
        英語のニュース記事から日本語要約を生成
        
        Args:
            title (str): 記事タイトル（英語）
            description (str): 記事説明（英語）
            url (str): 記事URL（オプション）
        
        Returns:
            Optional[str]: 日本語要約（失敗時はNone）
        """
        if not self.enabled or not self.available:
            return self._fallback_summary(title, description)
        
        try:
            return self._summarize_with_qwen3(title, description)
        except Exception as e:
            print(f"Qwen3要約エラー: {e}")
            return self._fallback_summary(title, description)
    
    def _summarize_with_qwen3(self, title: str, description: str) -> Optional[str]:
        """
        Qwen3を使用して日本語要約を生成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            Optional[str]: 日本語要約
        """
        # 非thinking modeを強制し、直接的な日本語要約を生成
        # Qwen3のchat templateを使用してthinking modeを回避
        prompt = f"""<|user|>
以下の英語のAI業界ニュースを読んで、重要なポイントを日本語で50文字以内で要約してください。

タイトル: {title}
内容: {description}

日本語要約を簡潔に作成してください。
<|assistant|>
"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 30,
                "num_predict": 100,
                "stop": ["<|user|>", "<|assistant|>", "\n\n"],
                "repeat_penalty": 1.1,
                "seed": 42  # 一貫性のため固定シード
            }
        }
        
        try:
            print(f"🤖 Qwen3で要約生成中: {title[:30]}...")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=40
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_summary = result.get('response', '').strip()
                
                print(f"📝 生成された要約（生）: {raw_summary}")
                
                # thinkingコンテンツの完全除去
                if '<think>' in raw_summary:
                    if '</think>' in raw_summary:
                        # thinking部分後の内容を取得
                        parts = raw_summary.split('</think>')
                        raw_summary = parts[-1].strip()
                    else:
                        # thinking途中の場合はより強制的なアプローチ
                        print("⚠️ Thinking mode detected, trying direct approach...")
                        return self._direct_translation_approach(title, description)
                
                # クリーンアップ
                summary = self._clean_summary(raw_summary)
                
                # 品質チェック
                if self._is_valid_summary(summary, title, description):
                    print(f"✅ 最終要約: {summary}")
                    return summary
                else:
                    print("⚠️ Summary quality check failed, trying direct approach...")
                    return self._direct_translation_approach(title, description)
                    
            else:
                print(f"❌ Ollama APIエラー: {response.status_code}")
                return self._direct_translation_approach(title, description)
                
        except Exception as e:
            print(f"❌ Qwen3 API呼び出しエラー: {e}")
            return self._direct_translation_approach(title, description)
    
    def _direct_translation_approach(self, title: str, description: str) -> Optional[str]:
        """
        より直接的なアプローチで翻訳・要約
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            Optional[str]: 日本語要約
        """
        # 最もシンプルなプロンプトで直接的に要求
        text_to_summarize = f"{title}. {description}"
        
        prompt = f"""Translate to Japanese and summarize in 50 characters:

{text_to_summarize}

Japanese:"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 80,
                "stop": ["\n", "English:", "Translate:"],
                "repeat_penalty": 1.2
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                # thinking contentがある場合はフォールバック
                if '<think>' in summary:
                    print("⚠️ Still in thinking mode, using improved fallback...")
                    return self._improved_fallback_summary(title, description)
                
                summary = self._clean_summary(summary)
                
                if self._is_valid_summary(summary, title, description):
                    return summary
                else:
                    return self._improved_fallback_summary(title, description)
            else:
                return self._improved_fallback_summary(title, description)
                
        except Exception:
            return self._improved_fallback_summary(title, description)
    
    def _is_valid_summary(self, summary: str, title: str, description: str) -> bool:
        """
        要約の品質をチェック
        
        Args:
            summary (str): 生成された要約
            title (str): 元のタイトル
            description (str): 元の説明
        
        Returns:
            bool: 有効な要約かどうか
        """
        if not summary or len(summary) < 10:
            return False
        
        # 日本語が含まれているかチェック
        import re
        has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', summary))
        
        # 元のタイトルをそのまま使っていないかチェック
        title_words = title.lower().split()[:3]  # 最初の3単語
        summary_lower = summary.lower()
        
        similarity_count = sum(1 for word in title_words if word in summary_lower)
        too_similar = len(title_words) > 0 and similarity_count >= len(title_words)
        
        return has_japanese and not too_similar
    
    def _improved_fallback_summary(self, title: str, description: str) -> str:
        """
        改善されたフォールバック要約
        descriptionの内容を分析してより意味のある要約を作成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            str: 日本語要約
        """
        # 重要なキーワードマッピング（英語→日本語）
        keyword_mapping = {
            "announced": "発表",
            "announces": "発表",
            "launched": "リリース",
            "launches": "リリース",
            "released": "リリース",
            "releases": "リリース",
            "updated": "更新",
            "updates": "更新",
            "enhanced": "強化",
            "improved": "改善",
            "new": "新",
            "AI": "AI",
            "artificial intelligence": "AI",
            "model": "モデル",
            "technology": "技術",
            "OpenAI": "OpenAI",
            "Google": "Google",
            "Meta": "Meta",
            "funding": "資金調達",
            "investment": "投資",
            "partnership": "提携",
            "acquisition": "買収",
            "video": "動画",
            "analysis": "分析",
            "capabilities": "機能",
            "performance": "性能",
            "breakthrough": "ブレイクスルー"
        }
        
        # descriptionまたはtitleから重要な情報を抽出
        content = description if description and len(description) > 20 else title
        
        # キーワードベースの翻訳・要約
        summary_parts = []
        
        # 会社名を特定
        companies = ["OpenAI", "Google", "Meta", "Microsoft", "Amazon", "Apple", "Anthropic", "Gemini"]
        for company in companies:
            if company.lower() in content.lower():
                summary_parts.append(company)
                break
        
        # アクションを特定
        for eng_word, jp_word in keyword_mapping.items():
            if eng_word.lower() in content.lower():
                summary_parts.append(jp_word)
                break
        
        # 技術・製品を特定
        tech_terms = ["GPT", "model", "AI", "video", "analysis", "tool", "platform", "API"]
        for term in tech_terms:
            if term.lower() in content.lower():
                if term == "model":
                    summary_parts.append("AIモデル")
                elif term == "video":
                    summary_parts.append("動画")
                elif term == "analysis":
                    summary_parts.append("分析")
                else:
                    summary_parts.append(term)
                break
        
        # 要約を構築
        if summary_parts:
            summary = "".join(summary_parts[:3]) + "関連ニュース"
        else:
            # 最低限の情報
            first_sentence = content.split('.')[0] if '.' in content else content
            summary = f"AI業界: {first_sentence[:20]}..."
        
        # 50文字制限
        if len(summary) > 50:
            summary = summary[:47] + "..."
        
        return summary
    
    def _clean_summary(self, summary: str) -> str:
        """
        要約テキストをクリーンアップ
        
        Args:
            summary (str): 生の要約テキスト
        
        Returns:
            str: クリーンアップされた要約
        """
        # 不要な前置きや記号を除去
        prefixes_to_remove = [
            "日本語要約:",
            "要約:",
            "まとめ:",
            "概要:",
            "Japanese Summary:",
            "Japanese:",
            "Summary:",
            "この記事は",
            "このニュースは",
            "**",
            "##",
            "- "
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 改行を除去
        summary = summary.replace('\n', ' ').replace('\r', ' ')
        
        # 複数スペースを単一スペースに
        import re
        summary = re.sub(r'\s+', ' ', summary)
        
        # 50文字制限
        if len(summary) > 50:
            summary = summary[:47] + "..."
        
        return summary.strip()
    
    def _fallback_summary(self, title: str, description: str) -> str:
        """
        フォールバック要約（LLMが利用できない場合）
        改善版：descriptionの内容も考慮
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            str: 簡易要約
        """
        # descriptionから重要なキーワードを抽出
        important_keywords = [
            "AI", "artificial intelligence", "machine learning", "ChatGPT", "GPT",
            "model", "technology", "startup", "funding", "release", "launch",
            "announce", "update", "improve", "enhance", "breakthrough"
        ]
        
        content = description if description else title
        
        # 重要なキーワードを含む文を優先
        sentences = content.split('.')
        best_sentence = ""
        
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in important_keywords):
                best_sentence = sentence.strip()
                break
        
        if not best_sentence:
            best_sentence = sentences[0] if sentences else title
        
        # 日本語プレフィックスを追加
        summary = f"AI業界: {best_sentence}"
        
        if len(summary) > 47:
            summary = summary[:47] + "..."
        
        return summary
    
    def process_news_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        ニュース記事リストを処理して日本語要約を追加
        
        Args:
            articles (List[Dict]): ニュース記事リスト
        
        Returns:
            List[Dict]: 日本語要約付きニュース記事リスト
        """
        processed_articles = []
        
        for i, article in enumerate(articles):
            processed_article = article.copy()
            
            print(f"📝 記事 {i+1}/{len(articles)} を要約中...")
            
            # 日本語要約を生成
            summary_jp = self.generate_summary_japanese(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", "")
            )
            
            processed_article["summary_jp"] = summary_jp
            processed_articles.append(processed_article)
            
            # API呼び出し間隔を調整（Ollamaサーバーの負荷軽減）
            if i < len(articles) - 1:
                time.sleep(1)
        
        return processed_articles
    
    def get_status(self) -> Dict[str, Any]:
        """
        ローカルLLM機能の状態を取得
        
        Returns:
            Dict: 状態情報
        """
        return {
            "enabled": self.enabled,
            "model_name": self.model_name,
            "ollama_available": self.available,
            "ollama_url": self.ollama_url,
            "thinking_mode": self.thinking_mode,
            "fallback_enabled": True
        }


if __name__ == "__main__":
    # テスト実行
    summarizer = LocalLLMSummarizer()
    
    print("=== ローカルLLM（Qwen3）要約機能テスト ===")
    status = summarizer.get_status()
    print(f"状態: {status}")
    
    # サンプル記事でテスト
    sample_articles = [
        {
            "title": "OpenAI announces new GPT-5 model with enhanced reasoning capabilities",
            "description": "The latest AI model from OpenAI shows significant improvements in logical reasoning, mathematics, and code generation, outperforming previous versions in benchmark tests.",
            "url": "https://example.com/openai-gpt5",
            "keyword": "OpenAI"
        },
        {
            "title": "Google's Gemini AI now supports video analysis and understanding",
            "description": "Google has updated its Gemini AI model to include advanced video processing capabilities, allowing users to analyze and interact with video content in natural language.",
            "url": "https://example.com/gemini-video",
            "keyword": "Gemini"
        }
    ]
    
    if summarizer.enabled:
        print("\n=== 要約テスト開始 ===")
        processed = summarizer.process_news_articles(sample_articles)
        
        print("\n=== 処理結果 ===")
        for article in processed:
            print(f"📰 タイトル: {article['title'][:50]}...")
            print(f"🇯🇵 日本語要約: {article.get('summary_jp', '未生成')}")
            print("---")
    else:
        print("⚠️  ローカルLLM機能が無効またはOllamaが利用できません。")
        print("Ollamaをインストールし、以下を実行してください:")
        print("  ollama pull qwen3:8b")
        print("  ollama serve") 