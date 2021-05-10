from django.db import models


# Create your models here.


class Task(models.Model):
    fk_device = models.ForeignKey(to='device.Device', on_delete=models.CASCADE)
    taskId = models.CharField(max_length=16, null=True)
    taskInfo = models.TextField(null=True)
    taskSubmitUrl = models.URLField(null=True)
    taskSubmitInfo = models.CharField(max_length=64, null=True)
