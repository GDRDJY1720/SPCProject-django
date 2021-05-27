from django.db import models


# Create your models here.


class Task(models.Model):
    fk_device = models.ForeignKey(to='device.Device', on_delete=models.CASCADE)
    task_id = models.CharField(max_length=16, null=True)
    task_info = models.TextField(null=True)
    task_submit_url = models.URLField(null=True)
    task_submit_info = models.CharField(max_length=64, null=True)
