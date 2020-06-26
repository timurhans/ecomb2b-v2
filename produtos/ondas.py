import pandas as pd
import pyodbc
from django.core.cache import cache
import glob
from params.models import (ColecaoErp)
from django.contrib.auth.models import User

DRIVER = '{ODBC Driver 17 for SQL Server}'

class Produto:
    pass

class Estoque:
    pass

def lista_sql(lista):
    lista_sql = '(\''
    i = 0
    for l in lista:
        if i>0:
            lista_sql = lista_sql+',\''
        lista_sql = lista_sql+l+'\''
        i = i+1
    lista_sql = lista_sql+')'
    return lista_sql


def produtos_disp():

    server = '192.168.2.11'
    db = 'ondas800'
    user = 'sa'
    pwd = 'p$3dasony' 
    conn = pyodbc.connect('DRIVER=' + DRIVER + ';SERVER=' + server + ';DATABASE=' + db + ';UID=' + user + ';PWD=' + pwd)

    #seleciona somente solecoes ERP de colecoes B2B ativas
    cols_erp = ColecaoErp.objects.filter(colecaoB2b__active=True).values_list('codigo', flat=True).distinct()
    cols_erp = lista_sql(cols_erp)

    #seleciona somente tabelas distintas que estao cadastradas nos usuarios
    tabelas = User.objects.all().values_list('first_name', flat=True).distinct()
    tabelas = lista_sql(tabelas)
    
    
    query = """
        select
        --atributos produto
        p.PRODUTO,ep.COR_PRODUTO,p.SORTIMENTO_COR,cb.DESC_COR,mc.DESC_COMPOSICAO,
        p.COLECAO,pc.CATEGORIA_PRODUTO,psc.SUBCATEGORIA_PRODUTO,pp.CODIGO_TAB_PRECO,
        pp.PRECO1,p.GRADE,pt.TAMANHOS_DIGITADOS,pt.TAMANHO_1,pt.TAMANHO_2,pt.TAMANHO_3,
        pt.TAMANHO_4,pt.TAMANHO_5,pt.TAMANHO_6,pt.TAMANHO_7,pt.TAMANHO_8,
        pt.TAMANHO_9,pt.TAMANHO_10,pt.TAMANHO_11,pt.TAMANHO_12,
        --estoques
        ep.ES1,ep.ES2,ep.ES3,ep.ES4,ep.ES5,ep.ES6,ep.ES7,ep.ES8,ep.ES9,ep.ES10,ep.ES11,ep.ES12,
        --vendas-
        SUM(vp.VE1) as VE1,sum(vp.VE2) as VE2,
        SUM(vp.VE3) as VE3,SUM(vp.VE4) as VE4,SUM(vp.VE5) as VE5,SUM(vp.VE6) as VE6,
        SUM(vp.VE7) as VE7,SUM(vp.VE8) as VE8,SUM(vp.VE9) as VE9,SUM(vp.VE10) as VE10,
        SUM(vp.VE11) as VE11,SUM(vp.VE12) as VE12
        from 
        ESTOQUE_PRODUTOS ep left join PRODUTOS p on p.PRODUTO = ep.PRODUTO
        left join produtos_tamanhos pt on p.GRADE=pt.GRADE
        left join PRODUTOS_PRECOS pp on p.PRODUTO=pp.PRODUTO and pp.CODIGO_TAB_PRECO in %s
        left join PRODUTOS_CATEGORIA pc on p.COD_CATEGORIA=pc.COD_CATEGORIA
        left join PRODUTOS_SUBCATEGORIA psc on p.COD_SUBCATEGORIA=psc.COD_SUBCATEGORIA and p.COD_CATEGORIA=psc.COD_CATEGORIA
        left join MATERIAIS_COMPOSICAO mc on mc.COMPOSICAO=p.COMPOSICAO
        left join VENDAS_PRODUTO vp on ep.PRODUTO=vp.PRODUTO and vp.COR_PRODUTO=ep.COR_PRODUTO
        left join CORES_BASICAS cb on cb.COR=ep.COR_PRODUTO
        where 
        ep.ESTOQUE>0 and ep.FILIAL='ONDAS' and p.COLECAO in %s
        group by 
        p.PRODUTO,ep.COR_PRODUTO,p.SORTIMENTO_COR,cb.DESC_COR,mc.DESC_COMPOSICAO,
        p.COLECAO,pc.CATEGORIA_PRODUTO,psc.SUBCATEGORIA_PRODUTO,pp.CODIGO_TAB_PRECO,
        pp.PRECO1,p.GRADE,pt.TAMANHOS_DIGITADOS,pt.TAMANHO_1,pt.TAMANHO_2,pt.TAMANHO_3,
        pt.TAMANHO_4,pt.TAMANHO_5,pt.TAMANHO_6,pt.TAMANHO_7,pt.TAMANHO_8,
        pt.TAMANHO_9,pt.TAMANHO_10,pt.TAMANHO_11,pt.TAMANHO_12,
        ep.ES1,ep.ES2,ep.ES3,ep.ES4,ep.ES5,ep.ES6,ep.ES7,ep.ES8,ep.ES9,ep.ES10,ep.ES11,ep.ES12
        order by pp.CODIGO_TAB_PRECO,p.PRODUTO,ep.COR_PRODUTO
    """%(tabelas,cols_erp)

    prods = pd.read_sql(query,conn)
    
    prods['PRODUTO'] = prods['PRODUTO'].str.strip()
    prods['COR_PRODUTO'] = prods['COR_PRODUTO'].str.strip()
    prods['DESC_COR'] = prods['DESC_COR'].str.strip()
    prods['DESC_COMPOSICAO'] = prods['DESC_COMPOSICAO'].str.strip()
    prods['COLECAO'] = prods['COLECAO'].str.strip()
    prods['CATEGORIA_PRODUTO'] = prods['CATEGORIA_PRODUTO'].str.strip()
    prods['SUBCATEGORIA_PRODUTO'] = prods['SUBCATEGORIA_PRODUTO'].str.strip()
    prods['GRADE'] = prods['GRADE'].str.strip()
    prods['TAMANHO_1'] = prods['TAMANHO_1'].str.strip()
    prods['TAMANHO_2'] = prods['TAMANHO_2'].str.strip()
    prods['TAMANHO_3'] = prods['TAMANHO_3'].str.strip()
    prods['TAMANHO_4'] = prods['TAMANHO_4'].str.strip()
    prods['TAMANHO_5'] = prods['TAMANHO_5'].str.strip()
    prods['TAMANHO_6'] = prods['TAMANHO_6'].str.strip()
    prods['TAMANHO_7'] = prods['TAMANHO_7'].str.strip()
    prods['TAMANHO_8'] = prods['TAMANHO_8'].str.strip()
    prods['TAMANHO_9'] = prods['TAMANHO_9'].str.strip()
    prods['TAMANHO_10'] = prods['TAMANHO_10'].str.strip()
    prods['TAMANHO_11'] = prods['TAMANHO_11'].str.strip()
    prods['TAMANHO_12'] = prods['TAMANHO_12'].str.strip()
    prods['CODIGO_TAB_PRECO'] = prods['CODIGO_TAB_PRECO'].astype(str)
    prods['CODIGO_TAB_PRECO'] = prods['CODIGO_TAB_PRECO'].str.strip()
    
    prods['D1'] = prods['ES1']-prods['VE1']
    prods['D2'] = prods['ES2']-prods['VE2']
    prods['D3'] = prods['ES3']-prods['VE3']
    prods['D4'] = prods['ES4']-prods['VE4']
    prods['D5'] = prods['ES5']-prods['VE5']
    prods['D6'] = prods['ES6']-prods['VE6']
    prods['D7'] = prods['ES7']-prods['VE7']
    prods['D8'] = prods['ES8']-prods['VE8']
    prods['D9'] = prods['ES9']-prods['VE9']
    prods['D10'] = prods['ES10']-prods['VE10']
    prods['D11'] = prods['ES11']-prods['VE11']
    prods['D12'] = prods['ES12']-prods['VE12']

    num = prods._get_numeric_data()
    num[num < 0] = 0

    prods['D1'] = prods['D1'].astype('Int64')
    prods['D2'] = prods['D2'].astype('Int64')
    prods['D3'] = prods['D3'].astype('Int64')
    prods['D4'] = prods['D4'].astype('Int64')
    prods['D5'] = prods['D5'].astype('Int64')
    prods['D6'] = prods['D6'].astype('Int64')
    prods['D7'] = prods['D7'].astype('Int64')
    prods['D8'] = prods['D8'].astype('Int64')
    prods['D9'] = prods['D9'].astype('Int64')
    prods['D10'] = prods['D10'].astype('Int64')
    prods['D11'] = prods['D11'].astype('Int64')
    prods['D12'] = prods['D12'].astype('Int64')

    prods['DISP'] = (prods['D1'] + prods['D2'] + prods['D3'] + prods['D4'] +
         prods['D5'] + prods['D6'] + prods['D7']+prods['D8']+prods['D9']
         +prods['D10']+prods['D11']+prods['D12'])
    
    prods = prods[(prods['DISP'] > 0)]
    
    

    prods = prods.drop(columns=['ES1', 'ES2','ES3','ES4','ES5','ES6','ES7','ES8','ES9','ES10','ES11','ES2','VE1','VE2','VE3','VE4','VE5','VE6','VE7','VE8',
                                'VE9','VE10','VE11','VE12'])

    # prods = prods.sort_values(by=['CATEGORIA_PRODUTO', 'SUBCATEGORIA_PRODUTO','DISP'],ascending=[True,True,False])

    conn.close()
    return prods


