#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDファイルからニュースデータを抽出してJSON化するスクリプト

このスクリプトは:
1. reports/ディレクトリ内の最新のMDファイルを検索
2. ニュース記事データを抽出・パース
3. web/news-data.jsonファイルとして出力
4. Webページから読み込み可能なJSON形式で保存

使用方法:
    python scripts/generate-news-json.py
"""

import os
import re
import json
import glob
from datetime import datetime
from typing import Dict, List, Any


def find_latest_report() -> str:
    """最新のレポートファイルを検索"""
    reports_dir = "reports"
    pattern = os.path.join(reports_dir, "週次レポート_テスト_*.md")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError("レポートファイルが見つかりません")
    
    # ファイル名の日時部分でソート
    files.sort(reverse=True)
    return files[0]


def parse_news_section(content: str) -> Dict[str, Any]:
    """MDファイルからニュースセクションを抽出・パース"""
    
    # ニュースサマリーを抽出
    summary_match = re.search(r'### 📋 今週のサマリー\n\n(.+?)\n\n---', content, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""
    
    # カテゴリ別ニュースを抽出
    categories = {
        'openai': 'OpenAI',
        'gemini': 'Gemini', 
        'lovable': 'Lovable',
        'perplexity': 'Perplexity',
        'grok': 'Grok',
        'anthropic': 'Anthropic',
        'other': 'その他'
    }
    
    news_data = []
    
    for category_key, category_name in categories.items():
        # カテゴリセクションを検索
        pattern = rf'### 🔍 {re.escape(category_name)} 関連\n\n(.*?)(?=### 🔍|\n---|\Z)'
        category_match = re.search(pattern, content, re.DOTALL)
        
        if category_match:
            category_content = category_match.group(1)
            
            # 記事を抽出
            article_pattern = r'\d+\.\s*\*\*\[(.+?)\]\((.+?)\)\*\*\n\s*🇯🇵\s*\*\*要約\*\*:\s*(.+?)\n\s*\*(.+?)\*'
            articles = re.findall(article_pattern, category_content, re.DOTALL)
            
            for title, url, summary, time in articles:
                # カテゴリを正規化
                if category_key in ['lovable', 'perplexity', 'grok', 'anthropic', 'other']:
                    display_category = 'other'
                else:
                    display_category = category_key
                
                news_data.append({
                    'category': display_category,
                    'title': title.strip(),
                    'summary': summary.strip(),
                    'url': url.strip(),
                    'time': time.strip(),
                    'source': category_name
                })
    
    return {
        'summary': summary,
        'articles': news_data,
        'total_articles': len(news_data),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def save_news_json(news_data: Dict[str, Any], output_path: str = "web/news-data.json"):
    """ニュースデータをJSONファイルとして保存"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ ニュースJSONファイル保存完了: {output_path}")
    print(f"📊 記事数: {news_data['total_articles']}件")
    print(f"📅 生成日時: {news_data['generated_at']}")


def main():
    """メイン処理"""
    try:
        print("🔍 最新レポートファイルを検索中...")
        latest_report = find_latest_report()
        print(f"📄 対象ファイル: {latest_report}")
        
        print("📰 ニュースデータ抽出中...")
        with open(latest_report, 'r', encoding='utf-8') as f:
            content = f.read()
        
        news_data = parse_news_section(content)
        
        print("💾 JSONファイル生成中...")
        save_news_json(news_data)
        
        print("\n🎉 処理完了！")
        print("📝 使用方法:")
        print("   1. Webページから news-data.json を読み込み")
        print("   2. fetch('news-data.json').then(r => r.json())")
        print("   3. レスポンシブなニュース表示に活用")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 