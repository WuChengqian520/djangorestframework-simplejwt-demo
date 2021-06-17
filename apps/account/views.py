from rest_framework import status
from django.http import HttpResponse
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import MyTokenSerializer


User = get_user_model()


# 用于演示后台获取token中payload数据的视图
class DemoView(APIView):

    def get(self, request):
        # 通过request.auth获取用户Token
        print('请求用户Token为：')
        print(request.auth)

        # 通过request.auth.payload可以获取到解析后的payload内容（字典类型）
        print("\n有效荷载信息：")
        print(request.auth.payload)

        return HttpResponse('身份验证通过！', status=status.HTTP_200_OK)


# 自定义的登陆视图
class LoginView(TokenViewBase):

    serializer_class = MyTokenSerializer   # 使用刚刚编写的序列化类

    # post方法对应post请求，登陆时post请求在这里处理
    def post(self, request, *args, **kwargs):
        # 使用刚刚编写时序列化处理登陆验证及数据响应
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ValueError(f'验证失败： {e}')

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