def df_tolist(prods):

    lista_produtos =[]
    
    prod_ant = ''
    
    p = Produto()
    p.produto = 'ERRO'
    
    for index, row in prods.iterrows():

        #elimina produtos sem imagem
        if not glob.glob('static/imgs/'+row['PRODUTO']+'.jpg'):
            continue
        
        if row['PRODUTO']==prod_ant:
            
            p.estoque_tot = p.estoque_tot + row['DISP']
            estq = Estoque()
            estq.cor = row['COR_PRODUTO']
            
            es = []
            for i in range(p.qtd_tams):
                t =i+1
                es.append(row['D'+str(t)])
            estq.qtds = es
            p.estoque.append(estq)
            
        else:            
            if p.produto != 'ERRO':            
                lista_produtos.append(p)
            
            p = Produto()
            p.estoque_tot = row['DISP']
            
            prod = row['PRODUTO']
            p.produto = prod
            p.produto_modal = prod.replace(".", "z")
            p.tabela = row['CODIGO_TAB_PRECO']
            p.colecao = row['COLECAO']
            p.categoria = row['CATEGORIA_PRODUTO']
            p.subcategoria = row['SUBCATEGORIA_PRODUTO']
            p.qtd_tams = row['TAMANHOS_DIGITADOS']
            p.preco = row['PRECO1']
            if row['SORTIMENTO_COR']:
                p.sortido = 'Venda Sortida'
            else:
                p.sortido = 'Venda por cor'
            p.desc_cor = row['DESC_COR']
            p.composicao = row['DESC_COMPOSICAO']
            p.url = 'imgs/'+p.produto+'.jpg'
            p.estoque = []
            
            tams = []
            for i in range(p.qtd_tams):
                t =i+1
                tams.append(row['TAMANHO_'+str(t)])
            p.tams = tams
            
            estq = Estoque()
            estq.cor = row['COR_PRODUTO']
            
            es = []
            for i in range(p.qtd_tams):
                t =i+1
                es.append(row['D'+str(t)])
            estq.qtds = es
            p.estoque.append(estq)
        
        
        
        prod_ant = row['PRODUTO']

    lista_produtos = sorted(lista_produtos, key = lambda x: (x.subcategoria, -x.estoque_tot))

    return lista_produtos

