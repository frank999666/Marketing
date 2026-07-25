import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status


class RateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self):
        self._requests: Dict[str, list[float]] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def check(self, request: Request, key: str, max_requests: int, window_seconds: int) -> None:
        client_id = self._get_client_id(request)
        cache_key = f"{key}:{client_id}"
        now = time.time()

        self._requests[cache_key] = [
            t for t in self._requests[cache_key] if now - t < window_seconds
        ]

        if len(self._requests[cache_key]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        self._requests[cache_key].append(now)


limiter = RateLimiter()
