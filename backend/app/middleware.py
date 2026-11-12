from fastapi.responses import JSONResponse


class _RequestBodyTooLarge(Exception):
    pass


class EnrichmentBodySizeLimitMiddleware:
    """Reject oversized enrichment bodies before JSON/Pydantic parsing."""

    def __init__(self, app, max_body_bytes: int):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"] != "/v1/activities/enrich"
        ):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                declared_size = int(content_length)
            except ValueError:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Content-Length invalide"},
                )
                await response(scope, receive, send)
                return

            if declared_size > self.max_body_bytes:
                await self._too_large_response(scope, receive, send)
                return

        received_size = 0

        async def receive_with_limit():
            nonlocal received_size
            message = await receive()
            if message["type"] == "http.request":
                received_size += len(message.get("body", b""))
                if received_size > self.max_body_bytes:
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, receive_with_limit, send)
        except _RequestBodyTooLarge:
            await self._too_large_response(scope, receive, send)

    async def _too_large_response(self, scope, receive, send):
        response = JSONResponse(
            status_code=413,
            content={"detail": "Corps de requête trop volumineux"},
        )
        await response(scope, receive, send)
