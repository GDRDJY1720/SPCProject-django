# _*_ coding:utf-8 _*_
from rest_framework.pagination import PageNumberPagination


class CommonPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    # max_page_size = 5
    page_query_param = 'page'
