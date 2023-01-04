# -*- coding: utf-8 -*-
"""module16exercise.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kQBvtNyE8kYp1eLvsIIjPM0BJRAqxxo5

---

# **Análise Exploratória de Dados de vendas da Adidas (2020-2021)**

## 1\. Contexto

**Definindo problema de negócio:**


1.   Qual foi o método de venda que mais gerou lucro operacional, no período analisado?
2.   Quais foram os 3 maiores vendedores, do método de venda que mais gerou lucro operacional?.
4.  Ranking das cidades que mais registraram vendas online.
5.  Mostrar em um mapa as cidades que registraram vendas online.

## 2\. Pacotes e bibliotecas
"""

#bibliotecas

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os
import getpass
from matplotlib import cm
from datetime import datetime

import geopy
import folium
from geopy import Nominatim

import warnings
warnings.filterwarnings('ignore')

#carregando dataset
!wget 'https://raw.githubusercontent.com/Fagner608/adidas_sales_analytics/main/adidas_csv.csv' -O dados.csv

#lendo dataset
dados_brutos  = pd.read_csv('./dados.csv', sep = ';')



"""## 3\. Exploração de dados

Conhecendo a estrutura dos dados
"""

dados_brutos.shape

dados_brutos.columns

dados_brutos.head()

"""**Resumo do dataset**

Os dados estão organizados em formato tabular e schema está bem definido. Por isso, aparentemente não será necessário implementar grande trabalho no pré-processamento para responder às questões de negócio levantadas.

Assim sendo, tendo em vista o problema de negócio definido no início da sessão, será procedida a filtragem dos dados, mantendo-se apenas o necessário.

**Data wrangling**
"""

#Filtragem dos dados
dados = dados_brutos[['Retailer', 'Invoice Date', 'City',
       'Product', 'Units Sold', 'Total Sales','Operating Profit', 'Operating Margin', 'Sales Method']]

dados.head()

#verificando dados faltantes
dados.isnull().any()

#verificando schema dos dados
dados.info()

"""- Não existem dados faltantes
- Os atributos 'total sales', 'operating margem' e 'operating margin' precisaram de tratamento para adequar os dados ao tipo correto.
"""

#iniciando tratamento de 'total_sales'
dados['Total Sales'] = dados['Total Sales'].apply(lambda x: float(x.split('$')[1]))

#iniciando tratamento de 'Operating Margin'
dados['Operating Margin'] = dados['Operating Margin'].apply(lambda x: float(x.split('%')[0]))

#iniciando tratamento de 'Operating Margin'
dados['Operating Profit'] = dados['Operating Profit'].apply(lambda x: float(x.split('$')[1]))

dados.info()

"""**Iniciando descrição estatística dos dados**"""

#dados numéricos
dados.select_dtypes('float64').describe().T

#dados categórios
dados.select_dtypes('object').describe().T

"""## **Iniciando pesquisa**

- Qual foi o método de venda que mais gerou lucro operacional, no período analisado?
"""

profit_methods = dados[['Sales Method', 'Operating Profit']].groupby('Sales Method').agg('sum')

profit_methods['relative_profts'] = profit_methods['Operating Profit'].apply(lambda x: round(x / profit_methods['Operating Profit'].sum() * 100, 2))
profit_methods

#labels
#criadno labels
labels = [str(i) + " " + '[' + str(profit_methods.loc['{}'.format(i), 'relative_profts']) + "%" + "]" for i in profit_methods.index]

#Visualizando resultados


cs = cm.Set3(np.arange(100))

    
f = plt.figure()

plt.pie(profit_methods['relative_profts'], labeldistance = 1, radius= 3, colors = cs, wedgeprops = dict(width = 0.8))
plt.legend(labels = labels, loc = "center", prop = {'size':12})
plt.title("Lucro operacional /\n método de venda", loc = "Center", fontdict = {"fontsize": 17, "fontweight":17})
plt.show()

"""**Respondendo a questão de negócio 1:**
  - O método de venda que mais contribuiu para o resultado, é a venda online, responsável por 53.26% do lucro operacional gerado no período analisado.

- Mostrar os 3 maiores vendedores, do método de venda que mais gerou lucro operacional?
"""

dados.head()

top3_retailer = dados[['Sales Method', "Operating Profit", 'Retailer']]

top3_retailer.columns = ['Sales_Method', 'Operating_Profit', 'Retailer']

top3_retailer = top3_retailer.query('Sales_Method == "Online"').reset_index(drop = True)

top3_retailer.drop('Sales_Method', axis = 1, inplace=True)

top3_retailer = top3_retailer.groupby('Retailer').agg('sum').sort_values(by = 'Operating_Profit', ascending = False)

#Iniciando criacao de other
other = {}
other['Operating_Profit'] = top3_retailer.query('Operating_Profit < 87588.214').sum()['Operating_Profit']

