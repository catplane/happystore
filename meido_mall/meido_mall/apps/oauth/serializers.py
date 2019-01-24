from rest_framework import serializers
from django_redis import get_redis_connection
from .utils import check_save_user_token
from users.models import User
from .models import QQAuthUser


class QQAuthUserSerializer(serializers.Serializer):
    """绑定用户的序列化器"""
    access_token = serializers.CharField(label="操作凭证")
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 检验access_token
        access_token = attrs['access_token']
        openid = check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError('openid无敌')
        attrs['access_token'] = openid  # 把解密后的openid保存到反序列化的大字典中以备后期绑定用户时使用
        # 验证短信验证码是否正确
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs.get('mobile')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        # 获取前端传过来的验证码
        sms_code = attrs.get('sms_code')
        if real_sms_code.decode() != sms_code:# 注意redis中取出来的验证码是bytes类型注意类型处理
            raise serializers.ValidationError('验证码错误')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            if not user.check_password(attrs.get('password')):
                raise serializers.ValidationError('密码不正确')
            else:
                attrs['user'] = user

            return attrs

        def create(self, validated_data):
            """把openid和user进行绑定"""
            user = validated_data.get('user')
            if not user:
                user = User(
                    username=validated_data.get('mobile'),
                    password=validated_data.get('password'),
                    mobile=validated_data.get('mobile')
                )
                user.set_password(validated_data.get('password'))
                user.save()
                QQAuthUser.objects.create(
                    user=user,
                    openid=validated_data.get('access_token')
                )
                return user