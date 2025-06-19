#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュース記事の日本語要約機能

このモジュールは英語のニュース記事を取得し、
AIを使用して要約・日本語翻訳を行います。
"""

import json
import requests
import openai
from typing import Dict, List, Optional, Any
from google.cloud import translate_v2 as translate


class NewsSummarizer:
    """
    ニュース記事のAI要約・翻訳機能を提供するクラス
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.ai_config = self.config["data_sources"]["ai_summarization"]
        self.enabled = self.ai_config.get("enabled", False)
        self.provider = self.ai_config.get("provider", "openai")
        
        # OpenAI設定
        if self.provider == "openai":
            openai_config = self.ai_config["openai"]
            if openai_config["api_key"] != "OPENAI_API_KEY_TO_BE_PROVIDED":
                openai.api_key = openai_config["api_key"]
                self.openai_client = openai.OpenAI(api_key=openai_config["api_key"])
            else:
                self.openai_client = None
        
        # Google Translate設定
        self.google_translate_client = None
        translate_config = self.ai_config["google_translate"]
        if translate_config["api_key"] != "GOOGLE_TRANSLATE_API_KEY_TO_BE_PROVIDED":
            self.google_translate_client = translate.Client()
    
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
        if not self.enabled:
            return None
        
        try:
            if self.provider == "openai" and self.openai_client:
                return self._summarize_with_openai(title, description)
            elif self.google_translate_client:
                return self._translate_with_google(title, description)
            else:
                # APIが利用できない場合、フォールバックを使用
                if self.ai_config.get("fallback_enabled", True):
                    return self._fallback_summary(title, description)
                return None
        except Exception as e:
            print(f"要約生成エラー: {e}")
            if self.ai_config.get("fallback_enabled", True):
                return self._fallback_summary(title, description)
            return None
    
    def _summarize_with_openai(self, title: str, description: str) -> Optional[str]:
        """
        OpenAI GPTを使用して日本語要約を生成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            Optional[str]: 日本語要約
        """
        try:
            openai_config = self.ai_config["openai"]
            
            prompt = f"""以下の英語ニュース記事を日本語で簡潔に要約してください。
重要なポイントを含み、50文字以内でまとめてください。

タイトル: {title}
内容: {description}

日本語要約:"""
            
            response = self.openai_client.chat.completions.create(
                model=openai_config["model"],
                messages=[
                    {"role": "system", "content": "あなたは優秀な記者です。英語ニュースを正確かつ簡潔に日本語で要約します。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=openai_config["max_tokens"],
                temperature=openai_config["temperature"]
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            print(f"OpenAI要約エラー: {e}")
            return None
    
    def _translate_with_google(self, title: str, description: str) -> Optional[str]:
        """
        Google Translateを使用して翻訳・要約を生成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            Optional[str]: 日本語翻訳
        """
        try:
            # 簡単な要約作成（最初の100文字程度）
            content = f"{title}. {description}"
            if len(content) > 100:
                content = content[:100] + "..."
            
            # Google Translateで翻訳
            result = self.google_translate_client.translate(
                content,
                target_language='ja',
                source_language='en'
            )
            
            return result['translatedText']
        
        except Exception as e:
            print(f"Google Translate翻訳エラー: {e}")
            return None
    
    def _fallback_summary(self, title: str, description: str) -> str:
        """
        フォールバック要約（APIが利用できない場合）
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
        
        Returns:
            str: 簡易要約
        """
        # 簡単な英語タイトルの省略版を作成
        content = f"{title}"
        if len(content) > 50:
            content = content[:50] + "..."
        return f"AI企業関連ニュース: {content}"
    
    def process_news_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        ニュース記事リストを処理して日本語要約を追加
        
        Args:
            articles (List[Dict]): ニュース記事リスト
        
        Returns:
            List[Dict]: 日本語要約付きニュース記事リスト
        """
        processed_articles = []
        
        for article in articles:
            processed_article = article.copy()
            
            # 日本語要約を生成
            summary_jp = self.generate_summary_japanese(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", "")
            )
            
            processed_article["summary_jp"] = summary_jp
            processed_articles.append(processed_article)
        
        return processed_articles
    
    def get_status(self) -> Dict[str, Any]:
        """
        要約機能の状態を取得
        
        Returns:
            Dict: 状態情報
        """
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "openai_available": self.openai_client is not None,
            "google_translate_available": self.google_translate_client is not None,
            "fallback_enabled": self.ai_config.get("fallback_enabled", True)
        }


if __name__ == "__main__":
    # テスト実行
    summarizer = NewsSummarizer()
    
    print("=== ニュース要約機能テスト ===")
    print(f"状態: {summarizer.get_status()}")
    
    # サンプル記事でテスト
    sample_articles = [
        {
            "title": "OpenAI announces new GPT-4.5 model with enhanced capabilities",
            "description": "The latest AI model from OpenAI shows significant improvements in reasoning and code generation, setting new benchmarks in artificial intelligence.",
            "url": "https://example.com/openai-news",
            "keyword": "OpenAI"
        }
    ]
    
    if summarizer.enabled:
        processed = summarizer.process_news_articles(sample_articles)
        print("\n=== 処理結果 ===")
        for article in processed:
            print(f"タイトル: {article['title']}")
            print(f"日本語要約: {article.get('summary_jp', '未生成')}")
            print("---")
    else:
        print("要約機能が無効化されています。設定ファイルでenabledをtrueに変更してください。") 