top3_retailer = top3_retailer.query('Operating_Profit >= 87588.214')

top3_retailer = top3_retailer.append(pd.DataFrame(other, index = ['other']))

top3_retailer

#inserindo colunas com lucro operacional relativo
top3_retailer = top3_retailer.apply(lambda x: round(x / top3_retailer['Operating_Profit'].sum()*100, 2))

#labels
labels_retailer  = [str(i)  + " " + "[" + str(top3_retailer.loc['{}'.format(i)][0]) + "%" + "]"  for i in top3_retailer.index]
labels_retailer

#plotando gráfico
cs = cm.Set3(np.arange(100))
f = plt.figure()


plt.pie(top3_retailer, labeldistance = 1, radius= 3, colors = cs, wedgeprops = dict(width = 0.8))
plt.legend(labels = labels_retailer, loc = "center", prop = {'size':12})
plt.title("Top-3 vendedores online", loc = "Center", fontdict = {"fontsize": 17, "fontweight":17})
plt.show()

"""**Respondendo à questão de negócio 2:**
  - Os Top-3 vendedores, em vendas online, foram:
        1.   Foot Locker
        2.   West Gear
        3.   Sports Direct

Outros vendedores contribuiram com 21.61% da vendas online.

- Ranking das cidades que mais registraram vendas online
"""

#Preparando variáveis de interesse
profit_cities = dados[['City', 'Operating Profit', 'Sales Method']]

profit_cities.columns = ['City', 'Operating_Profit', 'Sales_Method']

profit_cities = profit_cities.query('Sales_Method == "Online"')

profit_cities.drop('Sales_Method', axis = 1, inplace = True)

profit_cities = profit_cities.groupby('City').agg('sum')

profit_cities['relative_profts'] = profit_cities['Operating_Profit'].apply(lambda x: round(x / profit_cities['Operating_Profit'].sum()*100, 2))

profit_cities.drop('Operating_Profit', axis = 1, inplace = True)

#Monstando dataframe para plotagem
other_profit = {}

other_profit['relative_profts'] = profit_cities.query('relative_profts < 1.00')['relative_profts'].sum()

profit_cities = profit_cities.query('relative_profts >= 1.00')

profit_cities = profit_cities.append(pd.DataFrame(other_profit, index = ['Others']))

profit_cities = profit_cities.sort_values(by = 'relative_profts', ascending = False)

#plotando gráfico

plt.figure(figsize=(16,8))
sns.barplot(x = profit_cities['relative_profts'], y = profit_cities.index, orient = 'h', palette = "terrain")
plt.ylabel('Cidades')
plt.xlabel('\nContribuição ao lucro operacional(%)')
plt.title('\nLucro operacional das vendas online por cidade\n')
plt.show()

"""**Impressões do gráfico das cidades que mais registraram vendas online**

  - O gráfico mostra o equilíbrio entre as cidades que mais venderam, e o conjunto que se forma com as cidades que registraram menos de 1% no lucro operacional. Observe, que um grande grupo de cidades registrou, sozinha, mais de 1% - algumas, inclusive, se destacam com mais de 3% -; contudo, a categoria 'others', formada por cidades que registraram menos de 1% apresentam a maior participação no lucro operacional do período, com mais de 6%.

**Inserindo no mapa as cidade acima mencionadas**
"""

profit_cities.drop('Others', inplace = True)

#instanciando usuario
geolocator = Nominatim(user_agent = 'my_project')

#buscando dados geográficos
for i in profit_cities.index:
   location = geolocator.geocode(i)
   if location:
     profit_cities.loc[i, 'latitude'] = location.latitude
     profit_cities.loc[i, 'longitude'] = location.longitude
   else:
      profit_cities.loc[i, 'latitude'] = None
      profit_cities.loc[i, 'longitude'] = None

#conferindo se todos os dados foram encontrados
profit_cities.info()

#criando marcadores
marcadores = []

for i in profit_cities.index:
  cidade = i
  lat = profit_cities.loc[i, 'latitude']
  lon = profit_cities.loc[i, 'longitude']
  marcadores.append((cidade, lat, lon))

#Instanciando mapa
mapa = folium.Map(location=[43.548826,	-96.730774], zoom_start=3.2)

#Instanciando marcadores
for cidade, lat, lon in marcadores:
  dados = folium.CircleMarker(
    location=[lat, lon],
    radius=5,
    popup= cidade,
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
)
  dados.add_to(mapa)

#salvando dados
mapa.save('index.html')

#plotando mapa
mapa

"""**Impressões do mapa geográfico das vendas**
  - Por fim, o mapa evidencia que a grande parte das vendas online, no período analisado, vem da costa leste dos Estados Unidos. Isso inseja várias conjecturas sobre as possíveis causas, a primeira a ser analisada, seria a área coberta pelas 3 principais empresas de vendas online acima citadas.
"""