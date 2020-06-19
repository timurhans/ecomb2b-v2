from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core.cache import cache
from .ondas import (Produto,Estoque,produtos_col_cat,
produtos_col_subcat,cats_subcats,get_produto,prods_sem_imagem)
from .forms import LoginForm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
# from django_xhtml2pdf.utils import generate_pdf
from xhtml2pdf import pisa
from django.template import Context
from django.template.loader import get_template
import time
from datetime import date
import re
from params.models import (ColecaoB2b,ColecaoErp,Banner)
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os, zipfile
import glob
import shutil

# Create your views here.

class ItemPedido():
    pass

def adciona_carrinho(request):

    tabela=request.user.first_name
    session = request.COOKIES.get('sessionid')
    pedido = Produto()

    produto = request.POST.get('produto')
    pedido.produto = get_produto(produto,tabela)
    itens = []
    er_cor = r'@(.+)@'
    qtd_tot = 0
    for key, value in request.POST.items():
        #checa se info confere com padrao cor
        cor = re.match(er_cor,key)
        if cor is not None:
            qtds = request.POST.getlist(key)
            qtds = [int(q) for q  in qtds ]
            qtd_tot = qtd_tot + sum(qtds)
            print(qtds)
            #checa se itens nao estao zerados
            if all(i == 0 for i in qtds):
                continue
            cor = cor.group(1)
            item = ItemPedido()
            item.cor = cor
            item.qtds = qtds
            item.qtd_item = sum(qtds)
            item.valor_item = round(item.qtd_item*pedido.produto.preco,2)
            itens.append(item)
    pedido.qtd_tot = qtd_tot
    pedido.valor_tot = round(qtd_tot*pedido.produto.preco,2)
    if len(itens)>0:
        pedido.itens = itens #qtd pedido

        if cache.get(session) is None:
            pedidos = []
            pedidos.append(pedido)   
            cache.set(session, pedidos, 60*60)
        else:
            pedidos = cache.get(session)
            if any(x.produto.produto == pedido.produto.produto for x in pedidos):
                pedidos = [pedido if x.produto.produto == pedido.produto.produto else x for x in pedidos]
            else:
                pedidos.append(pedido)
            cache.set(session, pedidos, 60*60)

def produtos(request):

    colecoes = list(ColecaoB2b.objects.filter(active=True).order_by('ordem').values_list('title', flat=True).distinct())
    banners = Banner.objects.all().order_by('ordem')

    page_size = 12

    session = request.COOKIES.get('sessionid')
    lista_carrinho = cache.get(session)
    try:
        qtd_carrinho = len(lista_carrinho)
    except:
        qtd_carrinho = 0

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
        qtd_pags = paginator.num_pages
        qtd_prods = len(queryset)
        if qtd_prods>page_size:
            is_paginated = True
        else:
            is_paginated = False

        cats = cats_subcats()
        context = {
        'object_list' : queryset,
        'categorias' : cats,
        'colecoes' : colecoes,
        'page_obj': page_obj,
        'is_paginated' : is_paginated,
        'selected_col' : col,
        'selected_cat' : cat,
        'selected_subcat' : subcat,
        'qtd_carrinho' : qtd_carrinho,
        'qtd_pags' : qtd_pags,
        'qtd_prods' : qtd_prods,
        'banners' : banners
        }
        return render(request,"produtos/produtos.html",context)
    else:
        print(request)
        return redirect('/login')


