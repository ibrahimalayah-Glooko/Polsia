"""Twitter/X posting — the real API call, gated behind SANDBOX_MODE and configured credentials."""
from app.config import settings


def _has_user_context_credentials() -> bool:
    return bool(
        settings.twitter_api_key
        and settings.twitter_api_secret
        and settings.twitter_access_token
        and settings.twitter_access_token_secret
    )


def get_twitter_client():
    import tweepy

    return tweepy.Client(
        bearer_token=settings.twitter_bearer_token or None,
        consumer_key=settings.twitter_api_key or None,
        consumer_secret=settings.twitter_api_secret or None,
        access_token=settings.twitter_access_token or None,
        access_token_secret=settings.twitter_access_token_secret or None,
    )


def post_tweet(content: str) -> dict:
    """Post a tweet. In SANDBOX_MODE (or without credentials), simulate instead of calling the real API."""
    if settings.sandbox_mode or not _has_user_context_credentials():
        return {"tweet_id": None, "simulated": True}

    client = get_twitter_client()
    response = client.create_tweet(text=content)
    return {"tweet_id": response.data["id"], "simulated": False}
