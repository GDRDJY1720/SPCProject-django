# _*_ coding:utf-8 _*_

from rest_framework import serializers
from rest_framework import exceptions
from account import models


class LoginSerialiser(serializers.Serializer):
    phoneNum = serializers.CharField(error_messages={'blank': '不能为空'})
    password = serializers.CharField(error_messages={'blank': '不能为空'})

    def validate_phoneNum(self, value):
        user = models.UserInfo.objects.filter(phonenum=value).first()
        if not user:
            raise exceptions.ValidationError('用户不存在')

        return user


class TokenSerialiser(serializers.ModelSerializer):
    privilege = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = models.UserToken
        fields = ['token', 'privilege', 'user_name', 'end_time']
        # depth = 1

    def get_privilege(self, row):
        return row.user.from_privilege

    def get_user_name(self, row):
        return row.user.username

    def get_end_time(self, row):
        import time
        return round(time.mktime(row.end_time.timetuple()) * 1000)


class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ['username', 'useremail', 'phonenum', 'from_privilege', 'user_id', 'user_secret', 'from_product']
        # depth = 1