def carrinho_view(request):

    colecoes = list(ColecaoB2b.objects.filter(active=True).order_by('ordem').values_list('title', flat=True).distinct())

    session = request.COOKIES.get('sessionid')
    lista_carrinho = cache.get(session)
    try:
        qtd_carrinho = len(lista_carrinho)
    except:
        qtd_carrinho = 0

    if request.user.is_authenticated:

        if request.method == 'POST':

            if request.POST.get('altera') is not None:
                adciona_carrinho(request)
                return HttpResponse('<script>history.back();</script>')
            elif request.POST.get('remove') is not None:
                #exclusao carrinho
                produto = request.POST.get('produto')
                print(produto)
                pedidos = cache.get(session)
                pedidos = list(filter(lambda x: x.produto.produto != produto, pedidos))
                cache.set(session, pedidos, 60*60)
            elif request.POST.get('processa') is not None:
                #processa pedido
                observacoes = request.POST.get('obs_pedido')
                return generate_PDF(request,observacoes)
        try:
            queryset = cache.get(session)
            valor_tot = round(sum([x.valor_tot for x in queryset]),2)
            qtd_tot = sum([x.qtd_tot for x in queryset])
        except:
            queryset = []
            valor_tot = 0
            qtd_tot = 0

        cats = cats_subcats()
        context = {
        'object_list' : queryset,
        'categorias' : cats,
        'colecoes' : colecoes,
        'valor_tot' : valor_tot,
        'qtd_tot' : qtd_tot,
        'qtd_carrinho' : qtd_carrinho
        }
        return render(request,"produtos/carrinho.html",context)
    else:
        print(request)
        return redirect('/login')



def generate_PDF(request,observacoes):

    session = request.COOKIES.get('sessionid')
    queryset = cache.get(session)

    valor_total_pedido = round(sum([x.valor_tot for x in queryset]),2)
    qtd_total_pedido = sum([x.qtd_tot for x in queryset])
    today = date.today().strftime("%d/%m/%Y")
    data = {'object_list' : queryset,
            'data' : today,
            'valor_total' : valor_total_pedido,
            'qtd_total' : qtd_total_pedido,
            'observacoes' : observacoes}

    template = get_template('produtos/pedido.html')
    html  = template.render(data)

    file_path = 'static/pdfs/'+session
    file = open(file_path, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()      
    return HttpResponse(pdf, 'application/pdf')


def html_pedido(request):

    session = request.COOKIES.get('sessionid')
    queryset = cache.get(session)
    data = {'object_list' : queryset}

    return render(request,"produtos/pedido.html",data)

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

def produtos_sem_imagem_view(request):

    if request.user.is_authenticated:
        prods = prods_sem_imagem()
        context = {
            'produtos' : prods,
            'qtd' : len(prods)
        }
        return render(request,"produtos/prods_sem_img.html",context)
    else:
        return redirect('/login')

def upload_img(request):
    if request.user.is_authenticated:
        session = request.COOKIES.get('sessionid')
        dir_imports = 'static/imports/'
        dir_imports_session = dir_imports + session+'/' #pasta para sessao para nao ter conflito na importacao
        dir_imgs = 'static/imgs/'
        if request.method == 'POST':
            try:
                myfile = request.FILES['myfile']
            except:
                return render(request, 'produtos/upload.html')
            fs = FileSystemStorage() 
            filename = fs.save(dir_imports+myfile.name, myfile) # salva arquivo
            zip_ref = zipfile.ZipFile(filename)
            zip_ref.extractall(dir_imports_session) # extrai para pasta da sessao
            zip_ref.close()
            os.remove(filename) #exlui arquivo zip
            fotos = glob.glob(dir_imports_session+'**/*.jpg', recursive=True) # busca todos os arquivos jpg recursivamente
            cont_novas = 0
            cont_atualiz = 0
            for f in fotos:
                
                novo_path = dir_imgs+os.path.basename(f)
                if glob.glob(novo_path):
                    cont_atualiz = cont_atualiz+1
                else:
                    cont_novas = cont_novas+1
                print(novo_path)
                os.replace(f, novo_path) # move para a pasta imgs

            shutil.rmtree(dir_imports_session) #exclui pasta sessao
            return render(request, 'produtos/upload.html', {
                'novas': cont_novas,
                'atualizadas' : cont_atualiz
            })
        return render(request, 'produtos/upload.html')
    else:
        return redirect('/login')    

def limpa_cache(request):
    if request.user.is_authenticated:
        cache.delete("dados")
        return redirect('home') 
    else:
        return redirect('/login')    