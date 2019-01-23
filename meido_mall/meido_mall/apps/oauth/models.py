from django.db import models

# Create your models here.
from meido_mall.utils.models import BaseModel
from users.models import User

class QQAuthUser(BaseModel):
    user = models.ForeignKey(User, verbose_name='openid关联的用户',
                             on_delete=models.CASCADE)
    openid = models.CharField(verbose_name='QQ用户唯一标识', db_index=True,
                              max_length=64)

    class Meta:
        db_table = 'tb_qq_auth'
        verbose_name = 'QQ登录用户2数据'
        verbose_name_plural = verbose_name