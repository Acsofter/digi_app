import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User



class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'bearer'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if len(auth_header) <= 1: return None
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8') 

        if not auth_header or prefix.lower() != self.authentication_header_prefix:
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=('HS256',))
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Sesion Expirada', code=403)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token invalido', code=401)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Ningun usuario con este token', code=401)

        if not user.is_active:
            raise exceptions.AuthenticationFailed('El usuario esta inhabilitado', code=401)

        return (user, token)
