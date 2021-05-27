# _*_ coding:utf-8 _*_

from rest_framework.permissions import BasePermission


class SVIPPermission(BasePermission):
    message = "无管理员权限"

    def has_permission(self, request, view):
        if request.method == 'POST' or request.method == 'DELETE' or request.method == 'PUT':
            if request.user.privilege != 1:
                return False

        return True
