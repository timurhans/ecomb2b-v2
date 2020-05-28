from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from .ondas import (Produto,Estoque,produtos_col_cat,
produtos_col_subcat,cats_subcats)
from .forms import LoginForm
import time

COLECOES = ['2001','Saldos']
# Create your views here.


def product_list_view_drop(request):

    page_size = 12

    if request.user.is_authenticated:



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
        return render(request,"produtos/lista_prods_drop.html",context)
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

