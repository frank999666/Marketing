import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import get_settings
from app.models.social import SocialAccount

settings = get_settings()


class SocialManagerService:

    async def exchange_token(
        self,
        platform: str,
        auth_code: str,
        redirect_uri: str,
    ) -> Dict[str, Any]:
        if platform == "instagram":
            return await self._exchange_instagram(auth_code, redirect_uri)
        elif platform == "tiktok":
            return await self._exchange_tiktok(auth_code, redirect_uri)
        elif platform == "twitter":
            return await self._exchange_twitter(auth_code, redirect_uri)
        else:
            raise ValueError(f"Platform {platform} not supported")

    async def publish(
        self,
        platform: str,
        account: SocialAccount,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        if platform == "instagram":
            return await self._publish_instagram(account, content)
        elif platform == "tiktok":
            return await self._publish_tiktok(account, content)
        elif platform == "twitter":
            return await self._publish_twitter(account, content)
        else:
            raise ValueError(f"Platform {platform} not supported")

    async def fetch_metrics(
        self,
        platform: str,
        account: SocialAccount,
    ) -> Dict[str, Any]:
        if platform == "instagram":
            return await self._fetch_instagram_metrics(account)
        elif platform == "tiktok":
            return await self._fetch_tiktok_metrics(account)
        elif platform == "twitter":
            return await self._fetch_twitter_metrics(account)
        return {}

    # Instagram
    async def _exchange_instagram(self, code: str, redirect_uri: str) -> Dict:
        async with httpx.AsyncClient() as client:
            token_resp = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": settings.INSTAGRAM_APP_ID,
                    "client_secret": settings.INSTAGRAM_APP_SECRET,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            token_data = token_resp.json()

            user_resp = await client.get(
                "https://graph.facebook.com/v18.0/me",
                params={
                    "fields": "id,name,email",
                    "access_token": token_data["access_token"],
                },
            )
            user_data = user_resp.json()

            return {
                "account_id": user_data["id"],
                "access_token": token_data["access_token"],
                "username": user_data.get("name", ""),
                "profile_data": {"name": user_data.get("name", "")},
            }

    async def _publish_instagram(self, account: SocialAccount, content: Dict) -> Dict:
        async with httpx.AsyncClient() as client:
            if content.get("image_url"):
                # Create media container
                container_resp = await client.post(
                    f"https://graph.facebook.com/v18.0/{account.account_id}/media",
                    data={
                        "image_url": content["image_url"],
                        "caption": self._format_caption(content),
                        "access_token": account.access_token,
                    },
                )
                container = container_resp.json()

                # Publish
                publish_resp = await client.post(
                    f"https://graph.facebook.com/v18.0/{account.account_id}/media_publish",
                    data={
                        "creation_id": container["id"],
                        "access_token": account.access_token,
                    },
                )
                return publish_resp.json()
            else:
                # Text only post
                resp = await client.post(
                    f"https://graph.facebook.com/v18.0/{account.account_id}/media",
                    data={
                        "caption": self._format_caption(content),
                        "access_token": account.access_token,
                    },
                )
                return resp.json()

    async def _fetch_instagram_metrics(self, account: SocialAccount) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.facebook.com/v18.0/{account.account_id}",
                params={
                    "fields": "followers_count,media_count",
                    "access_token": account.access_token,
                },
            )
            return resp.json()

    # TikTok
    async def _exchange_tiktok(self, code: str, redirect_uri: str) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://business-api.tiktok.com/portal/api/v2/oauth2/access_token/",
                data={
                    "app_id": settings.TIKTOK_APP_ID,
                    "secret": settings.TIKTOK_APP_SECRET,
                    "auth_code": code,
                    "grant_type": "authorization_code",
                },
            )
            data = resp.json().get("data", {})
            return {
                "account_id": data.get("openid", ""),
                "access_token": data.get("access_token", ""),
                "refresh_token": data.get("refresh_token", ""),
                "username": data.get("name", ""),
                "profile_data": {},
            }

    async def _publish_tiktok(self, account: SocialAccount, content: Dict) -> Dict:
        # TikTok requires video upload via their API
        # This is a simplified version
        return {"status": "pending", "message": "Video upload required"}

    async def _fetch_tiktok_metrics(self, account: SocialAccount) -> Dict:
        return {"followers": 0, "likes": 0}

    # Twitter
    async def _exchange_twitter(self, code: str, redirect_uri: str) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": settings.TWITTER_API_KEY,
                },
                auth=(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET),
            )
            data = resp.json()

            user_resp = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {data['access_token']}"},
            )
            user_data = user_resp.json().get("data", {})

            return {
                "account_id": user_data.get("id", ""),
                "access_token": data.get("access_token", ""),
                "refresh_token": data.get("refresh_token", ""),
                "username": user_data.get("username", ""),
                "profile_data": {"name": user_data.get("name", "")},
            }

    async def _publish_twitter(self, account: SocialAccount, content: Dict) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.twitter.com/2/tweets",
                json={"text": self._format_caption(content)},
                headers={"Authorization": f"Bearer {account.access_token}"},
            )
            return resp.json()

    async def _fetch_twitter_metrics(self, account: SocialAccount) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.twitter.com/2/users/{account.account_id}",
                params={"user.fields": "public_metrics"},
                headers={"Authorization": f"Bearer {account.access_token}"},
            )
            data = resp.json().get("data", {}).get("public_metrics", {})
            return {
                "followers": data.get("followers_count", 0),
                "tweets": data.get("tweet_count", 0),
            }

    def _format_caption(self, content: Dict) -> str:
        parts = []
        if content.get("text"):
            parts.append(content["text"])
        if content.get("hashtags"):
            hashtags = " ".join(f"#{h.lstrip('#')}" for h in content["hashtags"])
            parts.append(hashtags)
        return "\n\n".join(parts)
