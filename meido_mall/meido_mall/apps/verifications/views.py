from random import randint
import logging
from django.shortcuts import render
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# from meido_mall.meido_mall.libs.yuntongxun.sms import CCP
from . import constants

logger = logging.getLogger('django')

class SMSCodeView(APIView):
    def get(self, request, mobile):
        redis_conn = get_redis_connection('verify_codes')
        flag = redis_conn.get('send_flag_%s' % mobile)
        if flag:
            return Response({'message': '请勿频繁发送短信'},
                            status=status.HTTP_400_BAD_REQUEST)
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)
        # CCP().send_template_sms(mobile,[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
        send_sms_code.delay(mobile, sms_code)
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile,constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        return Response({"message": "OK"})
