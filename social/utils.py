import re
from urllib.parse import urlparse, parse_qs

def normalize_video_url(url: str) -> str:
    """
    Converts video URLs from popular sites into clean embeddable forms.
    Handles YouTube, Vimeo, TikTok, Instagram, Facebook, Twitch, Dailymotion, Streamable, and X (Twitter).
    """

    if not url:
        return url
    url = url.strip()
    domain = urlparse(url).netloc.lower()

    # ---------------- YOUTUBE ----------------
    # Matches: watch?v=, youtu.be/, shorts/, embed/
    yt_match = re.search(r'(?:v=|be/|shorts/|embed/)([A-Za-z0-9_-]{11})', url)
    if yt_match:
        video_id = yt_match.group(1)
        # ✅ clean canonical embed URL (no params)
        return f"https://www.youtube.com/embed/{video_id}"

    # ---------------- VIMEO ----------------
    if "vimeo.com" in domain:
        m = re.search(r"vimeo\.com/(?:video/)?(\d+)", url)
        if m:
            return f"https://player.vimeo.com/video/{m.group(1)}"

    # ---------------- TIKTOK ----------------
    if "tiktok.com" in domain:
        m = re.search(r"tiktok\.com/.*/video/(\d+)", url)
        if m:
            return f"https://www.tiktok.com/embed/v2/{m.group(1)}/"

    # ---------------- INSTAGRAM ----------------
    if "instagram.com" in domain:
        shortcode = None
        if "/reel/" in url:
            shortcode = url.split("/reel/")[-1].split("/")[0]
        elif "/p/" in url:
            shortcode = url.split("/p/")[-1].split("/")[0]
        if shortcode:
            return f"https://www.instagram.com/p/{shortcode}/embed/"

    # ---------------- FACEBOOK ----------------
    if "facebook.com" in domain or "fb.watch" in domain:
        vid_match = re.search(r"facebook\.com/.*/videos/(\d+)", url)
        if vid_match:
            return f"https://www.facebook.com/video/embed?video_id={vid_match.group(1)}"
        reel_match = re.search(r"facebook\.com/reel/(\d+)", url)
        if reel_match:
            return f"https://www.facebook.com/reel/{reel_match.group(1)}/embed/"

    # ---------------- TWITCH ----------------
    if "twitch.tv" in domain:
        if "/videos/" in url:
            video_id = url.split("/videos/")[-1].split("?")[0]
            # ⚠️ Update 'parent' with your production domain later
            return f"https://player.twitch.tv/?video={video_id}&parent=localhost"
        elif "clips.twitch.tv" in domain:
            slug = url.split("/")[-1]
            return f"https://clips.twitch.tv/embed?clip={slug}&parent=localhost"

    # ---------------- DAILYMOTION ----------------
    if "dailymotion.com" in domain:
        m = re.search(r"dailymotion\.com/video/([a-zA-Z0-9]+)", url)
        if m:
            return f"https://www.dailymotion.com/embed/video/{m.group(1)}"

    # ---------------- STREAMABLE ----------------
    if "streamable.com" in domain:
        shortcode = url.split("/")[-1]
        return f"https://streamable.com/e/{shortcode}"

    # ---------------- TWITTER / X ----------------
    if "twitter.com" in domain or "x.com" in domain:
        tweet_id_match = re.search(r"(?:status|video)/(\d+)", url)
        if tweet_id_match:
            tweet_id = tweet_id_match.group(1)
            return f"https://twitframe.com/show?url=https://twitter.com/i/status/{tweet_id}"

    # ---------------- DEFAULT ----------------
    return url
