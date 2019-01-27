from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData


def generate_save_user_token(openid):
    """对openid进行加密"""
    serializer = Serializer(settings.SECRET_KEY, 600)
    data = {'openid': openid}
    access_token_bytes = serializer.dumps(data)
    print(access_token_bytes, access_token_bytes.decode())
    return access_token_bytes.decode()


def check_save_user_token(openid):
    """对加密的openid进行解密"""

    serializer = Serializer(settings.SECRECT_KEY, 600)
    try:
        data = serializer.loads(openid)
    except BadData:
        return None
    else:
        return data.get('openid')