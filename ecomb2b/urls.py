"""ecomb2b URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path
from produtos.views import (login_view,logout_view,
produtos,carrinho_view,generate_PDF,html_pedido,
produtos_sem_imagem_view,upload_img,limpa_cache,users_log)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('colecao-<str:colecao>/', colecao_view),
    # path('colecao-<str:colecao>/categoria-<str:categoria>/', categoria_view),
    # path('colecao-<str:colecao>/categoria-<str:categoria>/subcategoria-<str:subcategoria>/', product_list_view),
    path('', produtos, name='home'),
    path('login/', login_view,name='login'),
    path('accounts/logout/', logout_view), 
    path('carrinho/', carrinho_view),
    path('prods_sem_imagem/', produtos_sem_imagem_view),
    path('carrinho/pedido/', generate_PDF),
    path('carrinho/pedido_teste/', html_pedido),
    path('upload/', upload_img),
    path('limpa_cache/', limpa_cache),
    path('log/', users_log),
]
