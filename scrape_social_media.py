#!/usr/bin/env python3

import os
import json
import time
import requests
import asyncio
import random
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

from instagrapi import Client as InstagramClient
import sys
sys.path.append('./tiktok_api')
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler
from crawlers.tiktok.web.utils import SecUserIdFetcher

load_dotenv()

INSTAGRAM_HANDLES = ['samsunguk', 'googlepixeluk', 'apple']
TIKTOK_HANDLES = ['samsunguk', 'googlepixel', 'apple']

BASE_DIR = Path("social_data")
INSTAGRAM_DIR = BASE_DIR / "instagram"
TIKTOK_DIR = BASE_DIR / "tiktok"

class SocialMediaScraper:
    def __init__(self):
        self.instagram_client = None
        self.tiktok_crawler = None
        self.all_posts = []
        self.proxies = self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from environment variables or proxies.json file"""
        proxies = []
        
        # Try to load from proxies.json file first
        try:
            if os.path.exists('proxies.json'):
                with open('proxies.json', 'r') as f:
                    proxy_data = json.load(f)
                    if isinstance(proxy_data, list):
                        for proxy in proxy_data:
                            if all(key in proxy for key in ['host', 'port', 'username', 'password']):
                                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                                proxies.append(proxy_url)
        except Exception as e:
            print(f"WARNING: Could not load proxies.json: {e}")
        
        # Fallback to single proxy from .env
        if not proxies:
            single_proxy = os.getenv('TIKTOK_PROXY')
            if single_proxy:
                proxies.append(single_proxy)
        
        if proxies:
            print(f"Loaded {len(proxies)} residential proxies")
        else:
            print("WARNING: No proxies configured - TikTok scraping may fail")
            
        return proxies
    
    def get_random_proxy(self):
        """Get a random proxy from the available list"""
        if self.proxies:
            return random.choice(self.proxies)
        return None
        
    def setup_directories(self):
        BASE_DIR.mkdir(exist_ok=True)
        INSTAGRAM_DIR.mkdir(exist_ok=True)
        TIKTOK_DIR.mkdir(exist_ok=True)
        
        for handle in INSTAGRAM_HANDLES:
            (INSTAGRAM_DIR / handle).mkdir(exist_ok=True)
            
        for handle in TIKTOK_HANDLES:
            (TIKTOK_DIR / handle).mkdir(exist_ok=True)
    
    def setup_instagram(self):
        username = os.getenv('IG_USERNAME')
        password = os.getenv('IG_PASSWORD')
        session_id = os.getenv('IG_SESSIONID')
        
        if not username or not password:
            print("WARNING: Instagram credentials not found in .env file")
            return False
            
        try:
            self.instagram_client = InstagramClient()
            
            if session_id:
                print("Using existing Instagram session...")
                self.instagram_client.set_settings({'session_id': session_id})
                try:
                    self.instagram_client.login(username, password)
                except Exception as e:
                    print(f"WARNING: Session login failed, trying fresh login: {e}")
                    self.instagram_client = InstagramClient()
                    self.instagram_client.login(username, password)
            else:
                print("Logging into Instagram...")
                self.instagram_client.login(username, password)
                
            print(f"SUCCESS: Instagram login successful for @{username}")
            
            # Print session ID for future use
            settings = self.instagram_client.get_settings()
            if 'session_id' in settings:
                print(f"TIP: Save this session ID to .env as IG_SESSIONID: {settings['session_id']}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Instagram login failed: {e}")
            return False
    
    def setup_tiktok(self):
        try:
            random_proxy = self.get_random_proxy()
            
            if random_proxy:
                print(f"Using proxy: {random_proxy.split('@')[1] if '@' in random_proxy else random_proxy}")
                # Update TikTok config with random proxy
                self.update_tiktok_proxy_config(random_proxy)
                
            self.tiktok_crawler = TikTokWebCrawler()
            print("SUCCESS: TikTok Evil0ctal API initialized")
            return True
            
        except Exception as e:
            print(f"ERROR: TikTok API setup failed: {e}")
            print("WARNING: TikTok requires proper configuration")
            return False
    
    def update_tiktok_proxy_config(self, proxy_url):
        """Update TikTok config with proxy information"""
        try:
            import yaml
            config_path = './tiktok_api/crawlers/tiktok/web/config.yaml'
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update proxy configuration
            config['TokenManager']['tiktok']['proxies']['http'] = proxy_url
            config['TokenManager']['tiktok']['proxies']['https'] = proxy_url
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            print(f"WARNING: Could not update TikTok proxy config: {e}")
    
    def download_media(self, url, filepath):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"ERROR: Failed to download {filepath}: {e}")
            return False
    
    def scrape_instagram_user(self, username):
        if not self.instagram_client:
            return []
            
        try:
            print(f"Scraping Instagram @{username}...")
            user_id = self.instagram_client.user_id_from_username(username)
            medias = self.instagram_client.user_medias(user_id, amount=10)
            
            posts = []
            user_dir = INSTAGRAM_DIR / username
            
            for i, media in enumerate(tqdm(medias, desc=f"Processing @{username}")):
                try:
                    # Handle media_type as either enum or int
                    media_type_name = 'unknown'
                    if hasattr(media.media_type, 'name'):
                        media_type_name = media.media_type.name.lower()
                    elif isinstance(media.media_type, int):
                        # Map media type integers to names
                        type_map = {1: 'photo', 2: 'video', 8: 'carousel'}
                        media_type_name = type_map.get(media.media_type, 'unknown')
                    
                    post_data = {
                        'platform': 'instagram',
                        'username': username,
                        'post_id': media.id,
                        'post_url': f"https://www.instagram.com/p/{media.code}/",
                        'timestamp': media.taken_at.isoformat(),
                        'caption': media.caption_text or "",
                        'likes': media.like_count,
                        'comments': media.comment_count,
                        'media_type': media_type_name,
                        'media_files': []
                    }
                    
                    # Download media files based on type
                    if media_type_name == 'photo' or media.media_type == 1:
                        filename = f"{media.id}.jpg"
                        filepath = user_dir / filename
                        if hasattr(media, 'thumbnail_url') and media.thumbnail_url:
                            if self.download_media(media.thumbnail_url, filepath):
                                post_data['media_files'].append(str(filepath))
                                
                    elif media_type_name == 'video' or media.media_type == 2:
                        filename = f"{media.id}.mp4"
                        filepath = user_dir / filename
                        if hasattr(media, 'video_url') and media.video_url:
                            if self.download_media(media.video_url, filepath):
                                post_data['media_files'].append(str(filepath))
                                
                    elif media_type_name == 'carousel' or media.media_type == 8:
                        if hasattr(media, 'resources') and media.resources:
                            for j, resource in enumerate(media.resources):
                                resource_type = 'unknown'
                                if hasattr(resource.media_type, 'name'):
                                    resource_type = resource.media_type.name.lower()
                                elif isinstance(resource.media_type, int):
                                    type_map = {1: 'photo', 2: 'video'}
                                    resource_type = type_map.get(resource.media_type, 'unknown')
                                
                                if resource_type == 'photo' or resource.media_type == 1:
                                    filename = f"{media.id}_{j}.jpg"
                                    filepath = user_dir / filename
                                    if hasattr(resource, 'thumbnail_url') and resource.thumbnail_url:
                                        if self.download_media(resource.thumbnail_url, filepath):
                                            post_data['media_files'].append(str(filepath))
                                elif resource_type == 'video' or resource.media_type == 2:
                                    filename = f"{media.id}_{j}.mp4"
                                    filepath = user_dir / filename
                                    if hasattr(resource, 'video_url') and resource.video_url:
                                        if self.download_media(resource.video_url, filepath):
                                            post_data['media_files'].append(str(filepath))
                    
                    posts.append(post_data)
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"WARNING: Error processing Instagram post {media.id}: {e}")
                    continue
            
            print(f"SUCCESS: Instagram @{username}: {len(posts)} posts scraped")
            return posts
            
        except Exception as e:
            print(f"ERROR: Failed to scrape Instagram @{username}: {e}")
            return []
    
    async def scrape_tiktok_user_async(self, username):
        if not self.tiktok_crawler:
            return []
            
        try:
            print(f"Scraping TikTok @{username}...")
            
            # Get user secUid from username
            user_url = f"https://www.tiktok.com/@{username}"
            sec_uid = await SecUserIdFetcher.get_secuid(user_url)
            
            if not sec_uid:
                print(f"ERROR: Could not get secUid for @{username}")
                return []
            
            # Get user posts
            response = await self.tiktok_crawler.fetch_user_post(sec_uid, count=10)
            
            posts = []
            user_dir = TIKTOK_DIR / username
            
            if response and 'itemList' in response:
                items = response['itemList'][:10]  # Limit to 10 posts
                
                for i, item in enumerate(items):
                    try:
                        # Extract post data
                        post_data = {
                            'platform': 'tiktok',
                            'username': username,
                            'post_id': item.get('id', ''),
                            'post_url': f"https://www.tiktok.com/@{username}/video/{item.get('id', '')}",
                            'timestamp': datetime.fromtimestamp(item.get('createTime', 0)).isoformat(),
                            'caption': item.get('desc', ''),
                            'likes': item.get('stats', {}).get('diggCount', 0),
                            'comments': item.get('stats', {}).get('commentCount', 0),
                            'views': item.get('stats', {}).get('playCount', 0),
                            'shares': item.get('stats', {}).get('shareCount', 0),
                            'media_type': 'video',
                            'media_files': []
                        }
                        
                        # Download video
                        video_id = item.get('id', f'video_{i}')
                        filename = f"{video_id}.mp4"
                        filepath = user_dir / filename
                        
                        # Get video download URL - TikTok blocks direct video access
                        video_info = item.get('video', {})
                        video_url = video_info.get('downloadAddr') or video_info.get('playAddr')
                        
                        if video_url and self.download_media(video_url, filepath):
                            post_data['media_files'].append(str(filepath))
                        else:
                            # Fallback: Download thumbnail/cover image
                            cover_url = video_info.get('cover') or video_info.get('originCover')
                            if cover_url:
                                thumb_filename = f"{video_id}_thumb.jpg"
                                thumb_filepath = user_dir / thumb_filename
                                if self.download_media(cover_url, thumb_filepath):
                                    post_data['media_files'].append(str(thumb_filepath))
                                    print(f"  Downloaded thumbnail for video {video_id} (video blocked by TikTok)")
                            else:
                                print(f"  ERROR: No video or thumbnail URL available for {video_id}")
                        
                        # Add note about TikTok video blocking
                        if not video_url:
                            post_data['download_note'] = 'Video URL blocked by TikTok - thumbnail saved instead'
                        
                        posts.append(post_data)
                        print(f"  Processed TikTok video {i+1}/10 from @{username}")
                        
                        await asyncio.sleep(2)  # Rate limiting for TikTok
                        
                    except Exception as e:
                        print(f"WARNING: Error processing TikTok video: {e}")
                        continue
            
            print(f"SUCCESS: TikTok @{username}: {len(posts)} posts scraped")
            return posts
            
        except Exception as e:
            print(f"ERROR: Failed to scrape TikTok @{username}: {e}")
            return []
    
    def scrape_tiktok_user(self, username):
        # Wrapper to run async function in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.scrape_tiktok_user_async(username))
    
    def save_results(self):
        output_file = BASE_DIR / "social_posts.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_posts, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")
        print(f"Total posts collected: {len(self.all_posts)}")
        
        # Summary by platform
        instagram_count = len([p for p in self.all_posts if p['platform'] == 'instagram'])
        tiktok_count = len([p for p in self.all_posts if p['platform'] == 'tiktok'])
        
        print(f"   Instagram: {instagram_count} posts")
        print(f"   TikTok: {tiktok_count} posts")
    
    def run(self):
        print("Starting Social Media Scraper...")
        print("=" * 50)
        
        # Setup
        self.setup_directories()
        
        instagram_ready = self.setup_instagram()
        tiktok_ready = self.setup_tiktok()
        
        if not instagram_ready and not tiktok_ready:
            print("ERROR: Neither Instagram nor TikTok could be initialized. Exiting.")
            return
        
        print("\n" + "=" * 50)
        print("Starting data collection...")
        
        # Scrape Instagram
        if instagram_ready:
            for handle in INSTAGRAM_HANDLES:
                posts = self.scrape_instagram_user(handle)
                self.all_posts.extend(posts)
                time.sleep(3)  # Pause between users
        
        # Scrape TikTok with proxy rotation
        if tiktok_ready:
            for i, handle in enumerate(TIKTOK_HANDLES):
                # Rotate proxy for each user to avoid detection
                if i > 0 and self.proxies:
                    print(f"Rotating proxy for better success rate...")
                    self.setup_tiktok()  # Re-initialize with new proxy
                    
                posts = self.scrape_tiktok_user(handle)
                self.all_posts.extend(posts)
                time.sleep(5)  # Pause between users
        
        # Save results
        print("\n" + "=" * 50)
        self.save_results()
        print("SUCCESS: Scraping completed!")

if __name__ == "__main__":
    scraper = SocialMediaScraper()
    scraper.run()