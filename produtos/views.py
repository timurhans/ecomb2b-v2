from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core.cache import cache
from .ondas import (Produto,Estoque,produtos_col_cat,
produtos_col_subcat,cats_subcats)
from .forms import LoginForm
import time
import re
import ast

COLECOES = ['2001','Saldos']
# Create your views here.

class ItemPedido():
    pass

def adciona_carrinho(request):
    session = request.COOKIES.get('sessionid')

    pedido = Produto()
    pedido.produto = request.POST.get('produto')
    pedido.url = request.POST.get('url')
    pedido.composicao = request.POST.get('composicao')
    pedido.sortido = request.POST.get('sortido')
    pedido.preco = request.POST.get('preco')
    tams = request.POST.get('tams')
    tams = ast.literal_eval(tams)
    pedido.tams = tams
    print(request.POST.get('produto'))
    print(request.POST.get('tams'))
    itens = []
    er_cor = r'@(.+)@'
    for key, value in request.POST.items():
        #checa se info confere com padrao cor
        cor = re.match(er_cor,key)
        if cor is not None:
            qtds = request.POST.getlist(key)
            qtds = [int(q) for q  in qtds ]
            print(qtds)
            #checa se itens nao estao zerados
            if all(i == 0 for i in qtds):
                continue
            cor = cor.group(1)
            item = ItemPedido()
            item.cor = cor
            item.qtds = qtds
            itens.append(item)
    
    if len(itens)>0:
        pedido.estoque = itens

        if cache.get(session) is None:
            pedidos = []
            pedidos.append(pedido)   
            cache.set(session, pedidos, 60*60)
        else:
            pedidos = cache.get(session)
            pedidos.append(pedido)
            cache.set(session, pedidos, 60*60)

def product_list_view_drop(request):

    page_size = 12

    print(request.COOKIES)
    session = request.COOKIES.get('sessionid')
    print(cache.get(session))

    if request.user.is_authenticated:

        if request.method == 'POST':
            adciona_carrinho(request)

            return HttpResponse('<script>history.back();</script>')


        try:
            col = request.GET['colecao']
            cat = request.GET['categoria']
            subcat = request.GET['subcategoria']
            queryset = produtos_col_subcat(tabela=request.user.first_name,
            colecao=col,categoria=cat,subcategoria=subcat)
        except:
            subcat = ''
            try:
                col = request.GET['colecao']
                cat = request.GET['categoria']
                queryset = produtos_col_cat(tabela=request.user.first_name,
                    colecao=col,categoria=cat)
            except:
                col = ''
                cat = ''
                queryset =[]
                
        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if len(queryset)>page_size:
            is_paginated = True
        else:
            is_paginated = False

        cats = cats_subcats()
        context = {
        'object_list' : queryset,
        'categorias' : cats,
        'colecoes' : COLECOES,
        'page_obj': page_obj,
        'is_paginated' : is_paginated,
        'selected_col' : col,
        'selected_cat' : cat,
        'selected_subcat' : subcat
        }
        return render(request,"produtos/lista_prods_form.html",context)
    else:
        print(request)
        return redirect('/login')


def carrinho_view(request):


    page_size = 12

    print(request.COOKIES)
    session = request.COOKIES.get('sessionid')
    print(cache.get(session))

    if request.user.is_authenticated:

        if request.method == 'POST':
            produto = request.POST.get('produto')
            pedidos = cache.get(session)
            pedidos = list(filter(lambda x: x.produto != produto, pedidos))
            cache.set(session, pedidos, 60*60)

        queryset = cache.get(session)

        cats = cats_subcats()
        context = {
        'object_list' : queryset,
        'categorias' : cats,
        'colecoes' : COLECOES
        }
        return render(request,"produtos/carrinho.html",context)
    else:
        print(request)
        return redirect('/login')


def login_view(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            password = form.cleaned_data['password']
            try:
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('home')
            except:
                form = LoginForm()
                context = {
                    'form' : form,
                    'erro_login' : 'erro'
                }
                return render(request,"produtos/login.html",context)

    else:
        form = LoginForm()
        context = {
            'form' : form
        }

        return render(request,"produtos/login.html",context)




def logout_view(request):

    logout(request)
    return redirect('home')

