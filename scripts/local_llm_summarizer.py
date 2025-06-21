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

# Ollama Python APIのインポート（フォールバック対応）
try:
    import ollama
    OLLAMA_CLIENT_AVAILABLE = True
except ImportError:
    OLLAMA_CLIENT_AVAILABLE = False
    print("⚠️ Ollama Python client not found. Install with: pip install ollama")


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
        
        # Ollama Pythonクライアントの初期化
        self.ollama_client = None
        if OLLAMA_CLIENT_AVAILABLE:
            try:
                self.ollama_client = ollama.Client(host=self.ollama_url)
                print("✅ Ollama Python client initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Ollama client: {e}")
                self.ollama_client = None
        
        # 接続テスト
        self.available = self._test_ollama_connection()
    
    def _test_ollama_connection(self) -> bool:
        """
        Ollamaサーバーとの接続をテスト
        
        Returns:
            bool: 接続成功の場合True
        """
        try:
            if self.ollama_client:
                # Python clientでテスト
                models = self.ollama_client.list()
                model_names = [model['name'] for model in models['models']]
                return any(self.model_name in name for name in model_names)
            else:
                # フォールバック：直接APIテスト
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [model['name'] for model in models]
                    return any(self.model_name in name for name in model_names)
            return False
        except Exception as e:
            print(f"Ollama接続テストエラー: {e}")
            return False
    
    def generate_summary_japanese(self, title: str, description: str, url: str = "", content: str = "") -> Optional[str]:
        """
        英語のニュース記事から日本語要約を生成
        
        Args:
            title (str): 記事タイトル（英語）
            description (str): 記事説明（英語）
            url (str): 記事URL（オプション）
            content (str): 記事本文（英語、オプション）
        
        Returns:
            Optional[str]: 日本語要約（失敗時はNone）
        """
        if not self.enabled or not self.available:
            return self._create_intelligent_fallback(title, description, content)
        
        try:
            return self._summarize_with_qwen3(title, description, content)
        except Exception as e:
            print(f"Qwen3要約エラー: {e}")
            return self._create_intelligent_fallback(title, description, content)
    
    def _summarize_with_qwen3(self, title: str, description: str, content: str = "") -> Optional[str]:
        """
        Qwen3を使用して日本語要約を生成（thinking mode無効化）
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
            content (str): 記事本文（オプション）
        
        Returns:
            Optional[str]: 日本語要約
        """
        # より多くの情報を活用して要約の質を向上
        full_text = f"{title}. {description or ''} {content or ''}".strip()
        
        # 最新のOllama Python APIを使用してthinking modeを完全無効化
        if self.ollama_client:
            return self._summarize_with_ollama_client(full_text, title)
        else:
            # フォールバック：従来のrequests方式
            return self._summarize_with_requests_fallback(full_text, title, description, content)
    
    def _summarize_with_ollama_client(self, full_text: str, title: str) -> Optional[str]:
        """
        Ollama Python clientを使用した要約生成（thinking mode完全無効化）
        
        Args:
            full_text (str): 全記事テキスト
            title (str): 記事タイトル
        
        Returns:
            Optional[str]: 日本語要約
        """
        try:
            print(f"🤖 Qwen3（thinking OFF）で要約生成中: {title[:30]}...")
            
            # thinking mode完全無効化のプロンプト
            prompt = f"""You are a professional Japanese business news summarizer.

Article: {full_text[:800]}

Task: Create a concise Japanese summary (max 50 characters) that includes:
1. What happened (具体的な出来事)
2. Who is involved (関係者・企業名) 
3. Key impact (重要な影響)

Requirements: 
- Output ONLY the Japanese summary
- No thinking, no explanation, no analysis
- Direct answer only

Japanese summary:"""
            
            # Ollama Python clientでthinking mode無効化
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                stream=False,
                think=False,  # 🔑 Key: thinking mode完全無効化
                options={
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'top_k': 40,
                    'num_predict': 80,
                    'repeat_penalty': 1.15,
                    'seed': 42
                }
            )
            
            if response and 'message' in response:
                raw_summary = response['message']['content'].strip()
                print(f"📝 生成された要約（Ollama Client）: {raw_summary}")
                
                # クリーンアップと品質チェック
                summary = self._clean_summary(raw_summary)
                
                if self._is_high_quality_summary(summary, title, ""):
                    print(f"✅ 高品質要約（thinking無効化）: {summary}")
                    return summary
                else:
                    print("⚠️ 品質不足、インテリジェントフォールバックを使用...")
                    return self._create_intelligent_fallback(title, "", "")
            else:
                print("❌ Ollama client response invalid")
                return self._create_intelligent_fallback(title, "", "")
                
        except Exception as e:
            print(f"❌ Ollama client error: {e}")
            return self._create_intelligent_fallback(title, "", "")
    
    def _summarize_with_requests_fallback(self, full_text: str, title: str, description: str, content: str) -> Optional[str]:
        """
        従来のrequests方式でのフォールバック要約生成
        
        Args:
            full_text (str): 全記事テキスト
            title (str): 記事タイトル
            description (str): 記事説明
            content (str): 記事本文
        
        Returns:
            Optional[str]: 日本語要約
        """
        print(f"🤖 Qwen3（requests fallback）で要約生成中: {title[:30]}...")
        
        # プロンプトに/no_thinkを追加してthinking mode抑制を試行
        prompt = f"""/no_think

You are a professional Japanese business news summarizer.

Article: {full_text[:800]}

Task: Create a concise Japanese summary (max 50 characters).
Output ONLY the Japanese summary, no thinking, no explanation.

Japanese summary:

/no_think"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 80,
                "stop": ["<|user|>", "<|assistant|>", "\n\n", "English:", "Article:", "<think>"],
                "repeat_penalty": 1.15,
                "seed": 42
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=40
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_summary = result.get('response', '').strip()
                print(f"📝 生成された要約（requests）: {raw_summary}")
                
                # thinking content detection
                if '<think>' in raw_summary or 'thinking' in raw_summary.lower():
                    print("⚠️ Thinking mode detected in requests fallback, using intelligent fallback...")
                    return self._create_intelligent_fallback(title, description, content)
                
                summary = self._clean_summary(raw_summary)
                
                if self._is_high_quality_summary(summary, title, description):
                    print(f"✅ 要約（requests fallback）: {summary}")
                    return summary
                else:
                    print("⚠️ 品質不足、インテリジェントフォールバックを使用...")
                    return self._create_intelligent_fallback(title, description, content)
                    
            else:
                print(f"❌ Requests API error: {response.status_code}")
                return self._create_intelligent_fallback(title, description, content)
                
        except Exception as e:
            print(f"❌ Requests API error: {e}")
            return self._create_intelligent_fallback(title, description, content)
    
    def _create_intelligent_fallback(self, title: str, description: str, content: str = "") -> str:
        """
        インテリジェントなフォールバック要約を生成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
            content (str): 記事本文
        
        Returns:
            str: 改善されたフォールバック要約
        """
        # 全テキストを結合
        full_text = f"{title} {description or ''} {content or ''}".lower()
        
        # キーワードベースの分析
        summary_parts = []
        
        # 企業・サービス名の抽出
        companies = self._extract_companies_enhanced(full_text)
        if companies:
            summary_parts.append(companies[0])
        
        # アクション・イベントの抽出
        actions = self._extract_key_actions(full_text)
        if actions:
            summary_parts.append(actions[0])
        
        # 金額・数値の抽出
        amounts = self._extract_amounts(full_text)
        if amounts:
            summary_parts.append(amounts[0])
        
        # 要約を構築
        if summary_parts:
            base_summary = "、".join(summary_parts)
        else:
            # 最低限の情報からでも意味のある要約を作成
            base_summary = self._extract_core_meaning(title, description)
        
        # 50文字以内に調整
        if len(base_summary) > 50:
            base_summary = base_summary[:47] + "..."
        
        return base_summary

    def _extract_companies_enhanced(self, text: str) -> List[str]:
        """
        企業名を抽出（強化版）
        """
        companies = []
        text_lower = text.lower()
        
        # より詳細な企業・サービス名マッピング
        company_patterns = [
            ('openai', 'OpenAI'),
            ('google', 'Google'),
            ('gboard', 'Google'),
            ('microsoft', 'Microsoft'),
            ('anthropic', 'Anthropic'),
            ('meta', 'Meta'),
            ('nvidia', 'NVIDIA'),
            ('apple', 'Apple'),
            ('amazon', 'Amazon'),
            ('tesla', 'Tesla'),
            ('netflix', 'Netflix'),
            ('polar', 'Polar'),
            ('polyhedra', 'Polyhedra'),
            ('deepgram', 'Deepgram'),
            ('gemini', 'Google Gemini'),
            ('gpt', 'OpenAI'),
            ('chatgpt', 'OpenAI'),
            ('claude', 'Anthropic'),
            ('bard', 'Google'),
            ('pypi', 'Python'),
            ('python', 'Python')
        ]
        
        for pattern, company_name in company_patterns:
            if pattern in text_lower:
                companies.append(company_name)
                break
        
        # 記事タイトルから具体的な企業を抽出
        if not companies:
            if 'ai industry' in text_lower:
                companies.append('AI業界')
            elif 'ecommerce' in text_lower:
                companies.append('Eコマース')
            elif 'ad industry' in text_lower:
                companies.append('広告業界')
            else:
                companies.append('テック企業')
        
        return companies

    def _extract_key_actions(self, text: str) -> List[str]:
        """
        主要なアクション・イベントを抽出（改善版）
        """
        actions = []
        text_lower = text.lower()
        
        # より具体的なパターンマッチング
        if 'raise' in text_lower and ('million' in text_lower or 'billion' in text_lower):
            actions.append('資金調達')
        elif 'replace' in text_lower and 'human' in text_lower:
            actions.append('AI人材置き換え')
        elif 'gboard' in text_lower and 'change' in text_lower:
            actions.append('Gboard機能更新')
        elif 'ecommerce' in text_lower and 'tool' in text_lower:
            actions.append('Eコマースツール発表')
        elif 'environment' in text_lower and 'impact' in text_lower:
            actions.append('AI環境負荷対策')
        elif 'voice' in text_lower and 'chat' in text_lower:
            actions.append('音声チャット機能')
        elif 'podcast' in text_lower or 'interview' in text_lower:
            actions.append('業界インタビュー')
        elif 'cannes' in text_lower and 'ad' in text_lower:
            actions.append('カンヌ広告業界動向')
        elif 'pandas' in text_lower and 'collective' in text_lower:
            actions.append('動物学用語話題')
        elif 'netflix' in text_lower and 'review' in text_lower:
            actions.append('Netflix新作レビュー')
        elif 'mindhunter' in text_lower:
            actions.append('俳優インタビュー')
        elif 'school bus' in text_lower:
            actions.append('社会問題報道')
        elif 'pypi' in text_lower or 'python' in text_lower:
            actions.append('Pythonライブラリ公開')
        elif 'ai industry' in text_lower and 'veteran' in text_lower:
            actions.append('AI業界専門家講演')
        else:
            # デフォルトアクション
            if 'launch' in text_lower or 'release' in text_lower:
                actions.append('新製品発表')
            elif 'update' in text_lower or 'improve' in text_lower:
                actions.append('機能改善')
            elif 'announce' in text_lower:
                actions.append('重要発表')
            else:
                actions.append('業界動向')
        
        return actions

    def _extract_amounts(self, text: str) -> List[str]:
        """
        金額・数値を抽出
        """
        amounts = []
        
        # 金額パターン
        import re
        money_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*million',
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*billion',
            r'(\d+(?:,\d{3})*)\s*million',
            r'(\d+(?:,\d{3})*)\s*billion'
        ]
        
        for pattern in money_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                amount = matches[0]
                if 'million' in text:
                    amounts.append(f"{amount}百万ドル")
                elif 'billion' in text:
                    amounts.append(f"{amount}億ドル")
                break
        
        return amounts

    def _extract_core_meaning(self, title: str, description: str) -> str:
        """
        タイトルと説明から核心的な意味を抽出
        """
        # タイトルから重要なキーワードを抽出
        title_lower = title.lower()
        
        # 重要なキーワードパターン
        keyword_map = {
            'ai': 'AI',
            'artificial intelligence': 'AI',
            'machine learning': '機械学習',
            'deep learning': '深層学習',
            'neural network': 'ニューラルネット',
            'chatbot': 'チャットボット',
            'voice': '音声技術',
            'automation': '自動化',
            'startup': 'スタートアップ',
            'funding': '資金調達',
            'investment': '投資',
            'technology': '技術',
            'innovation': 'イノベーション',
            'platform': 'プラットフォーム',
            'service': 'サービス',
            'tool': 'ツール',
            'model': 'モデル',
            'feature': '機能',
            'update': 'アップデート',
            'launch': 'ローンチ',
            'release': 'リリース'
        }
        
        found_keywords = []
        for eng, jp in keyword_map.items():
            if eng in title_lower:
                found_keywords.append(jp)
        
        if found_keywords:
            return f"{found_keywords[0]}関連の新展開"
        else:
            # 最後の手段：タイトルの最初の部分を使用
            title_parts = title.split()[:3]
            return f"{''.join(title_parts)[:20]}関連ニュース"

    def _is_high_quality_summary(self, summary: str, title: str, description: str) -> bool:
        """
        要約の品質をチェック（強化版）
        
        Args:
            summary (str): 生成された要約
            title (str): 元のタイトル
            description (str): 元の説明
        
        Returns:
            bool: 高品質の場合True
        """
        if not summary or len(summary.strip()) < 10:
            return False
        
        # 不適切なパターンをチェック
        bad_patterns = [
            'AI業界:',  # 古いパターン
            '...',  # 省略記号のみ
            'calls for',  # 英語の残存
            'industry veteran',  # 英語の残存
            '<think>',  # thinking mode
            'assistant',  # システムメッセージ
            'user',  # システムメッセージ
        ]
        
        for pattern in bad_patterns:
            if pattern in summary:
                return False
        
        # 日本語コンテンツの確認
        japanese_chars = sum(1 for char in summary if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF')
        if japanese_chars < len(summary) * 0.3:  # 30%以上が日本語である必要
            return False
        
        return True
    
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
    
    def _improved_fallback_summary(self, title: str, description: str, content: str = "") -> str:
        """
        改善されたフォールバック要約
        具体的な事実と結論が分かる要約を作成
        
        Args:
            title (str): 記事タイトル
            description (str): 記事説明
            content (str): 記事本文（オプション）
        
        Returns:
            str: 日本語要約
        """
        # 全文を結合してより多くの情報を活用
        full_content = f"{title}. {description or ''} {content or ''}".strip()
        
        # 具体的な事実を抽出するパターン分析
        summary = self._extract_key_facts(full_content)
        
        # 50文字制限
        if len(summary) > 50:
            summary = summary[:47] + "..."
        
        return summary
    
    def _extract_key_facts(self, content: str) -> str:
        """
        ニュース内容から具体的な事実と結論を抽出
        
        Args:
            content (str): ニュース全文
        
        Returns:
            str: 具体的な事実を含む日本語要約
        """
        content_lower = content.lower()
        
        # パターン1: 会社間の動き（買収、提携、競争等）
        if "meta" in content_lower and "openai" in content_lower:
            if "bonus" in content_lower or "million" in content_lower:
                return "Meta、OpenAI社員に巨額ボーナス提示で引き抜き"
            elif "compete" in content_lower or "competition" in content_lower:
                return "MetaとOpenAI、AI人材を巡り競争激化"
            else:
                return "MetaとOpenAI間で新たな動き"
        
        # パターン2: 新製品・機能発表
        if any(word in content_lower for word in ["announce", "launch", "release", "unveil"]):
            # OpenAI関連
            if "openai" in content_lower:
                if "gpt" in content_lower and ("5" in content or "new" in content_lower):
                    return "OpenAI、新型GPTモデルを発表"
                elif "pentagon" in content_lower or "defense" in content_lower:
                    return "OpenAI、米国防総省と契約締結"
                else:
                    return "OpenAI、新サービス・機能を発表"
            
            # Google/Gemini関連
            elif "gemini" in content_lower or "google" in content_lower:
                if "video" in content_lower:
                    return "Google Gemini、動画分析機能を追加"
                elif "update" in content_lower:
                    return "Google Gemini、機能強化版をリリース"
                else:
                    return "Google、AI新機能を発表"
            
            # その他企業
            elif "microsoft" in content_lower:
                return "Microsoft、AI関連新製品を発表"
            elif "amazon" in content_lower:
                return "Amazon、AI戦略を発表"
        
        # パターン3: 投資・資金調達
        if any(word in content_lower for word in ["funding", "investment", "raise", "million", "billion"]):
            if "startup" in content_lower:
                return "AI関連スタートアップ、大型資金調達"
            else:
                return "AI業界で大型投資案件が発生"
        
        # パターン4: 技術革新・ブレイクスルー
        if any(word in content_lower for word in ["breakthrough", "advancement", "improve", "enhance"]):
            if "reasoning" in content_lower or "logic" in content_lower:
                return "AI推論能力が大幅向上、新技術を開発"
            elif "performance" in content_lower:
                return "AI性能向上、処理速度が改善"
            else:
                return "AI技術で新たなブレイクスルー"
        
        # パターン5: 人事・組織変更
        if any(word in content_lower for word in ["hire", "employee", "ceo", "executive"]):
            return "AI企業で重要人事、組織体制を変更"
        
        # パターン6: 規制・政策
        if any(word in content_lower for word in ["regulation", "policy", "government", "law"]):
            return "AI規制・政策に関する重要動向"
        
        # パターン7: パートナーシップ・提携
        if any(word in content_lower for word in ["partnership", "collaborate", "team up"]):
            companies = self._extract_companies(content)
            if len(companies) >= 2:
                return f"{companies[0]}と{companies[1]}が提携"
            else:
                return "AI業界で新たな提携が発表"
        
        # パターン8: PyPI/GitHub等開発ツール
        if "pypi" in content_lower or "github" in content_lower:
            return "AI開発ツール、新ライブラリが公開"
        
        # デフォルト: タイトルから最重要情報を抽出
        return self._extract_from_title(content)
    
    def _extract_companies(self, content: str) -> List[str]:
        """
        文章から企業名を抽出
        
        Args:
            content (str): ニュース内容
        
        Returns:
            List[str]: 抽出された企業名リスト
        """
        companies = []
        company_names = [
            ("OpenAI", "OpenAI"), ("Google", "Google"), ("Meta", "Meta"), 
            ("Microsoft", "Microsoft"), ("Amazon", "Amazon"), ("Apple", "Apple"),
            ("Anthropic", "Anthropic"), ("Tesla", "Tesla"), ("xAI", "xAI")
        ]
        
        content_lower = content.lower()
        for english, japanese in company_names:
            if english.lower() in content_lower:
                companies.append(japanese)
        
        return companies
    
    def _extract_from_title(self, content: str) -> str:
        """
        タイトルから重要情報を抽出してより意味のある要約を作成
        
        Args:
            content (str): ニュース内容
        
        Returns:
            str: 意味のある要約
        """
        # タイトルの最初の部分（通常最も重要）を取得
        title = content.split('.')[0]
        
        # 企業名を特定
        companies = self._extract_companies(title)
        company = companies[0] if companies else "AI企業"
        
        # キーワードベースの動作抽出
        title_lower = title.lower()
        
        if "warn" in title_lower or "warning" in title_lower:
            return f"{company}CEO、AI関連で重要警告"
        elif "cut" in title_lower and "time" in title_lower:
            return f"{company}、AI活用で作業時間を大幅短縮"
        elif "hire" in title_lower or "talent" in title_lower:
            return f"{company}、AI人材確保に積極投資"
        elif "video" in title_lower and "analysis" in title_lower:
            return f"{company}、動画AI分析サービス開始"
        elif "chatbot" in title_lower:
            return f"{company}、チャットボット技術を向上"
        else:
            # 最後の手段：タイトル前半の重要部分を日本語化
            important_part = title[:30].strip()
            return f"AI業界: {important_part}..."
    
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
            
            # 日本語要約を生成（contentも含める）
            summary_jp = self.generate_summary_japanese(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", ""),
                content=article.get("content", "")
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

    def generate_weekly_news_summary(self, articles: List[Dict[str, Any]]) -> str:
        """
        週のニュース記事全体を日本語で300文字程度にサマライズ
        
        Args:
            articles (List[Dict]): 処理済みニュース記事リスト
        
        Returns:
            str: 週間ニュースサマリー（日本語、300文字程度）
        """
        if not articles:
            return "今週は注目すべきAI業界ニュースはありませんでした。"
        
        # 記事の主要情報を抽出
        titles = [article.get("title", "") for article in articles[:8]]  # 上位8件
        summaries = [article.get("summary_jp", "") for article in articles[:8]]
        
        if not self.enabled or not self.available:
            return self._create_fallback_weekly_summary(articles)
        
        try:
            return self._generate_weekly_summary_with_qwen3(titles, summaries)
        except Exception as e:
            print(f"週間サマリー生成エラー: {e}")
            return self._create_fallback_weekly_summary(articles)
    
    def _generate_weekly_summary_with_qwen3(self, titles: List[str], summaries: List[str]) -> str:
        """
        Qwen3を使用して週間ニュースサマリーを生成
        
        Args:
            titles (List[str]): 記事タイトルリスト
            summaries (List[str]): 個別記事要約リスト
        
        Returns:
            str: 週間サマリー
        """
        # 記事情報を整理
        article_info = []
        for i, (title, summary) in enumerate(zip(titles, summaries)):
            if title and summary:
                article_info.append(f"{i+1}. {summary}")
        
        articles_text = "\n".join(article_info[:6])  # 上位6件
        
        prompt = f"""<|user|>
