from django.db import models


# Create your models here.

class UserInfo(models.Model):
    privilege_choices = (
        (1, '管理员'),
        (2, '员工'),
        (3, '客户')
    )

    username = models.CharField(max_length=15, unique=True)
    # 密码加密是username+password+phonenum
    # 后续需要考虑忘记密码的时候如何找回密码
    password = models.CharField(max_length=32)
    useremail = models.EmailField(null=True, unique=True)
    phonenum = models.CharField(max_length=11, unique=True)
    # userphoto = models.ImageField(upload_to='img', blank=True, null=True)
    from_privilege = models.IntegerField(choices=privilege_choices)
    from_product = models.ManyToManyField(to='product.Product')
    # user_id和user_secret主要是在调用api的时候使用，所以生成的时候是api+username+时间生成user_id
    # user_id+password+时间生成user_secret
    user_id = models.CharField(max_length=64)
    user_secret = models.CharField(max_length=64)


class UserToken(models.Model):
    user = models.OneToOneField(to='UserInfo', on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
