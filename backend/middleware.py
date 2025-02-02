from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_cache = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip in self.ip_cache:
            request_times = self.ip_cache[client_ip]
            self.ip_cache[client_ip] = [t for t in request_times if current_time - t < self.window_seconds]
            if len(self.ip_cache[client_ip]) >= self.max_requests:
                raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

        else:
            self.ip_cache[client_ip] = []

        self.ip_cache[client_ip].append(current_time)

        response = await call_next(request)
        return response
