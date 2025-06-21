#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企業ロゴ自動ダウンロードスクリプト

ニュース表示で使用する企業ロゴを自動ダウンロードします。
"""

import os
import requests
import json
from typing import Dict, List
from urllib.parse import urlparse
import time

class LogoDownloader:
    """企業ロゴダウンロード機能"""
    
    def __init__(self):
        """初期化"""
        self.logos_dir = "web/logos"
        self.logo_urls = {
            # AI・Tech企業の公式ロゴURL
            "openai": {
                "url": "https://cdn.openai.com/assets/apple-touch-icon-512x512.png",
                "name": "OpenAI",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg"
            },
            "google": {
                "url": "https://www.google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png",
                "name": "Google", 
                "fallback": "https://developers.google.com/static/site-assets/logo-google.svg"
            },
            "microsoft": {
                "url": "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31",
                "name": "Microsoft",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg"
            },
            "anthropic": {
                "url": "https://www.anthropic.com/images/icons/anthropic-icon.svg",
                "name": "Anthropic",
                "fallback": "https://assets-global.website-files.com/6128b8718aa36c7d7d6ad7dc/6163e2b1a3b13104ad87e7a5_anthopic-icon.svg"
            },
            "meta": {
                "url": "https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5SId3UHWd.svg",
                "name": "Meta",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg"
            },
            "nvidia": {
                "url": "https://www.nvidia.com/content/nvidiaGDC/us/en_US/about-nvidia/legal-info/logo-brand-usage/_jcr_content/root/responsivegrid/nv_container_392921705/nv_container/nv_image.coreimg.svg/1703060329053/nvidia-logo-vert.svg",
                "name": "NVIDIA",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg"
            },
            "apple": {
                "url": "https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png",
                "name": "Apple",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"
            },
            "amazon": {
                "url": "https://d1.awsstatic.com/logos/aws-logo-lockups/poweredbyaws/PB_AWS_logo_RGB_stacked_REV_SQinverse.8c88ac215fe4e441dc42865dd6962ed4f444a90d.png",
                "name": "Amazon/AWS",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
            },
            "tesla": {
                "url": "https://www.tesla.com/ns_videos/commerce/content/dam/tesla/CAR_ACCESSORIES/MODEL_S/CHARGING/1457768-00-A_0.jpg",
                "name": "Tesla",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/b/bb/Tesla_T_symbol.svg"
            },
            "spacex": {
                "url": "https://www.spacex.com/static/images/share.jpg",
                "name": "SpaceX",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/d/de/SpaceX-Logo.svg"
            },
            "polar": {
                "url": "https://avatars.githubusercontent.com/u/47153943?s=200&v=4",
                "name": "Polar",
                "fallback": "https://github.com/polarsource.png"
            },
            "netflix": {
                "url": "https://assets.nflxext.com/us/ffe/siteui/common/icons/nficon2023.ico",
                "name": "Netflix", 
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg"
            },
            "gemini": {
                "url": "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
                "name": "Gemini",
                "fallback": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg"
            },
            "other": {
                "url": "https://cdn-icons-png.flaticon.com/512/3176/3176363.png",
                "name": "その他",
                "fallback": "https://cdn-icons-png.flaticon.com/512/929/929378.png"
            }
        }
        
        # ディレクトリ作成
        os.makedirs(self.logos_dir, exist_ok=True)
    
    def download_all_logos(self) -> Dict[str, str]:
        """
        全企業ロゴをダウンロード
        
        Returns:
            Dict[str, str]: 企業名とローカルファイルパスのマッピング
        """
        print("🖼️  企業ロゴダウンロード開始...")
        
        downloaded = {}
        success_count = 0
        
        for company_id, logo_info in self.logo_urls.items():
            try:
                print(f"📥 {logo_info['name']} ロゴダウンロード中...")
                
                # メインURLでダウンロード試行
                file_path = self._download_logo(company_id, logo_info['url'], logo_info['name'])
                
                if not file_path:
                    # フォールバックURLで再試行
                    print(f"⚠️  メインURL失敗、フォールバックURL使用: {logo_info['name']}")
                    file_path = self._download_logo(company_id, logo_info['fallback'], logo_info['name'], is_fallback=True)
                
                if file_path:
                    downloaded[company_id] = file_path
                    success_count += 1
                    print(f"✅ {logo_info['name']} ダウンロード成功: {file_path}")
                else:
                    print(f"❌ {logo_info['name']} ダウンロード失敗")
                
                # API制限対策で小休止
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ {logo_info['name']} ダウンロードエラー: {e}")
                continue
        
        print(f"\n🎉 ロゴダウンロード完了: {success_count}/{len(self.logo_urls)} 成功")
        
        # ダウンロード結果をJSONで保存
        self._save_logo_mapping(downloaded)
        
        return downloaded
    
    def _download_logo(self, company_id: str, url: str, company_name: str, is_fallback: bool = False) -> str:
        """
        個別ロゴダウンロード
        
        Args:
            company_id (str): 企業ID
            url (str): ロゴURL
            company_name (str): 企業名
            is_fallback (bool): フォールバックURLかどうか
        
        Returns:
            str: ローカルファイルパス（失敗時は空文字）
        """
        try:
            # ヘッダー設定（ブロック回避）
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # ファイル拡張子を決定
            content_type = response.headers.get('content-type', '').lower()
            if 'svg' in content_type or url.endswith('.svg'):
                ext = 'svg'
            elif 'png' in content_type or url.endswith('.png'):
                ext = 'png'
            elif 'jpg' in content_type or 'jpeg' in content_type or url.endswith(('.jpg', '.jpeg')):
                ext = 'jpg'
            elif 'gif' in content_type or url.endswith('.gif'):
                ext = 'gif'
            else:
                # URLから拡張子を推測
                parsed_url = urlparse(url)
                path_ext = os.path.splitext(parsed_url.path)[1].lower().lstrip('.')
                ext = path_ext if path_ext in ['png', 'jpg', 'jpeg', 'svg', 'gif'] else 'png'
            
            # ファイル名決定
            suffix = '_fallback' if is_fallback else ''
            filename = f"{company_id}{suffix}.{ext}"
            file_path = os.path.join(self.logos_dir, filename)
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # ファイルサイズチェック
            file_size = os.path.getsize(file_path)
            if file_size < 100:  # 100バイト未満は無効
                os.remove(file_path)
                return ""
            
            print(f"   💾 保存: {filename} ({file_size:,} bytes)")
            return f"logos/{filename}"  # webディレクトリからの相対パス
            
        except Exception as e:
            print(f"   ❌ ダウンロードエラー: {e}")
            return ""
    
    def _save_logo_mapping(self, downloaded: Dict[str, str]) -> None:
        """
        ダウンロード結果をJSONファイルに保存
        
        Args:
            downloaded (Dict[str, str]): ダウンロード済みロゴのマッピング
        """
        mapping_file = os.path.join(self.logos_dir, "logo_mapping.json")
        
        # 企業名も含めたマッピングを作成
        logo_mapping = {}
        for company_id, file_path in downloaded.items():
            logo_mapping[company_id] = {
                "path": file_path,
                "name": self.logo_urls[company_id]["name"],
                "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(logo_mapping, f, ensure_ascii=False, indent=2)
        
        print(f"📄 ロゴマッピング保存: {mapping_file}")
    
    def get_company_from_title(self, title: str) -> str:
        """
        記事タイトルから企業を特定
        
        Args:
            title (str): 記事タイトル
        
        Returns:
            str: 企業ID（見つからない場合は'other'）
        """
        title_lower = title.lower()
        
        # 企業キーワードマッピング
        company_keywords = {
            "openai": ["openai", "open ai", "chatgpt", "gpt-4", "gpt-3", "gpt", "sam altman"],
            "google": ["google", "alphabet", "bard", "palm", "lamda", "deepmind", "waymo"],
            "microsoft": ["microsoft", "azure", "copilot", "bing", "satya nadella"],
            "anthropic": ["anthropic", "claude", "constitutional ai"],
            "meta": ["meta", "facebook", "instagram", "whatsapp", "llama", "mark zuckerberg"],
            "nvidia": ["nvidia", "jensen huang", "gpu", "cuda", "tegra"],
            "apple": ["apple", "siri", "ios", "iphone", "ipad", "mac", "tim cook"],
            "amazon": ["amazon", "aws", "alexa", "kindle", "prime", "jeff bezos"],
            "tesla": ["tesla", "elon musk", "model s", "model 3", "model y", "model x", "cybertruck"],
            "spacex": ["spacex", "falcon", "dragon", "starship", "starlink"],
            "polar": ["polar"],
            "netflix": ["netflix", "streaming"],
            "gemini": ["gemini", "bard", "google ai"]
        }
        
        # タイトルから企業を特定
        for company_id, keywords in company_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return company_id
        
        return "other"

def main():
    """メイン実行関数"""
    downloader = LogoDownloader()
    
    print("🎯 企業ロゴ自動ダウンロード開始")
    print(f"📁 保存先: {downloader.logos_dir}")
    print(f"🏢 対象企業: {len(downloader.logo_urls)}社")
    print("-" * 50)
    
    # ロゴダウンロード実行
    results = downloader.download_all_logos()
    
    print("\n" + "=" * 50)
    print("🎉 ダウンロード完了サマリー:")
    print(f"✅ 成功: {len(results)}社")
    print(f"❌ 失敗: {len(downloader.logo_urls) - len(results)}社")
    
    if results:
        print("\n📂 ダウンロード済みロゴ:")
        for company_id, path in results.items():
            company_name = downloader.logo_urls[company_id]["name"]
            print(f"   🏢 {company_name}: {path}")
    
    print(f"\n🌐 Web表示準備完了: web/logos/")
    print("💡 次は web/script.js でロゴ表示機能を実装します")

if __name__ == "__main__":
    main() 