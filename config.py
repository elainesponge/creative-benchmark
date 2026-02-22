"""
Product configuration: all 25 creative tools with their data sources.
"""

PRODUCTS = [
    # ── Non-AI tools ──────────────────────────────────────────────────────────
    {
        "name": "Canva",
        "category": "non-ai",
        "blog_url": "https://www.canva.com/newsroom/",
        "blog_rss": None,
        "appstore_id": "897446215",          # Canva iOS
        "twitter_handle": "canva",
    },
    {
        "name": "Adobe Express",
        "category": "non-ai",
        "blog_url": "https://blog.adobe.com/en/topics/adobe-express",
        "blog_rss": "https://blog.adobe.com/en/topics/adobe-express.rss",
        "appstore_id": "1051937019",
        "twitter_handle": "AdobeExpress",
    },
    {
        "name": "Figma",
        "category": "non-ai",
        "blog_url": "https://www.figma.com/blog/",
        "blog_rss": "https://www.figma.com/blog/rss.xml",
        "appstore_id": "1152747299",
        "twitter_handle": "figma",
    },
    {
        "name": "TikTok Studio",
        "category": "non-ai",
        "blog_url": "https://newsroom.tiktok.com/",
        "blog_rss": None,
        "appstore_id": "6451824786",
        "twitter_handle": "TikTok",
    },
    {
        "name": "YouTube Create",
        "category": "non-ai",
        "blog_url": "https://blog.youtube/",
        "blog_rss": "https://blog.youtube/rss/",
        "appstore_id": "6450122832",
        "twitter_handle": "YouTubeCreate",
    },
    {
        "name": "Adobe Premiere",
        "category": "non-ai",
        "blog_url": "https://blog.adobe.com/en/topics/premiere-pro",
        "blog_rss": "https://blog.adobe.com/en/topics/premiere-pro.rss",
        "appstore_id": "1540921001",          # Premiere Rush iOS
        "twitter_handle": "Premiere",
    },
    {
        "name": "Filmora",
        "category": "non-ai",
        "blog_url": "https://filmora.wondershare.com/filmora-video-editor/whats-new.html",
        "blog_rss": None,
        "appstore_id": "1435833022",
        "twitter_handle": "Filmora_Editor",
    },
    {
        "name": "InShot",
        "category": "non-ai",
        "blog_url": None,
        "blog_rss": None,
        "appstore_id": "997362197",
        "twitter_handle": "InShotApp",
    },
    {
        "name": "Splice",
        "category": "non-ai",
        "blog_url": "https://splice.com/blog/",
        "blog_rss": "https://splice.com/blog/feed/",
        "appstore_id": "409838725",
        "twitter_handle": "Splice",
    },
    # ── AI-native tools ───────────────────────────────────────────────────────
    {
        "name": "Runway",
        "category": "ai",
        "blog_url": "https://runwayml.com/blog/",
        "blog_rss": "https://runwayml.com/blog/rss.xml",
        "appstore_id": "1665024375",
        "twitter_handle": "runwayml",
    },
    {
        "name": "Kling",
        "category": "ai",
        "blog_url": "https://klingai.com/blog/",
        "blog_rss": None,
        "appstore_id": "6670179997",
        "twitter_handle": "KlingAI_Global",
    },
    {
        "name": "Pika",
        "category": "ai",
        "blog_url": "https://pika.art/blog",
        "blog_rss": None,
        "appstore_id": "6448905827",
        "twitter_handle": "pika_labs",
    },
    {
        "name": "Pixverse",
        "category": "ai",
        "blog_url": "https://pixverse.ai/blog",
        "blog_rss": None,
        "appstore_id": "6479062752",
        "twitter_handle": "PixverseAI",
    },
    {
        "name": "Vidu",
        "category": "ai",
        "blog_url": "https://www.vidu.io/blog",
        "blog_rss": None,
        "appstore_id": None,
        "twitter_handle": "ViduAI_Official",
    },
    {
        "name": "Higgsfield",
        "category": "ai",
        "blog_url": "https://higgsfield.ai/blog",
        "blog_rss": None,
        "appstore_id": "6502315560",
        "twitter_handle": "higgsfield_ai",
    },
    {
        "name": "Heygen",
        "category": "ai",
        "blog_url": "https://www.heygen.com/blog",
        "blog_rss": None,
        "appstore_id": "6476584176",
        "twitter_handle": "HeyGen_Official",
    },
    {
        "name": "Midjourney",
        "category": "ai",
        "blog_url": "https://www.midjourney.com/updates",
        "blog_rss": None,
        "appstore_id": None,
        "twitter_handle": "midjourney",
    },
    {
        "name": "Leonardo",
        "category": "ai",
        "blog_url": "https://leonardo.ai/blog",
        "blog_rss": None,
        "appstore_id": "6450261697",
        "twitter_handle": "LeonardoAi_",
    },
    {
        "name": "Adobe Firefly",
        "category": "ai",
        "blog_url": "https://blog.adobe.com/en/topics/firefly",
        "blog_rss": "https://blog.adobe.com/en/topics/firefly.rss",
        "appstore_id": "6445915557",
        "twitter_handle": "AdobeFirefly",
    },
    {
        "name": "ElevenLabs",
        "category": "ai",
        "blog_url": "https://elevenlabs.io/blog",
        "blog_rss": "https://elevenlabs.io/blog/rss.xml",
        "appstore_id": "6473491801",
        "twitter_handle": "elevenlabsio",
    },
    {
        "name": "OpusClip",
        "category": "ai",
        "blog_url": "https://www.opus.pro/blog",
        "blog_rss": None,
        "appstore_id": "6443907303",
        "twitter_handle": "OpusClip",
    },
    {
        "name": "Lovart",
        "category": "ai",
        "blog_url": "https://lovart.ai/blog",
        "blog_rss": None,
        "appstore_id": None,
        "twitter_handle": "lovart_ai",
    },
    {
        "name": "Krea",
        "category": "ai",
        "blog_url": "https://www.krea.ai/blog",
        "blog_rss": None,
        "appstore_id": "6578311050",
        "twitter_handle": "krea_ai",
    },
    {
        "name": "Google Flow",
        "category": "ai",
        "blog_url": "https://blog.google/products/google-labs/",
        "blog_rss": "https://blog.google/rss/",
        "appstore_id": None,
        "twitter_handle": "GoogleLabs",
    },
    {
        "name": "Google Vids",
        "category": "ai",
        "blog_url": "https://workspace.google.com/blog/",
        "blog_rss": "https://workspace.google.com/blog/rss.xml",
        "appstore_id": None,
        "twitter_handle": "GoogleWorkspace",
    },
]

# Map product name → config for quick lookup
PRODUCT_MAP = {p["name"]: p for p in PRODUCTS}

# Scraping settings
REQUEST_TIMEOUT = 15          # seconds
REQUEST_DELAY  = 1.5          # polite delay between requests (seconds)
MAX_RETRIES    = 3
USER_AGENT     = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

# Database
DB_PATH = "data/features.db"

# Scheduling  (24-hour format, local time)
SCRAPE_HOUR   = 8
SCRAPE_MINUTE = 0
