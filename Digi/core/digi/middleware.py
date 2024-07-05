import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import User
from channels.sessions import CookieMiddleware, SessionMiddleware
from channels.auth import AuthMiddlewareStack, AuthMiddleware


@database_sync_to_async
def get_user_from_id(data: dict):
    if data and 'username' in data and 'id' in data:
        try:
            return User.objects.get(username=data['username'], id=data['id'])
        except User.DoesNotExist:
            pass
    return False

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            if not scope or not isinstance(scope, dict):
                raise ValueError("Invalid scope")
            query_string = scope.get('query_string')
            if not query_string:
                raise Exception("No query string in scope")

            _, token = (query_string.decode()).split('=')
            if not token:
                raise Exception("No token in query string")

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                raise Exception("Invalid token") from e

            user = await get_user_from_id(payload)
            
            if not user:
                raise Exception("Invalid token")

            scope['user'] = user
            return await self.inner(scope, receive, send)
        except Exception as e:
            print("Error in JWTAuthMiddleware: ", e)
           



def JWTAuthMiddlewareStack(app):
    return CookieMiddleware(SessionMiddleware(JWTAuthMiddleware(app)))