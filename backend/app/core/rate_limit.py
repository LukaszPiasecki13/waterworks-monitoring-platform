"""Rate limiting for endpoints prone to credential-guessing abuse.

In-memory (slowapi/limits default): fine for the current single-instance
deployment. Move to a Redis storage backend if the backend ever runs behind
a load balancer with more than one instance, since per-instance counters
would no longer add up to one true limit.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def register_rate_limiting(app: FastAPI) -> None:
    """Wire the limiter into the app, matching the API's error response shape."""
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    def rate_limit_exceeded_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        response = JSONResponse(
            status_code=429, content={"detail": "Too many requests"}
        )
        return limiter._inject_headers(response, request.state.view_rate_limit)
