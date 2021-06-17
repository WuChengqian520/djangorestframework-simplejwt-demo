# djangorestframework-simplejwt高级定制教程

[toc]



>  本文为`djangorestframework-simplejwt入门教程`的高级篇，上一篇里面讲述了simplejwt的基本使用，包括安装，添加到项目，验证等。本文将接着上一页的内容继续，不再讲解安装配置等内容。如果没有特殊的需求的话，上一章的内容以及足够完成jwt验证了，但是在实际企业里面，总会有一些定制的需求，因此，本文主要简单介绍如何定制响应数据。

## 定制响应数据格式与内容

对于获取Token的接口，simplejwt默认返回的数据仅有`access`和`refresh`两个信息，对于常规的网站来说，有这两个信息已经足够了，通过解析token就可以得到很多信息。但是总会有那么一些时候，需要在响应的数据里面添加字段，比如系统以前是直接将用户信息直接放在响应数据里面的，出于兼容性考虑，响应数据还需要添加一些数据，因此，我们需要定制登录接口。

### 1.编写自定义的序列化类

要想自定义响应数据，就需要修改默认的序列化类`TokenObtainPairSerializer`。编写一个自定义的序列化类，继承自`TokenObtainPairSerializer`，然后重写它的两个方法：

- `get_token`： 生成Token的方法，重写这个方法修改有效荷载`payload`
- `validate`：重写这个方法修改响应数据结构

完整代码如下（`serializers.py`）

```python
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 如果自定义了用户表，那么就要使用这个方法来获取用户模型
# 没有自定义的话可以使用以下方式加载用户模型:
# from django.contrib.auth.models import User
# 不过这种是万能的
User = get_user_model()


# 重写TokenObtainPairSerializer类的部分方法以实现自定义数据响应结构和payload内容
class MyTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        """
        此方法往token的有效负载 payload 里面添加数据
        例如自定义了用户表结构，可以在这里面添加用户邮箱，头像图片地址，性别，年龄等可以公开的信息
        这部分放在token里面是可以被解析的，所以不要放比较私密的信息

        :param user: 用戶信息
        :return: token
        """
        token = super().get_token(user)
        # 添加个人信息
        token['name'] = user.username
        return token

    def validate(self, attrs):
        """
        此方法为响应数据结构处理
        原有的响应数据结构无法满足需求，在这里重写结构如下：
        {
            "refresh": "xxxx.xxxxx.xxxxx",
            "access": "xxxx.xxxx.xxxx",
            "expire": Token有效期截止时间,
            "username": "用户名",
            "email": "邮箱"
        }

        :param attrs: 請求參數
        :return: 响应数据
        """
        # data是个字典
        # 其结构为：{'refresh': '用于刷新token的令牌', 'access': '用于身份验证的Token值'}
        data = super().validate(attrs)

        # 获取Token对象
        refresh = self.get_token(self.user)
        # 令牌到期时间
        data['expire'] = refresh.access_token.payload['exp']  # 有效期
        # 用户名
        data['username'] = self.user.username
        # 邮箱
        data['email'] = self.user.email
        return data

```

### 2. 在视图中使用自定义的序列化类

在`views.py`中编写新的视图实现登陆功能

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import MyTokenSerializer

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
```

最后记得要配置一下`url.py`

```python
from django.urls import path

from .views import LoginView, DemoView

app_name = 'account'
urlpatterns = [
    path('login/', LoginView.as_view()),   # 使用自定义的视图进行登录
]

```



## 后台获取payload中的数据

在生成token的时候，我们往里面添加了一些数据，那么这些数据是可以拿出来用的

编写用于测试的视图，

```python
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
```

然后配置一下url进行测试，得到一下运行结果

```text
请求用户Token为：
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIzOTA2MTk1LCJqdGkiOiJmY2FjNjhhMzk3M2U0Y2Q0OTJkZjQ0YTFlNzc2ODA4MiIsInVzZXJfaWQiOjEsIm5hbWUiOiJhZG1pbiJ9.9Xd7oHIyMPFR1ZwR3RS0Kzwb2TUO_fVHB5ZFTmjtgrY

有效荷载信息：
{'token_type': 'access', 'exp': 1623906195, 'jti': 'fcac68a3973e4cd492df44a1e7768082', 'user_id': 1, 'name': 'admin'}
```



## Web端解析Token获取数据

### 1. js代码直接解析

```js
let token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIyNzEwNTkzLCJqdGkiOiIwYjg0ZjYzODkyNWY0YjE5Yjc1MzE4Njc4YmFhYTU5YiIsInVzZXJfaWQiOjEsIm5hbWUiOiJhZG1pbiJ9.-oSnx9ex__ZDi8-fOAV3tO-yFdCRhufxgEEkCQw8_9M';

// 解析token， 分割token，取出第二段（payload）进行解析
let user = JSON.parse(decodeURIComponent(escape(window.atob(token.split('.')[1]))))
console.log("user", user)
```

效果如下：

![](https://gitee.com/wuchengqian/picgo/raw/master/20210604092150.png)

### 2. npm安装`jsonwebtoken`模块解析

如果项目中使用了npm，那么可以利用npm快速安装一个模块来解析Token

1. 安装模块： `npm install jsonwebtoken`
2. 在js文件中使用`jsonwebtoken`

```javascript
// 引入模块
var jwt = require('jsonwebtoken');
// 要解析的token
let tokenString = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIyNzEwNTkzLCJqdGkiOiIwYjg0ZjYzODkyNWY0YjE5Yjc1MzE4Njc4YmFhYTU5YiIsInVzZXJfaWQiOjEsIm5hbWUiOiJhZG1pbiJ9.-oSnx9ex__ZDi8-fOAV3tO-yFdCRhufxgEEkCQw8_9M'
// 使用decode方法解析token
let token = jwt.decode(tokenString)
console.log(token)
```

最终的效果如下：

![](https://gitee.com/wuchengqian/picgo/raw/master/20210604092030.png)

