from django.urls import path

from .views import LoginView, DemoView

app_name = 'account'
urlpatterns = [
    path('login/', LoginView.as_view()),
    path('test/', DemoView.as_view())
]
