# _*_ coding:utf-8 _*_

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from utils.pagination import CommonPagination
from api.utils import serializers
from product import models as Pmodels


class QueryProductListView(GenericAPIView):
    serializer_class = serializers.QueryProductListSerializer
    pagination_class = CommonPagination

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        if request.user.from_privilege == 1:
            product_list = Pmodels.Product.objects.order_by('id').all()
        else:
            product_list = request.user.from_product.all().order_by('id')

        pager = self.paginate_queryset(product_list)
        ser = self.get_serializer(instance=pager, many=True)

        res['data'] = ser.data
        return Response(res)
