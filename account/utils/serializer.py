# _*_ coding:utf-8 _*_

import re

from rest_framework import serializers
from rest_framework import exceptions
from account import models


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(error_messages={'blank': '不能为空'})
    password = serializers.CharField(error_messages={'blank': '不能为空'})

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @staticmethod
    def validate_username(value):
        params = {}
        phone = re.match('^[1-9]{11}$', value)
        if phone is not None:
            params['phone_num'] = value
        else:
            email = re.match('^[a-zA-Z0-9]+([-_.][a-zA-Z0-9]+)*@[a-zA-Z0-9]+([-_.][a-zA-Z0-9]+)*\.[a-z]{2,}$', value)
            if email is not None:
                params['user_email'] = value
            else:
                params['username'] = value

        user = models.UserInfo.objects.filter(**params).first()

        if not user:
            raise exceptions.ValidationError('用户不存在，请检查用户信息是否输入正确')

        return user


class TokenSerializer(serializers.ModelSerializer):
    privilege = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = models.UserToken
        fields = ['token', 'privilege', 'user_name', 'end_time', 'customer']
        # depth = 1

    def get_privilege(self, row):
        return row.fk_user.privilege

    def get_user_name(self, row):
        return row.fk_user.username

    def get_end_time(self, row):
        import time
        return round(time.mktime(row.end_time.timetuple()) * 1000)

    def get_customer(self, row):
        if row.fk_user.fk_customer is None:
            return 100
        return 1


class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ['id', 'username', 'user_email', 'phone_num', 'privilege', 'user_id', 'user_secret', 'fk_product']
        # depth = 1
