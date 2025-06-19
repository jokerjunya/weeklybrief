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
        # シンプルなプロンプトでthinking modeを回避
        prompt = f"""以下の英語ニュースを日本語で50文字以内で要約してください。

Title: {title}
Content: {description}

Japanese Summary:"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # より低い温度で一貫性向上
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 80,  # 短い制限で迅速応答
                "stop": ["\n", "Summary:", "要約:", "Title:", "Content:"]
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30  # タイムアウトを短くしてテスト
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                # Thinking contentを完全に除去
                if '<think>' in summary:
                    if '</think>' in summary:
                        summary = summary.split('</think>')[-1].strip()
                    else:
                        # Thinking中で止まった場合はフォールバック
                        return self._fallback_summary(title, description)
                
                # 不要な前置きを除去
                summary = self._clean_summary(summary)
                
                return summary if summary else None
            else:
                print(f"Ollama APIエラー: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Qwen3 API呼び出しエラー: {e}")
            return None
    
    def _clean_summary(self, summary: str) -> str:
        """
        要約テキストをクリーンアップ
        
        Args:
            summary (str): 生の要約テキスト
        
        Returns:
            str: クリーンアップされた要約
        """
        # 不要な前置きを除去
        prefixes_to_remove = [
            "日本語要約:",
            "要約:",
            "まとめ:",
            "概要:",
            "この記事は",
            "このニュースは"
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 50文字制限
        if len(summary) > 50:
            summary = summary[:47] + "..."
        
        return summary
    
    def _fallback_summary(self, title: str, description: str) -> str:
        """
        フォールバック要約（LLMが利用できない場合）
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            str: 簡易要約
        """
        # 簡単な英語タイトルの省略版を作成
        content = f"{title}"
        if len(content) > 47:
            content = content[:47] + "..."
        return f"AI業界: {content}"
    
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