def produtos_col_cat(tabela,colecao,categoria):

    key = "dados"
    print('chave : ' + key)

    if cache.get(key) is None:
        prods = df_tolist(produtos_disp())         
        cache.set(key, prods, 60*30)
        print('Banco')
    else:
        print('Cache')
        prods = cache.get(key)

    #Busca cols erp vinculadas a colecao b2b selecionada
    cols_erp = list(ColecaoErp.objects.filter(colecaoB2b__title=colecao).values_list('codigo', flat=True).distinct())
    
    prods = list(filter(lambda x: x.colecao in cols_erp, prods))

    prods = list(filter(lambda x: x.categoria == categoria, prods))
    prods = list(filter(lambda x: x.tabela == tabela, prods))

    return prods

    

def produtos_col_subcat(tabela,colecao,categoria,subcategoria):

    key = "dados"
    print('chave : ' + key)

    if cache.get(key) is None:
        prods = df_tolist(produtos_disp())         
        cache.set(key, prods, 60*30)
        print('Banco')
    else:
        print('Cache')
        prods = cache.get(key)

    #Busca cols erp vinculadas a colecao b2b selecionada
    cols_erp = list(ColecaoErp.objects.filter(colecaoB2b__title=colecao).values_list('codigo', flat=True).distinct())
    
    prods = list(filter(lambda x: x.colecao in cols_erp, prods))
    
    prods = list(filter(lambda x: x.categoria == categoria, prods))
    prods = list(filter(lambda x: x.subcategoria == subcategoria, prods))
    prods = list(filter(lambda x: x.tabela == tabela, prods))

    return prods


