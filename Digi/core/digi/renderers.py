import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList

class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'


    def render(self, data, media_type=None, renderer_context=None):            
        errors = data.get("errores")
        token = data.get('token')

        print("data: ", data)

        if errors is not None:
            return super().render(data)

        if isinstance(token, bytes):
            data['token'] = token.decode('utf-8')

        return json.dumps({
            'user': data
        }, separators=(',', ':'))
    