from django.conf.urls import url
from . import views

urlpatterns = [
    # 获取扫码url
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # 扫描后结果回调
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
]