#!/usr/bin/env python3
"""
企業別ニュース収集クラス（無料版）
RSS、Web scraping、NewsAPIを組み合わせて企業ニュースを収集
"""

import yaml
import requests
import feedparser
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import sys

class CompanyNewsCollector:
    def __init__(self, config_path="config/target_companies.yaml", newsapi_key=None):
        """
        初期化
        
        Args:
            config_path: 企業設定ファイルのパス
            newsapi_key: NewsAPIキー
        """
        self.companies = self.load_company_config(config_path)
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY') or "5d88b85486d641faba9a410aca9c138b"
        
        # スクレイピング設定（デフォルト値）
        self.delay_seconds = 2
        self.timeout_seconds = 15
        self.max_retries = 2
        self.user_agent = 'WeeklyBrief-NewsCollector/1.0'
        
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # レート制限対策
        self.last_newsapi_request = 0
        self.newsapi_min_interval = 1.5  # NewsAPIリクエスト間隔（秒）
        
    def load_company_config(self, config_path: str) -> Dict:
        """企業設定ファイルを読み込み（統合版）"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # companiesとadditional_targetsを統合
            all_companies = {}
            
            if 'companies' in config:
                all_companies.update(config['companies'])
            
            if 'additional_targets' in config:
                all_companies.update(config['additional_targets'])
            
            # 設定の正規化（RSSフィード設定を統一）
            for company_id, company_info in all_companies.items():
                # blog_rss を rss_feeds に変換
                if 'blog_rss' in company_info:
                    company_info.setdefault('rss_feeds', []).append(company_info['blog_rss'])
                
                # blog_url を blog_urls に変換
                if 'blog_url' in company_info:
                    company_info.setdefault('blog_urls', []).append(company_info['blog_url'])
                
                # 各種URLをリストに変換
                for url_key in ['news_url', 'research_url', 'deepmind_url']:
                    if url_key in company_info:
                        company_info.setdefault('news_urls', []).append(company_info[url_key])
            
            print(f"✅ 企業設定読み込み完了: {len(all_companies)}社")
            return all_companies
            
        except Exception as e:
            print(f"❌ 企業設定読み込みエラー: {e}")
            return {}
    
    def collect_all_company_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """全企業のニュース収集（統合版）"""
        all_news = []
        
        print(f"🏢 企業ニュース収集開始 - 過去{days_back}日間")
        
        # 統合された企業リストを処理
        for company_id, company_info in self.companies.items():
            try:
                company_news = self.collect_company_news(company_id, company_info, days_back)
                all_news.extend(company_news)
            except Exception as e:
                print(f"❌ {company_info.get('name', company_id)} 収集エラー: {e}")
                continue
        
        print(f"\n🎉 全企業収集完了: 合計{len(all_news)}件")
        return all_news
    
    def collect_company_news(self, company_id: str, company_info: Dict, days_back: int) -> List[Dict[str, Any]]:
        """特定企業のニュース収集（最適化版）"""
        all_items = []
        
        print(f"\n📊 {company_info['name']} の収集中...")
        
        # RSS フィードがある場合は優先
        if company_info.get('rss_feeds'):
            rss_items = self.collect_rss_feeds(company_id, company_info, days_back)
            all_items.extend(rss_items)
        
        # Webスクレイピング
        if company_info.get('blog_urls') or company_info.get('news_urls'):
            web_items = self.collect_web_content(company_id, company_info, days_back)
            all_items.extend(web_items)
        
        # NewsAPIは主要企業のみ（レート制限対策）
        priority_companies = ['openai', 'google_ai', 'anthropic', 'microsoft', 'meta']
        if company_id in priority_companies and company_info.get('keywords'):
            newsapi_items = self.collect_newsapi_content(company_id, company_info, days_back)
            all_items.extend(newsapi_items)
        elif company_info.get('keywords'):
            print(f"    ⚠️  NewsAPI: 主要企業以外はスキップ（レート制限対策）")
        
        # 重複除去
        unique_items = self.remove_duplicates(all_items)
        
        print(f"                                        ✅ {company_info['name']}: {len(unique_items)}件収集")
        return unique_items
    
    def collect_rss_feeds(self, company_id: str, company_info: Dict, days_back: int) -> List[Dict[str, Any]]:
        """RSS フィードからニュース収集"""
        items = []
        
        # メインRSS
        if company_info.get('blog_rss'):
            rss_items = self.fetch_rss_feed(company_info['blog_rss'], company_id, days_back)
            items.extend(rss_items)
        
        # 追加RSS（DeepMind等）
        if company_info.get('deepmind_rss'):
            rss_items = self.fetch_rss_feed(company_info['deepmind_rss'], company_id, days_back)
            items.extend(rss_items)
        
        return items
    
    def fetch_rss_feed(self, rss_url: str, company_id: str, days_back: int) -> List[Dict[str, Any]]:
        """
        RSS フィードを取得・解析（統一フィルタリング版）
        
        Args:
            rss_url: RSS URL
            company_id: 企業ID
            days_back: 過去何日分か
            
        Returns:
            記事リスト
        """
        items = []
        
        for attempt in range(self.max_retries):
            try:
                print(f"  📡 RSS取得中: {rss_url}")
                
                response = self.session.get(rss_url, timeout=self.timeout_seconds)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                if feed.entries:
                    for entry in feed.entries:
                        # 記事情報を構造化
                        item = {
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'published_at': self.parse_date(entry),
                            'summary': entry.get('summary', ''),
                            'company_id': company_id,
                            'source_type': 'rss',
                            'source_url': rss_url,
                            'content': ''  # パフォーマンス改善のため無効化
                        }
                        
                        items.append(item)
                
                # 統一された日付フィルタリングを適用
                filtered_items = self.filter_by_date_range(items, days_back)
                
                print(f"    ✅ RSS解析完了: {len(filtered_items)}件（フィルタ後）")
                return filtered_items
                
            except Exception as e:
                print(f"    ❌ RSS取得エラー (試行 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
        
        return []
    
    def collect_web_content(self, company_id: str, company_info: Dict, days_back: int) -> List[Dict[str, Any]]:
        """Web scraping でニュース収集"""
        items = []
        
        # ブログページ
        if company_info.get('blog_url'):
            blog_items = self.scrape_blog_page(company_info['blog_url'], company_id, days_back)
            items.extend(blog_items)
        
        # ニュースページ
        if company_info.get('news_url'):
            news_items = self.scrape_news_page(company_info['news_url'], company_id, days_back)
            items.extend(news_items)
        
        # 研究ページ
        if company_info.get('research_url'):
            research_items = self.scrape_research_page(company_info['research_url'], company_id, days_back)
            items.extend(research_items)
        
        return items
    
    def scrape_blog_page(self, blog_url: str, company_id: str, days_back: int) -> List[Dict[str, Any]]:
        """ブログページのスクレイピング（日付フィルタリング強化版）"""
        items = []
        
        try:
            print(f"  🕷️  ブログスクレイピング: {blog_url}")
            
            response = self.session.get(blog_url, timeout=self.timeout_seconds)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 一般的なブログ記事のセレクタを試行
            article_selectors = [
                'article',
                '.post',
                '.blog-post',
                '.entry',
                '.news-item',
                '.article-item',
                '[class*="post"]',
                '[class*="article"]'
            ]
            
            articles = []
            for selector in article_selectors:
                articles = soup.select(selector)
                if articles:
                    break
            
            if not articles:
                # フォールバック: リンクを探す
                articles = soup.find_all('a', href=True)
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            valid_items = []
            
            for article in articles[:10]:  # 処理件数を10件に制限（パフォーマンス改善）
                try:
                    # タイトルとURLを抽出
                    if article.name == 'a':
                        title = article.get_text(strip=True)
                        url = article['href']
                    else:
                        title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        url_elem = article.find('a', href=True)
                        if not url_elem:
                            continue
                        url = url_elem['href']
                    
                    # 相対URLを絶対URLに変換
                    if url.startswith('/'):
                        url = urljoin(blog_url, url)
                    
                    # 外部リンクをスキップ
                    if not self.is_same_domain(url, blog_url):
                        continue
                    
                    # 記事の公開日を抽出（強化版）
                    published_date = self.extract_article_date(article, url)
                    
                    # 記事情報を構造化
                    item = {
                        'title': title,
                        'url': url,
                        'published_at': published_date,
                        'summary': '',
                        'company_id': company_id,
                        'source_type': 'web_scraping',
                        'source_url': blog_url,
                        'content': ''
                    }
                    
                    valid_items.append(item)
                    
                except Exception as e:
                    continue
            
            # 日付による事後フィルタリング
            items = self.filter_by_date_range(valid_items, days_back)
            
            print(f"    ✅ ブログスクレイピング完了: {len(items)}件（フィルタ後）")
            
        except Exception as e:
            print(f"    ❌ ブログスクレイピングエラー: {e}")
        
        return items
    
    def scrape_news_page(self, news_url: str, company_id: str, days_back: int) -> List[Dict[str, Any]]:
        """ニュースページのスクレイピング（ブログと同様の処理）"""
        return self.scrape_blog_page(news_url, company_id, days_back)
    
    def scrape_research_page(self, research_url: str, company_id: str, days_back: int) -> List[Dict[str, Any]]:
        """研究ページのスクレイピング（ブログと同様の処理）"""
        return self.scrape_blog_page(research_url, company_id, days_back)
    
    def collect_newsapi_content(self, company_id: str, company_info: Dict, days_back: int) -> List[Dict[str, Any]]:
        """NewsAPI で企業関連ニュース収集（レート制限対策版）"""
        items = []
        
        if not self.newsapi_key or not company_info.get('keywords'):
            print(f"    ⚠️  NewsAPIキーまたはキーワードが未設定")
            return items
        
        try:
            # レート制限対策：前回リクエストから間隔をあける
            elapsed = time.time() - self.last_newsapi_request
            if elapsed < self.newsapi_min_interval:
                wait_time = self.newsapi_min_interval - elapsed
                print(f"    ⏳ レート制限対策: {wait_time:.1f}秒待機")
                time.sleep(wait_time)
            
            print(f"  📰 NewsAPI検索: {company_info['keywords']}")
            
            # 企業名 + キーワードで検索
            search_query = f"{company_info['name']} OR " + " OR ".join(company_info['keywords'])
            
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": search_query,
                "apiKey": self.newsapi_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "from": from_date
            }
            
            self.last_newsapi_request = time.time()
            response = self.session.get(url, params=params, timeout=self.timeout_seconds)
            
            # レート制限エラーの詳細処理
            if response.status_code == 429:
                print(f"    ⚠️  NewsAPIレート制限に達しました - スキップします")
                return []
            elif response.status_code == 401:
                print(f"    ⚠️  NewsAPIキーが無効です - スキップします")
                return []
            elif response.status_code != 200:
                print(f"    ⚠️  NewsAPIエラー: {response.status_code} - スキップします")
                return []
            
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                for article in data['articles']:
                    # 記事情報を構造化
                    item = {
                        'title': article.get("title", ""),
                        'url': article.get("url", ""),
                        'published_at': article.get("publishedAt", ""),
                        'summary': article.get("description", ""),
                        'company_id': company_id,
                        'source_type': 'newsapi',
                        'source_url': 'NewsAPI',
                        'content': article.get("content", "")
                    }
                    items.append(item)
            
            # 統一された日付フィルタリングを追加適用（二重チェック）
            filtered_items = self.filter_by_date_range(items, days_back)
            
            print(f"    ✅ NewsAPI検索完了: {len(filtered_items)}件（フィルタ後）")
            return filtered_items
            
        except requests.exceptions.Timeout:
            print(f"    ⚠️  NewsAPIタイムアウト - スキップします")
            return []
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  NewsAPI接続エラー: {str(e)[:50]}... - スキップします")
            return []
        except Exception as e:
            print(f"    ⚠️  NewsAPI処理エラー: {str(e)[:50]}... - スキップします")
            return []
    
    def extract_content_from_url(self, url: str) -> str:
        """URLから記事本文を抽出（簡易版）"""
        if not url:
            return ""
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 一般的な記事本文のセレクタを試行
            content_selectors = [
                'article',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                'main',
                '.main-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # スクリプトやスタイルを除去
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    text = content_elem.get_text(strip=True)
                    if len(text) > 100:  # 十分な長さがある場合のみ
                        return text[:1000]  # 最初の1000文字
            
            return ""
            
        except Exception:
            return ""
    
    def remove_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複記事の除去"""
        seen_urls = set()
        seen_titles = set()
        unique_items = []
        
        for item in items:
            url = item.get('url', '')
            title = item.get('title', '').lower().strip()
            
            # URL重複チェック
            if url and url in seen_urls:
                continue
            
            # タイトル重複チェック（類似度ベース）
            is_duplicate = False
            for seen_title in seen_titles:
                if self.calculate_similarity(title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue
            
            # 重複なしの場合追加
            unique_items.append(item)
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)
        
        return unique_items
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """テキストの類似度計算（簡易版）"""
        if not text1 or not text2:
            return 0.0
        
        # 単語レベルでの類似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """同じドメインかチェック"""
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except:
            return False
    
    def parse_date(self, entry) -> str:
        """RSS エントリから日付を解析"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'published'):
                # 文字列の日付をパース
                from dateutil import parser
                return parser.parse(entry.published).isoformat()
        except:
            pass
        
        return datetime.now().isoformat()

    def extract_article_date(self, article_element, article_url: str) -> str:
        """記事から公開日を抽出（最適化版）"""
        
        # 手法1: 記事要素内から日付を探す
        date_selectors = [
            'time',
            '.date',
            '.published',
            '.post-date',
            '.article-date',
            '[datetime]',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in date_selectors:
            date_elem = article_element.select_one(selector)
            if date_elem:
                # datetime属性を確認
                if date_elem.has_attr('datetime'):
                    try:
                        from dateutil import parser
                        parsed_date = parser.parse(date_elem['datetime'])
                        return parsed_date.isoformat()
                    except:
                        pass
                
                # テキストから日付を抽出
                date_text = date_elem.get_text(strip=True)
                extracted_date = self.parse_date_text(date_text)
                if extracted_date:
                    return extracted_date
        
        # 手法2: 記事URLから日付パターンを抽出
        url_date = self.extract_date_from_url(article_url)
        if url_date:
            return url_date
        
        # 手法3は無効化（パフォーマンス改善のため）
        # page_date = self.extract_date_from_article_page(article_url)
        # if page_date:
        #     return page_date
        
        # フォールバック: 現在時刻（重要ニュース漏れ防止のため期間内として扱う）
        return datetime.now().isoformat()

    def parse_date_text(self, date_text: str) -> Optional[str]:
        """テキストから日付を解析"""
        if not date_text or len(date_text) < 8:
            return None
        
        try:
            from dateutil import parser
            
            # よくある日付パターンをクリーンアップ
            clean_text = re.sub(r'^(Posted|Published|Date):\s*', '', date_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # 日付解析を試行
            parsed_date = parser.parse(clean_text, fuzzy=True)
            
            # 未来の日付は無効
            if parsed_date > datetime.now():
                return None
                
            # 10年以上前の日付も無効とする
            if parsed_date < datetime.now() - timedelta(days=3650):
                return None
            
            return parsed_date.isoformat()
            
        except Exception:
            return None

    def extract_date_from_url(self, url: str) -> Optional[str]:
        """URLから日付パターンを抽出"""
        if not url:
            return None
        
        try:
            # 一般的なURL日付パターン
            patterns = [
                r'/(\d{4})/(\d{1,2})/(\d{1,2})/',  # /2025/06/22/
                r'/(\d{4})-(\d{1,2})-(\d{1,2})/',  # /2025-06-22/
                r'/(\d{4})(\d{2})(\d{2})/',        # /20250622/
                r'(\d{4}-\d{2}-\d{2})',           # 2025-06-22
                r'(\d{4}/\d{2}/\d{2})',           # 2025/06/22
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    if len(match.groups()) == 3:
                        year, month, day = match.groups()
                        try:
                            date_obj = datetime(int(year), int(month), int(day))
                            return date_obj.isoformat()
                        except ValueError:
                            continue
                    elif len(match.groups()) == 1:
                        date_str = match.group(1).replace('/', '-')
                        try:
                            from dateutil import parser
                            date_obj = parser.parse(date_str)
                            return date_obj.isoformat()
                        except:
                            continue
            
        except Exception:
            pass
        
        return None

    def extract_date_from_article_page(self, article_url: str) -> Optional[str]:
        """記事ページから詳細な日付抽出"""
        try:
            # レート制限対策
            time.sleep(1)
            
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # メタデータから日付を抽出
            meta_selectors = [
                'meta[property="article:published_time"]',
                'meta[name="publish-date"]',
                'meta[name="date"]',
                'meta[name="DC.date.issued"]',
                'meta[itemprop="datePublished"]'
            ]
            
            for selector in meta_selectors:
                meta_elem = soup.select_one(selector)
                if meta_elem:
                    content = meta_elem.get('content') or meta_elem.get('datetime')
                    if content:
                        try:
                            from dateutil import parser
                            parsed_date = parser.parse(content)
                            return parsed_date.isoformat()
                        except:
                            continue
            
            # JSON-LD 構造化データから抽出
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        date_published = json_data.get('datePublished')
                        if date_published:
                            from dateutil import parser
                            parsed_date = parser.parse(date_published)
                            return parsed_date.isoformat()
                except:
                    continue
                    
        except Exception:
            pass
        
        return None

    def filter_by_date_range(self, items: List[Dict[str, Any]], days_back: int) -> List[Dict[str, Any]]:
        """統一された日付範囲フィルタリング"""
        if not items:
            return items
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_items = []
        excluded_count = 0
        
        for item in items:
            try:
                published_at = item.get('published_at', '')
                if not published_at:
                    # 日付が不明な場合は含める（重要ニュース漏れ防止）
                    filtered_items.append(item)
                    continue
                
                # ISO形式の日付を解析
                if isinstance(published_at, str):
                    from dateutil import parser
                    article_date = parser.parse(published_at.replace('Z', '+00:00'))
                    
                    # タイムゾーンを除去して比較
                    if article_date.tzinfo:
                        article_date = article_date.replace(tzinfo=None)
                    
                    if article_date >= cutoff_date:
                        filtered_items.append(item)
                    else:
                        excluded_count += 1
                        print(f"    📅 期間外除外: {item['title'][:50]}... ({article_date.strftime('%Y-%m-%d')})")
                else:
                    # 日付型の場合はそのまま比較
                    if published_at >= cutoff_date:
                        filtered_items.append(item)
                    else:
                        excluded_count += 1
                        
            except Exception as e:
                # 日付解析エラーの場合は含める（重要ニュース漏れ防止）
                print(f"    ⚠️ 日付解析エラー（含める）: {item['title'][:30]}... - {e}")
                filtered_items.append(item)
        
        if excluded_count > 0:
            print(f"    📊 期間フィルタ結果: {len(filtered_items)}件採用、{excluded_count}件除外")
        
        return filtered_items

if __name__ == "__main__":
    # テスト実行
    collector = CompanyNewsCollector()
    news = collector.collect_all_company_news(days_back=3)
    
    print(f"\n📊 収集結果: {len(news)}件")
    for item in news[:5]:
        print(f"  🏢 {item['company_id']}: {item['title'][:50]}...") 