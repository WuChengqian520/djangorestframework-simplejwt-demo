# djangorestframework-simplejwt入门教程示例

[toc]

## 说明
此项目为 `djangorestframework-simplejwt` 插件的入门示例代码

## 环境说明

| 环境                          | 版本   |
| ----------------------------- | ------ |
| Python                        | 3.6.8  |
| Django                        | 3.1    |
| djangorestframework （DRF）   | 3.12.4 |
| djangorestframework-simplejwt | 4.4.0  |

**注意：是`djangorestframework-simplejwt`不是`djangorestframework-jwt`，后者已停止维护。**

> Tips: 
>
> `Python 3.6 `默认安装`djangorestframework-simplejwt`最高版本是`4.4.0`， 该版本有一个bug， 获取token时会报错：
>
> ```text
> Traceback (most recent call last):
>   File "D:\myhub\simple_JWT_demo\venv\lib\site-packages\django\core\handlers\exception.py", line 47, in inner
>   
> ...
> 
>   File "D:\myhub\simple_JWT_demo\venv\lib\site-packages\rest_framework_simplejwt\tokens.py", line 82, in __str__
>     return token_backend.encode(self.payload)
>   File "D:\myhub\simple_JWT_demo\venv\lib\site-packages\rest_framework_simplejwt\backends.py", line 43, in encode
>     return token.decode('utf-8')
> AttributeError: 'str' object has no attribute 'decode'
> ```
>
> 这里解决办法是修改`djangorestframework-simplejwt`的源文件，及上面报错信息的倒数第三行（`rest_framework_simplejwt\backends.py` 文件`第 43行`）， 将 `return token.decode('utf-8')`改为：``return token`
>
> `Python 3.7+版本`默认安装`4.6.0+`以上版本，已修复此问题


> 约定：
>
> - `djangorestframework` 本文后续统一称为： `DRF`
>
> - `djangorestframework-simplejwt`本文后续统一称为`simplejwt`

## 安装

`simplejwt`是 `DRF`的插件，所以安装之前需要先安装`DRF`

```shell
pip install djangorestframework
pip install markdown
pip install django-filter

# 下面安装 simplejwt
pip install  djangorestframework-simplejwt
```



## 配置settings.py

### 在 `INSTALLED_APPS` 中注册

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自己的应用
	...
    'rest_framework',  # 注册DRF应用
]
```

### 配置 `DRF`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 使用rest_framework_simplejwt验证身份
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'    # 默认权限为验证用户
    ],
}
```

### 配置 `simplejwt`

```python
# simplejwt配置， 需要导入datetime模块
SIMPLE_JWT = {
    # token有效时长
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=30),
    # token刷新后的有效时间
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
}
```



## 编写路由 urls.py

这里直接编写项目下的根路由文件

```python
from django.contrib import admin
from django.urls import path, include

# 导入 simplejwt 提供的几个验证视图类
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # Django 后台
    path('admin/', admin.site.urls),
    # DRF 提供的一系列身份认证的接口，用于在页面中认证身份，详情查阅DRF文档
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 获取Token的接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 刷新Token有效期的接口
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 验证Token的有效性
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
```



## 创建数据库并添加用户

1. 执行模型变更命令初始化数据库

```shell
python manage.py migrate
```

2. 添加用户，直接生成超级用户

```shell
python manage.py createsuperuser
```

然后按照步骤输入邮箱用户名和密码就可以了

## 运行项目并查看效果

浏览器打开`http://127.0.0.1:8000/`应该就能看到URL提示了，下面进入刚刚配置的url查看一下效果

### 获取Token

进入 `http://127.0.0.1:8000/api/token/`， 一切正常的话应该会看到`DRF`提供的页面，提示`GET方法不被允许`，并且下面有用户名和密码的输入框。

![image-20210514154143145](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20210514154143145.png)

在输入库中输入刚刚创建的用户信息就能得到系统返回的信息了。返回的信息包括`refresh`和`access`两个字段。其中`refresh`是用于`刷新token`的（每个Token都是有时间限制的，过了时间就生效了），`access`是用于后续的请求时验证身份的。

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514160410.png)

### 验证Token

进入`http://127.0.0.1:8000/api/token/verify/`, 下面提示输入`Token`， 输入刚刚过去到的`access`的值，验证成功。注意，验证成功没有提示信息反悔，只有一个200的响应码

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514155255.png)

如果验证失败，则响应码为401，且下方有提示信息

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514155503.png)

### 刷新Token

进入 `http://127.0.0.1:8000/api/refresh/`，下面提示填写`refresh`，在里面填写上面获取到的`refresh`值，如果填写的正确，则会获取到新的`Token`，否则会提示验证失败

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514155924.png)

## Postman请求方式

上面的操作都是在`DRF`提供的页面里面进行的，实际使用的时候都是Ajax请求，下面讲解使用`Postman`进行请求的方法，以`获取Token`和自定义的视图

### 获取Token

在Postman中正常填写请求信息即可， 获取Token、刷新Token和验证Token都是直接填写即可

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514161053.png)

### 自定义的视图

上面的三个Token相关的接口是插件提供的，内部已经做了配置，免身份认证，但是我们自己的接口是需要做身份校验的。我们先创建一个自定义的视图，然后在路由中注册。为了便于演示，这里直接在`urls.py`中创建视图，之后，我们完整的`urls.py`文件如下

```python
from django.contrib import admin
from django.urls import path, include

from rest_framework.views import APIView, Response
# 导入 simplejwt 提供的几个验证视图类
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


# 创建一个自定义的视图，仅实现get方法做测试
class IndexView(APIView):
    def get(self, request):
        return Response('This is Index Page!', status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    # DRF 提供的一系列身份认证的接口，用于在页面中认证身份，详情查阅DRF文档
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 获取Token的接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 刷新Token有效期的接口
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 验证Token的有效性
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # 自定义视图
    path('index/', IndexView.as_view(), name='index')
]
```

>这里为了省事将视图写在了`urls.py`里面，实际开发请单独建立`views.py`，保持良好的代码风格

此时，我们使用Postman执行`GET`请求访问自定义接口为得到提示信息， 这就是在提示我们需要传递`Token`给后台认证了

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514163111.png)

`simplejwt`的身份认证方式为：在请求的`Headers`里面里面添加设置参数，名称为：`Authorization`,  值是一个固定组成的字符串： `Bearer` +` 空格` + `access`， 例如：`Bearer [token值]`。 正确的效果如下

![](https://gitee.com/wuchengqian/picgo/raw/master/20210514164617.png)

至此，已经完成`djangorestframework-simplejwt`入门

定制token有效载体内容，响应数据格式，请切换分支