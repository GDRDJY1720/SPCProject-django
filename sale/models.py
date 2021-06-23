from django.db import models


# Create your models here.


class SalesInfo(models.Model):
    customer_code = models.CharField("客户代码", max_length=64)
    company_name = models.CharField("公司名称", max_length=64, null=True)
    # 销售订单中只到日，没有具体的时间
    sell_time = models.DateField("销售时间", null=True)
    sell_code = models.CharField("销售订单号", max_length=64, null=True)
    sell_site = models.CharField("销售地点", max_length=128, null=True)
