from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core.cache import cache
from .ondas import (Produto,Estoque,produtos_col_cat,
produtos_col_subcat,cats_subcats)
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
    pedido.preco = round(float(request.POST.get('preco')),2)
    tams = request.POST.get('tams')
    tams = ast.literal_eval(tams)
    pedido.tams = tams
    print(request.POST.get('produto'))
    print(request.POST.get('tams'))
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
            item.valor_item = round(item.qtd_item*pedido.preco,2)
            itens.append(item)
    pedido.qtd_tot = qtd_tot
    pedido.valor_tot = round(qtd_tot*pedido.preco,2)
    if len(itens)>0:
        pedido.itens = itens #qtd pedido

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

    session = request.COOKIES.get('sessionid')
    lista_carrinho = cache.get(session)
    qtd_carrinho = len(lista_carrinho)

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
        'colecoes' : COLECOES,
        'page_obj': page_obj,
        'is_paginated' : is_paginated,
        'selected_col' : col,
        'selected_cat' : cat,
        'selected_subcat' : subcat,
        'qtd_carrinho' : qtd_carrinho,
        'qtd_pags' : qtd_pags,
        'qtd_prods' : qtd_prods
        }
        return render(request,"produtos/lista_prods_pop.html",context)
    else:
        print(request)
        return redirect('/login')


def carrinho_view(request):


    session = request.COOKIES.get('sessionid')
    lista_carrinho = cache.get(session)
    qtd_carrinho = len(lista_carrinho)

    if request.user.is_authenticated:

        if request.method == 'POST':

            if request.POST.get('processa') is None:
                #exclusao carrinho
                produto = request.POST.get('produto')
                pedidos = cache.get(session)
                pedidos = list(filter(lambda x: x.produto != produto, pedidos))
                cache.set(session, pedidos, 60*60)
            else:
                #processa pedido
                print(request.POST.get('processa'))
                return redirect('pedido/')
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
        'colecoes' : COLECOES,
        'valor_tot' : valor_tot,
        'qtd_tot' : qtd_tot,
        'qtd_carrinho' : qtd_carrinho
        }
        return render(request,"produtos/carrinho.html",context)
    else:
        print(request)
        return redirect('/login')


def pedido_view(request):
    
    session = request.COOKIES.get('sessionid')
    queryset = cache.get(session)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    c = canvas.Canvas(response,(420,594))



    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.    
    # Close the PDF object cleanly, and we're done.

    marg = 32
    for produto in queryset:
        c.setFont("Courier", 8)
        c.drawString(0,(594-marg),produto.produto)
        marg = marg+20
        cabecalho = ['COR']
        for t in produto.tams:
            cabecalho.append(t)
            cabecalho = [cabecalho]
        for ped in produto.estoque:
            linha = []
            linha.append(ped.cor)
            for q in ped.qtds:
                linha.append(q)
            cabecalho.append(linha)
        # marg = marg+10
        tabela_disp = cabecalho
        colunas = [15]
        
        # colunas_2 = [10]*(len(cabecalho[0])-3)

        # for col in colunas_2:
        #     colunas.append(col)
        colunas = [18]*len(cabecalho)
        tam_tabela = len(tabela_disp)
        linhas = [9]*tam_tabela

        marg = marg + sum(linhas)/2
        tabela_disp = Table(tabela_disp,colWidths=colunas, rowHeights=linhas,)
        tabela_disp.setStyle(TableStyle([
                ('TEXTCOLOR',(0,0),(-1,-1),colors.black),                       
                ('FONTSIZE', (0,0), (-1,-1), 6),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('INNERGRID', (0,0), (-1,-1), 0.1, colors.black),
                ('BOX', (0,0), (-1,-1), 0.1, colors.black)
                ]))
        tabela_disp.wrapOn(c, 0, (594-marg))
        tabela_disp.drawOn(c, 20, (594-marg))
        marg = marg + sum(linhas)/2
        
    c.showPage()
    c.save()
    return response

def generate_PDF(request):

    session = request.COOKIES.get('sessionid')
    queryset = cache.get(session)

    valor_total_pedido = round(sum([x.valor_tot for x in queryset]),2)
    qtd_total_pedido = sum([x.qtd_tot for x in queryset])
    today = date.today().strftime("%d/%m/%Y")
    data = {'object_list' : queryset,
            'data' : today,
            'valor_total' : valor_total_pedido,
            'qtd_total' : qtd_total_pedido}

    template = get_template('produtos/pedido.html')
    html  = template.render(data)

    file = open('static/test.pdf', "w+b")
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

