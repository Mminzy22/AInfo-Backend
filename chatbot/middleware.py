from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


class JWTAuthMiddleware(BaseMiddleware):
    """
    Websocket 연결을 위한 JWT 인증 미들웨어

    해당 미들웨어는 Websocket 연결 요청 시 쿼리 문자열에서 JWT 토큰을 추출하고,
    해당 토큰을 검증해서 user_id를 `scope`에 저장합니다.
    인증이 실패하면 `scope`에 어류 메시지를 추가합니다.

    사용 방식
    - 클라이언트는 Websocket 연결 시 `?token=<access_token>` 형태로 토큰을 전달해야 합니다.
    - 유효한 토큰이면 `scope["user_id"]`에 user_id를 추가합니다.
    = 유효하지 않거나 토큰이 없으면 `scope["error"]`에 오류 메시지를 추가합니다.

    매서드(Method)
    - get_token_from_scope(scope): 쿼리 문자열에서 JWT 토큰을 추출하는 매서드
    - get_user_from_token(token): 추출한 토큰을 검증하고, user_id를 반환하는 매서드
    """

    async def __call__(self, scope, receive, send):
        token = self.get_token_from_scope(scope)

        if token is not None:
            user_id = await self.get_user_from_token(token)
            if user_id:
                scope["user_id"] = user_id
            else:
                scope["error"] = "invalid_token"
        else:
            scope["error"] = "no_token"

        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):
        query_string = parse_qs(scope.get("query_string", b"").decode("utf-8"))
        return query_string.get("token", [None])[0]

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            return access_token["user_id"]
        except (TokenError, InvalidToken) as e:
            print(f"토큰 검증 실패: {e}")
            return None
