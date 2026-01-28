import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RateLimiter:
    def __init__(
        self,
        max_attempts: int,
        window_seconds: int,
        ban_seconds: int = 0,
        error_detail: str = "Rate limit exceeded",
    ) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.ban_seconds = ban_seconds
        self.error_detail = error_detail
        self._requests: dict[str, Deque[float]] = defaultdict(deque)
        self._banned_until: dict[str, float] = {}

    def _prune(self, key: str, now: float) -> None:
        window_start = now - self.window_seconds
        bucket = self._requests[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if not bucket:
            self._requests.pop(key, None)

    def _check_ban(self, key: str, now: float) -> None:
        banned_until = self._banned_until.get(key)
        if not banned_until:
            return
        if banned_until <= now:
            self._banned_until.pop(key, None)
            return
        raise HTTPException(status_code=429, detail=self.error_detail)

    def hit(self, key: str) -> None:
        now = time.time()
        self._check_ban(key, now)
        self._prune(key, now)
        bucket = self._requests.setdefault(key, deque())
        if len(bucket) >= self.max_attempts:
            if self.ban_seconds:
                self._banned_until[key] = now + self.ban_seconds
            raise HTTPException(status_code=429, detail=self.error_detail)
        bucket.append(now)

    def check(self, key: str) -> None:
        now = time.time()
        self._check_ban(key, now)
        self._prune(key, now)

    def register_failure(self, key: str) -> None:
        now = time.time()
        self._check_ban(key, now)
        self._prune(key, now)
        bucket = self._requests.setdefault(key, deque())
        bucket.append(now)
        if len(bucket) > self.max_attempts:
            if self.ban_seconds:
                self._banned_until[key] = now + self.ban_seconds
            raise HTTPException(status_code=429, detail=self.error_detail)

    def reset(self, key: str) -> None:
        self._requests.pop(key, None)
        self._banned_until.pop(key, None)