def get_produto(produto,tabela):

    key = "dados"
    print('chave : ' + key)

    if cache.get(key) is None:
        
        prods = df_tolist(produtos_disp()) 
        cache.set(key, prods, 60*30)
        print('Banco')
    else:
        print('Cache')
        prods = cache.get(key)

    prods = list(filter(lambda x: x.produto == produto, prods))
    prods = list(filter(lambda x: x.produto == produto, prods))
    prods = list(filter(lambda x: x.tabela == tabela, prods))
    prod = prods[0]

    return prod

# def cats_subcats():

#     key = "cats"

#     if cache.get(key) is None:
#         #Consulta BD
#         server = '192.168.2.11'
#         db = 'ondas800'
#         user = 'timur'
#         pwd = 'p$3dasony' 
#         conn = pyodbc.connect('DRIVER=' + DRIVER + ';SERVER=' + server + ';DATABASE=' + db + ';UID=' + user + ';PWD=' + pwd)

#         query = """
#             select distinct pc.CATEGORIA_PRODUTO, psc.SUBCATEGORIA_PRODUTO 
#             from 
#             PRODUTOS_CATEGORIA pc left join
#             PRODUTOS_SUBCATEGORIA psc on pc.COD_CATEGORIA=psc.COD_CATEGORIA
            
#             order by pc.CATEGORIA_PRODUTO
#         """
#         categorias = pd.read_sql(query,conn)

#         categorias['CATEGORIA_PRODUTO'] = categorias['CATEGORIA_PRODUTO'].str.strip()
#         categorias['SUBCATEGORIA_PRODUTO'] = categorias['SUBCATEGORIA_PRODUTO'].str.strip()

#         cats = []
#         cat = Produto()
#         cat.cat = 'PRIMEIRO'
#         cat.subcats =[]
#         for index,row in categorias.iterrows():
#             if cat.cat == 'PRIMEIRO':
#                 cat.cat = row['CATEGORIA_PRODUTO']
#                 if cat.cat == 'MASCULINO':
#                     cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])
#             elif cat.cat == row['CATEGORIA_PRODUTO']:
#                 if cat.cat == 'MASCULINO':
#                     cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])
#             else:
#                 cats.append(cat)
#                 cat = Produto()
#                 cat.subcats =[]
#                 cat.cat = row['CATEGORIA_PRODUTO']
#                 if cat.cat == 'MASCULINO':
#                     cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])

#         conn.close()
#         cache.set(key, cats, 60*60*24)
#         print('Banco')
#     else:
#         #Consulta Cache
#         cats = cache.get(key)
#         print('Cache')

#     return cats

def cats_subcats():

    key = "cats"

    if cache.get(key) is None:

        categorias = produtos_disp()
        categorias = categorias[categorias['CODIGO_TAB_PRECO']=='01']
        categorias = categorias[categorias['CATEGORIA_PRODUTO']!='ENTREGA']
        categorias = categorias.groupby(['CATEGORIA_PRODUTO','SUBCATEGORIA_PRODUTO'],as_index=False).sum()
        categorias = categorias[['CATEGORIA_PRODUTO','SUBCATEGORIA_PRODUTO']]

        print(categorias)

        cats = []
        cat = Produto()
        cat.cat = 'PRIMEIRO'
        cat.subcats =[]

        for index,row in categorias.iterrows():
            if cat.cat == 'PRIMEIRO':
                cat.cat = row['CATEGORIA_PRODUTO']
                cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])
            elif cat.cat == row['CATEGORIA_PRODUTO']:
                cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])
            else:
                cats.append(cat)
                cat = Produto()
                cat.subcats =[]
                cat.cat = row['CATEGORIA_PRODUTO']
                cat.subcats.append(row['SUBCATEGORIA_PRODUTO'])        
        cats.append(cat)
        cache.set(key, cats, 60*60*24)
        print('Banco')
    else:
        #Consulta Cache
        cats = cache.get(key)
        print('Cache')

    return cats    

def prods_sem_imagem():
    
    prods = produtos_disp()
    prods = prods[prods['CODIGO_TAB_PRECO']=='01']

    
    for index, row in prods.iterrows():
        
        #deixa somente produtos com imagem
        if glob.glob('static/imgs/'+row['PRODUTO']+'.jpg'):
            prods.drop(index, inplace=True)
    
    return prods
