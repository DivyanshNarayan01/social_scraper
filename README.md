# Social Media Scraper

A Python tool that collects **10 most recent posts** (with engagement metrics and media files) from public brand accounts on **Instagram** and **TikTok**.

> **Default Accounts Scraped:**
> - Instagram: `@example1`, `@example2`, `@example3`  
> - TikTok: `@example1`, `@example2`, `@example3`  

## Features

- **One-command scraping** with `python scrape_social_media.py`
- **Complete media downloads** - photos, videos, carousel posts
- **Comprehensive metadata** - likes, comments, views, shares, timestamps
- **Rate limiting & proxy support** for reliable data collection
- **Structured JSON output** for easy analysis
- **Built for academic research** with proper attribution

## Libraries Used

- [instagrapi](https://github.com/subzeroid/instagrapi) - Instagram API client
- [Evil0ctal's TikTok API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) - TikTok web scraping
- Standard Python libraries for data processing

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd social_scraper_v7
python -m venv venv && source venv/bin/activate  # recommended
pip install -r requirements.txt
```

### 2. Configuration

**Set up Instagram credentials:**
```bash
cp .env.example .env
# Edit .env with your Instagram username/password
```

**Optional - Configure proxies for TikTok:**
```bash
cp proxies.json.example proxies.json
# Edit proxies.json with your proxy settings
```

### 3. Run the Scraper

```bash
python scrape_social_media.py
```

## Configuration

### Environment Variables (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `IG_USERNAME` | Yes | Instagram login username |
| `IG_PASSWORD` | Yes | Instagram password |
| `IG_SESSIONID` | No | Session ID to avoid 2FA (printed after first login) |

### Proxy Configuration (proxies.json)

For TikTok scraping reliability, configure residential proxies:

```json
[
  {
    "host": "proxy1.example.com",
    "port": "8080", 
    "username": "your_username",
    "password": "your_password"
  }
]
```

## Output Structure

```
social_data/
├── instagram/
│   ├── example1/     # downloaded media files
│   ├── example2/
│   └── example3/
├── tiktok/
│   ├── example1/     # downloaded media files (thumbnails if videos blocked by platform)
│   ├── example2/
│   └── example3/
└── social_posts.json  # consolidated metadata
```

### JSON Output Format

```json
{
  "platform": "instagram",
  "username": "example1",
  "post_id": "12345_67890",
  "post_url": "https://www.instagram.com/p/ABC123/",
  "timestamp": "2025-07-14T10:30:00+00:00",
  "caption": "Post text content",
  "likes": 1250,
  "comments": 45,
  "media_type": "photo",
  "media_files": ["social_data/instagram/samsunguk/12345_67890.jpg"]
}
```

## Current Limitations

- **TikTok videos**: Platform blocks direct video downloads; thumbnails saved instead
- **Rate limiting**: Built-in delays prevent API blocks but slow collection
- **Account access**: Some accounts may require manual verification

## Customization

### Change Target Accounts

Edit `scrape_social_media.py`:

```python
INSTAGRAM_HANDLES = ['your_account1', 'your_account2']
TIKTOK_HANDLES = ['your_account1', 'your_account2']
```

### Adjust Post Count

Change the `amount` parameter in the scraper methods:

```python
medias = self.instagram_client.user_medias(user_id, amount=20)  # Instagram
response = await self.tiktok_crawler.fetch_user_post(sec_uid, count=20)  # TikTok
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Instagram checkpoint error | Use residential proxy; log in via official app first |
| TikTok 403/CAPTCHA | Add proxy rotation; reduce request rate |
| Media download failures | Check disk space; verify network connectivity |
| Missing posts | Some accounts may be private or geo-restricted |

## Legal & Ethical Considerations

- **Academic Research Only** - This tool is designed for legitimate research purposes
- **Respect Rate Limits** - Built-in delays prevent server overload
- **Public Data Only** - Only collects publicly available posts
- **Terms of Service** - Ensure compliance with platform ToS
- **Data Privacy** - Handle collected data responsibly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for academic and educational purposes. Please ensure compliance with Instagram and TikTok Terms of Service when using this tool.

## Acknowledgments

- [instagrapi](https://github.com/subzeroid/instagrapi) for reliable Instagram API access
- [Evil0ctal](https://github.com/Evil0ctal) for the TikTok API implementation
- Academic research community for feedback and requirements
