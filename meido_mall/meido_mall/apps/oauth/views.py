from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework import status

from . import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import QQAuthUser
from oauth.utils import generate_save_user_token


class QQAuthURLView(APIView):
    """生成QQ扫码url"""
    def get(self, request):
        next = request.query_params.get('next')
        if not next:
            next = '/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        return Response({'login_url': login_url})


class QQAuthUserView(GenericAPIView):
    """用户扫码登录的回调处理"""
    serializer_class = serializers.QQAuthUserSerializer
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return  Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception:
            return Response({'message': 'QQ服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用openid查询该qq用户是否在美多商城中绑定过用户
        try:
            qqauth_model = QQAuthUser.objects.get(openid=openid)
        except QQAuthUserView.DoesNotExist:
            # 如果openid没有绑定过美多商城中的用户
            # 把openid进行加密安全处理,再响应给浏览器,让它先帮我们保存一会
            openid_sin = generate_save_user_token(openid)
            return Response({'access_token': openid_sin})
        else:
            # 如果openid已经绑定过美多商城中的用户(生成jwt token直接让它登录成功)
            # 手动生成token

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数
            # 获取user对象
            user = qqauth_model.user
            payload = jwt_payload_handler(user)  # 生成载荷
            token = jwt_encode_handler(payload)  # 根据载荷生成token
            return Response({
                'token': token,
                'username': user.username,
                'user_id': user.id
            })

    def post(self, request):
        """openid绑定到用户"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # 生成JWT token，并响应
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })
        return response

