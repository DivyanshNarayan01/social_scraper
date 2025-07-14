# Social Media Scraper - Claude Instructions

## Project Overview
This is a social media scraper for academic research that collects posts from brand accounts on Instagram and TikTok, including engagement metrics and media files. Currently configured to scrape 2 posts per account for testing (can be modified in script).

## Key Files
- `scrape_social_media.py` - Main scraper script
- `.env` - Environment variables (Instagram credentials)
- `tiktok_api/` - Evil0ctal TikTok API integration
- `proxies.json` - Residential proxy configuration (11 proxies)
- `social_data/` - Output directory for scraped content
- `social_posts.json` - Consolidated metadata file

## Default Accounts Scraped
- **Instagram**: @samsunguk, @googlepixeluk, @apple
- **TikTok**: @samsunguk, @googlepixel, @apple

## How to Run
```bash
python3 scrape_social_media.py
```

## Environment Variables (.env file)
Required:
- `IG_USERNAME=your_instagram_username` - Instagram login username
- `IG_PASSWORD=your_instagram_password` - Instagram password

Optional:
- `IG_SESSIONID` - Reuse session to avoid 2FA (printed after first login)

## Residential Proxies (proxies.json file)
**SETUP REQUIRED**: Configure residential proxies in `proxies.json` for TikTok scraping.
The scraper automatically rotates between proxies for each TikTok user to avoid detection.

Example format:
```json
[
  {
    "host": "proxy_host",
    "port": "proxy_port", 
    "username": "proxy_username",
    "password": "proxy_password"
  }
]
```

## Dependencies
**INSTALLED**: All dependencies are already set up.

Core packages:
- `instagrapi` - Instagram API client
- `tqdm` - Progress bars
- `python-dotenv` - Environment variable loading
- `requests` - HTTP requests
- `pyyaml` - YAML configuration parsing

**TikTok Integration**: Uses Evil0ctal's Douyin_TikTok_Download_API (already cloned in `tiktok_api/`)

## Output Structure
```
social_data/
├── instagram/
│   ├── samsunguk/     # downloaded media files
│   ├── googlepixeluk/
│   └── apple/
├── tiktok/
│   ├── samsunguk/
│   ├── googlepixel/
│   └── apple/
└── social_posts.json  # consolidated metadata
```

## Current Status & Capabilities
**Instagram**: Full functionality - metadata + media downloads (photos/videos)
**TikTok**: Metadata collection + thumbnail downloads (videos blocked by platform)
**Proxy Rotation**: 11 residential proxies working correctly
**Post URLs**: Direct links to original posts included in output
**Error Handling**: Graceful fallbacks for blocked content

**Data Collected**:
- **Instagram**: post_id, post_url, timestamp, caption, likes, comments, media_type, media_files
- **TikTok**: post_id, post_url, timestamp, caption, likes, comments, views, shares, media_type, media_files, download_note

**Platform Limitations & Solutions**:
1. **TikTok Video Blocking**: Platform blocks direct video downloads via API
   - **Solution**: Implemented thumbnail download fallback
   - **Result**: All metadata collected, thumbnails saved for visual reference
2. **Instagram API Warnings**: Non-critical compatibility warnings from instagrapi
   - **Impact**: None - all functionality works correctly
3. **Rate Limiting**: Built-in delays prevent API blocks
   - **Instagram**: 1s between posts, 3s between users  
   - **TikTok**: 2s between posts, 5s between users

## Configuration
**Current Settings**:
- Scraping 2 posts per account (line 178, 274 in script)
- To change: modify `amount=2` for Instagram and `count=2` for TikTok

**Adding More Accounts**: Edit lists in `scrape_social_media.py`:
- `INSTAGRAM_HANDLES = ['samsunguk', 'googlepixeluk', 'apple']` (line 22)
- `TIKTOK_HANDLES = ['samsunguk', 'googlepixel', 'apple']` (line 23)

## Rate Limiting
Built-in delays:
- 1 second between Instagram posts
- 2 seconds between TikTok videos (async)
- 3 seconds between Instagram users
- 5 seconds between TikTok users

## Testing Commands
- **Run scraper**: `python3 scrape_social_media.py`
- **Check results**: `cat social_data/social_posts.json | jq length` (if jq installed)
- **View structure**: `tree social_data/` (if tree installed)

## Technical Implementation Lessons

### TikTok API Evolution
**Problem**: Initial TikTokApi library failed with multiple compatibility issues
**Solution**: Replaced with Evil0ctal's Douyin_TikTok_Download_API
**Result**: Stable metadata collection with proper anti-bot handling

### Video Download Challenges
**Discovery**: TikTok blocks direct video access even with proper API calls
**Evidence**: API returns video URLs but all result in 403 Forbidden
**Analysis**: Platform protection mechanisms prevent bulk video downloads
**Adaptation**: Implemented thumbnail fallback system for content reference

### Proxy Strategy
**Implementation**: 11 residential proxies with automatic rotation
**Effectiveness**: Prevents IP-based blocking for TikTok scraping
**Configuration**: Updates tiktok_api/crawlers/tiktok/web/config.yaml automatically

### Instagram Stability
**Success Factor**: instagrapi library with session reuse
**Best Practice**: Save IG_SESSIONID to avoid repeated 2FA prompts
**Media Downloads**: Full video/photo downloads work reliably

## Latest Test Results (2025-07-12)
Successfully collected:
- 6 Instagram posts (2 per account × 3 accounts) - full media
- 6 TikTok posts (2 per account × 3 accounts) - metadata + thumbnails
- Total: 12 posts with complete data structure
- Post URLs: Direct links to all original content

## Project Evolution Timeline
1. **Initial Setup**: Basic Instagram scraping with TikTokApi
2. **Proxy Integration**: Added 11 residential proxies for TikTok
3. **API Replacement**: Switched to Evil0ctal for TikTok stability  
4. **Fallback Implementation**: Added thumbnail downloads for blocked videos
5. **URL Enhancement**: Added direct post URLs to output
6. **Current State**: Robust dual-platform scraper with error handling