以下は今週のAI業界ニュースです。全体的なトレンドと重要なポイントを日本語で300文字以内でまとめてください。

今週のニュース:
{articles_text}

業界全体の動向、主要企業の動き、注目すべき技術トレンドを含めて週間サマリーを作成してください。
<|assistant|>
"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
                "num_predict": 400,
                "stop": ["<|user|>", "<|assistant|>"],
                "repeat_penalty": 1.1
            }
        }
        
        try:
            print("🔍 週間ニュースサマリーを生成中...")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_summary = result.get('response', '').strip()
                
                # thinking modeのクリーンアップ
                if '<think>' in raw_summary:
                    if '</think>' in raw_summary:
                        raw_summary = raw_summary.split('</think>')[-1].strip()
                    else:
                        return self._create_fallback_weekly_summary_from_summaries(summaries)
                
                # サマリーのクリーンアップ
                summary = self._clean_weekly_summary(raw_summary)
                
                # 品質チェック
                if len(summary) > 50 and any(char in summary for char in 'あいうえおかきくけこ'):
                    return summary
                else:
                    return self._create_fallback_weekly_summary_from_summaries(summaries)
            else:
                return self._create_fallback_weekly_summary_from_summaries(summaries)
                
        except Exception as e:
            print(f"週間サマリー生成エラー: {e}")
            return self._create_fallback_weekly_summary_from_summaries(summaries)
    
    def _create_fallback_weekly_summary(self, articles: List[Dict[str, Any]]) -> str:
        """
        フォールバック週間サマリー作成
        
        Args:
            articles (List[Dict]): ニュース記事リスト
        
        Returns:
            str: 週間サマリー
        """
        summaries = [article.get("summary_jp", "") for article in articles if article.get("summary_jp")]
        return self._create_fallback_weekly_summary_from_summaries(summaries)
    
    def _create_fallback_weekly_summary_from_summaries(self, summaries: List[str]) -> str:
        """
        個別要約から週間サマリーを構築
        
        Args:
            summaries (List[str]): 個別記事要約リスト
        
        Returns:
            str: 週間サマリー
        """
        if not summaries:
            return "今週は注目すべきAI業界ニュースはありませんでした。"
        
        # 主要トピックを分析
        topics = {
            "企業競争": 0,
            "技術発表": 0,
            "投資・資金調達": 0,
            "人事・組織": 0,
            "製品リリース": 0,
            "政府・規制": 0
        }
        
        key_companies = set()
        
        for summary in summaries[:8]:
            summary_lower = summary.lower()
            
            # トピック分析
            if any(word in summary for word in ["引き抜き", "競争", "ボーナス"]):
                topics["企業競争"] += 1
            if any(word in summary for word in ["発表", "リリース", "開始"]):
                topics["技術発表"] += 1
            if any(word in summary for word in ["投資", "資金調達", "大型"]):
                topics["投資・資金調達"] += 1
            if any(word in summary for word in ["人事", "組織", "CEO"]):
                topics["人事・組織"] += 1
            if any(word in summary for word in ["サービス", "機能", "動画"]):
                topics["製品リリース"] += 1
            if any(word in summary for word in ["政府", "規制", "政策"]):
                topics["政府・規制"] += 1
            
            # 企業名抽出
            for company in ["OpenAI", "Meta", "Google", "Microsoft", "Amazon", "Apple"]:
                if company in summary:
                    key_companies.add(company)
        
        # 主要トピックを特定
        main_topic = max(topics.items(), key=lambda x: x[1])
        
        # サマリー構築
        companies_str = "、".join(list(key_companies)[:3]) if key_companies else "AI関連企業"
        
        if main_topic[1] > 0:
            if main_topic[0] == "企業競争":
                summary_text = f"今週のAI業界では{companies_str}を中心とした人材獲得競争が激化。"
            elif main_topic[0] == "技術発表":
                summary_text = f"今週は{companies_str}による新技術・サービス発表が相次ぎ、AI機能の実用化が加速。"
            elif main_topic[0] == "投資・資金調達":
                summary_text = f"AI業界で大型投資案件が活発化。{companies_str}関連の資金調達ニュースが目立つ。"
            elif main_topic[0] == "製品リリース":
                summary_text = f"{companies_str}が新製品・機能を相次いで発表。特に動画AI分析などの実用的サービスが注目。"
            else:
                summary_text = f"今週のAI業界では{companies_str}を中心とした動きが活発化。"
        else:
            summary_text = f"今週のAI業界では{companies_str}による様々な取り組みが報告され、"
        
        # 具体的な動向を追加
        specific_trends = []
        for summary in summaries[:3]:
            if len(summary) > 10 and summary not in summary_text:
                specific_trends.append(summary.replace("AI業界: ", "").replace("...", ""))
        
        if specific_trends:
            summary_text += f" 主な動向として{specific_trends[0]}など、"
            if len(specific_trends) > 1:
                summary_text += f"{specific_trends[1]}といった展開も見られる。"
            else:
                summary_text += "業界全体の変化が継続している。"
        else:
            summary_text += " 業界全体でAI技術の実用化と競争が加速している状況が続いている。"
        
        # 300文字制限
        if len(summary_text) > 300:
            summary_text = summary_text[:297] + "..."
        
        return summary_text
    
    def _clean_weekly_summary(self, summary: str) -> str:
        """
        週間サマリーをクリーンアップ
        
        Args:
            summary (str): 生の週間サマリー
        
        Returns:
            str: クリーンアップされた週間サマリー
        """
        # 不要な前置きを除去
        prefixes_to_remove = [
            "今週のAI業界ニュースをまとめると、",
            "週間サマリー:",
            "まとめ:",
            "概要:",
            "今週は、"
        ]
        
        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        # 改行を除去
        summary = summary.replace('\n', ' ').replace('\r', ' ')
        
        # 複数スペースを単一スペースに
        import re
        summary = re.sub(r'\s+', ' ', summary)
        
        # 300文字制限
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary.strip()


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