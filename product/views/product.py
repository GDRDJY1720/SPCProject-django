# _*_ coding:utf-8 _*_

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from utils.pagination import CommonPagination
from product.utils.serializer import ProductSerializer

from commonTool import ali_api
from product import models


class ProductView(GenericViewSet):
    """
    产品类中，只有list方法有使用，其他的均未使用或者未测试
    """
    queryset = models.Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliProductAPI()

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        # ============================> 与物联网平台数据同步 <=======================================
        dic = self.get_APIRun(APIname='QueryProductList', res=res)
        if res['code'] != 1000:
            return Response(res)

        product_list = dic['Data']['List']['ProductInfo']
        new_product_list = []
        for product in product_list:
            new_product_list.append(product.get('ProductKey'))
            models.Product.objects.update_or_create(productkey=product.get('ProductKey'),
                                                    defaults={
                                                        'productname': product.get('ProductName')
                                                    })

        local_product_list = models.Product.objects.values_list('productkey', flat=True)
        for lo in local_product_list:
            if lo not in new_product_list:
                models.Product.objects.filter(productkey=lo).delete()
        # ============================> END <=======================================

        if request.user.from_privilege == 1:
            tmp_list = models.Product.objects.exclude(id=5).order_by('-id')
        else:
            tmp_list = request.user.from_product.order_by('-id').all()

        pager = self.paginate_queryset(tmp_list)
        ser = self.get_serializer(instance=pager, many=True, context={'request': request})
        res['data'] = ser.data
        return Response(res)

    def create(self, request, *args, **kwargs):
        """
        未测试
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        res = {'code': 1000, 'msg': '', 'data': []}

        params = {
            'NodeType': request.data.get('NodeType'),
            'ProductName': request.data.get('ProductName'),
            'DataFormat': request.data.get('DataFormat'),
            'AliyunCommodityCode': request.data.get('AliyunCommodityCode'),
            'ProtocolType': request.data.get('ProtocolType'),
            'NetType': request.data.get('NetType'),
            'AuthType': request.data.get('AuthType')
        }

        dic = self.get_APIRun(APIname='CreateProduct', res=res, **params)
        if res['code'] != 1000:
            return Response(res)

        data = dic.get('Data')

        models.Product.objects.create(productkey=data.get('ProductKey'), productname=data.get('ProductName'))

        return Response(res)

    def list_limit(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        pk = kwargs.get('pk', None)

        product = models.Product.objects.filter(id=pk).first()

        if not product:
            res['code'] = 1014
            res['msg'] = '没有找到产品'
            return Response(res)

        dic = self.get_APIRun(APIname='QueryProduct', res=res, ProductKey=product.productkey)
        if res['code'] != 1000:
            return Response(res)

        res['data'] = self.get_serializer(instance=product, context={'request': request, 'data': dic['Data']}).data
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        pk = kwargs.get('pk', None)

        product = models.Product.objects.filter(id=pk).first()

        dic = self.get_APIRun(APIname='DeleteProduct', res=res, ProductKey=product.productkey)
        if res['code'] != 1000:
            return Response(res)

        product.delete()

        return Response(res)

    def update(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        pk = kwargs.get('pk', None)
        product_new_name = request.data.get('ProductName', None)
        description = request.data.get('Description', '')

        product = models.Product.objects.filter(id=pk).first()

        dic = self.get_APIRun(APIname='UpdateProduct', res=res, ProductName=product_new_name,
                              ProductKey=product.productkey, Description=description)
        if res['code'] != 1000:
            return Response(res)

        return Response(res)

    def partial_update(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        return Response(res)

    def get_APIRun(self, res, APIname, **kwargs):
        try:
            dic = self.Api.APIRun(APIname, **kwargs)
        except Exception as e:
            res['code'] = 1003
            res['msg'] = '调用 APIRun：%s 出错' % APIname
            res['data'] = e
            return res

        if not dic.get('Success'):
            if not dic.get('ErrorMessage') == 'The specified product does not exist.':
                res['code'] = 1004
                res['msg'] = '调用 APIRun：%s 失败' % APIname
                res['data'] = dic
                return res

        return dic
