from django.db import models


# Create your models here.

class UserInfo(models.Model):
    privilege_choices = (
        (1, '管理员'),
        (2, '生产部'),
        (3, '销售财务部'),
        (99, '其他部门')
    )

    username = models.CharField(max_length=15)
    # 密码加密是username+password+phone_num
    # 后续需要考虑忘记密码的时候如何找回密码
    password = models.CharField(max_length=32)
    user_email = models.EmailField(null=True, unique=True)
    phone_num = models.CharField(max_length=11, unique=True)
    # userphoto = models.ImageField(upload_to='img', blank=True, null=True)
    privilege = models.IntegerField(choices=privilege_choices)
    # 与客户表链接，客户表应该与销售信息表中的用户代码相关联，目前是模拟数据，不为Nono就为用户
    fk_customer = models.IntegerField(null=True)
    fk_product = models.ManyToManyField(to='product.Product')
    # user_id和user_secret主要是在调用api的时候使用，所以生成的时候是api+username+时间生成user_id
    # user_id+password+时间生成user_secret
    user_id = models.CharField(max_length=64)
    user_secret = models.CharField(max_length=64)


class UserToken(models.Model):
    fk_user = models.OneToOneField(to='UserInfo', on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class LoginLog(models.Model):
    fk_user = models.ForeignKey(to='UserInfo', on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField()

