#------------------------------------------------------------------------------
# FTC - Aula 53 - Visão Empresa, versão 2
#                                                Data inicial: 17.6.2023   MLMM
#------------------------------------------------------------------------------

# Libraries
import pandas as pd
import numpy as np
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import folium

st.set_page_config( page_title='Visão Empresa', page_icon='🏯', layout='wide' )

#------------------------------------------------------------------------------
# FUNÇÕES
#------------------------------------------------------------------------------

def clean_data( df1 ):
    """ Esta função tem a reaponsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção de texto em variável numérica )

        Input: Dataframe
        Output: Dataframe
    """
    # Limpeza dos dados: Todas as filtragens e conversões de dados necessárias.
    linhas = ( (df['Delivery_person_Age']!='NaN ') & 
            (df['Delivery_person_Ratings']!='NaN ') & 
            (df['Road_traffic_density']!='NaN ') &
            (df['City']!='NaN ') &
            (df['multiple_deliveries']!='NaN ') &
            (df['Weatherconditions']!='conditions NaN')
            )
    df1 = df.loc[linhas, :].copy()

    # Removendo os espaços dentro de strings/texto/objects
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # Converte colunas para int, float, datetime, etc
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Converte o TIME-TAKEN
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # Converte DATA de string para DateTime
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    return df1

def order_metric( df1):
    # ..... Cálculo .1. Quantidade de pedidos por dia
    df2 = ( df1.loc[:, ['ID','Order_Date']]
               .groupby('Order_Date')
               .count()
               .reset_index() )
    df2['Order_Date'] = pd.to_datetime(df2['Order_Date'], format='%d-%m-%Y')
    df2.columns = ['order_date','qtde_entregas']
    fig = px.bar( df2, x='order_date', y='qtde_entregas' )
    return fig

def traffic_order_share( df1 ):
    colunas = ['ID','Road_traffic_density']
    df2 = ( df1.loc[:, colunas]
               .groupby('Road_traffic_density')
               .count()
               .reset_index() )
    df2['percent_id'] = 100 * (df2['ID'] / df2['ID'].sum())
    fig = px.pie( df2, values='percent_id', names='Road_traffic_density' )
    return fig

def traffic_order_city( df1 ):
    colunas = ['ID','City','Road_traffic_density']
    df2 = ( df1.loc[:,colunas]
               .groupby(['City','Road_traffic_density'])
               .count()
               .reset_index() )
    fig = px.scatter(df2, x='City', y='Road_traffic_density', size='ID', color='Road_traffic_density')
    return fig

def order_by_week( df1 ):
    # Não existe a coluna 'semana do ano': criar nova coluna
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    # Agrupar os pedidos por semana do ano
    df2 = ( df1.loc[:, ['ID','week_of_year'] ]
               .groupby('week_of_year')
               .count()
               .reset_index() )
    # Gráfico
    fig = px.line(df2, x='week_of_year', y='ID')
    return fig

def order_share_by_week( df1 ):
    # ..... Quantidade de ordens por entregador e por semana
    colunas = ['ID','Order_Date','Delivery_person_ID']
    # Calcula qtde de entregas por semana
    df2 = ( df1.loc[:,['ID','week_of_year']]
               .groupby('week_of_year')
               .count()
               .reset_index() )
    # Calcula qtde de entregadores únicos por semana
    df3 = ( df1.loc[:,['Delivery_person_ID','week_of_year']]
               .groupby('week_of_year')
               .nunique()
               .reset_index() )
    # Junta os resultados num único DataFrame
    df4 = pd.merge(df2, df3, how='inner')
    # Cálculo final: qtde média de ordens por entregador
    df4['order_by_deliver'] = df4['ID'] / df4['Delivery_person_ID']
    # Gráfico
    fig = px.line(df4, x='week_of_year', y='order_by_deliver')
    return fig

def country_map( df1 ):
    colunas = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    linhas = (df['City']!='NaN ') & (df['Road_traffic_density']!='NaN ')
    df1 = df.loc[linhas,colunas]
    df2 = ( df1.loc[:,:].groupby(['City','Road_traffic_density'])
                        .median()
                        .reset_index() )
    # Desenhar MAPA
    CityMap = folium.Map( zoom_start=11 )
    for index, location_info in df2.iterrows():
        # Insere, um por um, os pinos no mapa.
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City','Road_traffic_density']] ).add_to(CityMap)
    folium_static( CityMap, width=1024, height=600 )


#------------------------------------------------------------------------------
# ..... VISÃO EMPRESA ..... (ver Aula 37)
#------------------------------------------------------------------------------

# Read dataset
df = pd.read_csv('train.csv')
df1 = clean_data( df )

#------------------------------------------------------------------------------
#...... Barra Lateral no Streamlit ............................................
#------------------------------------------------------------------------------
st.header('Marketplace - Visão Cliente')

image_path = 'LOGO_MONKEY.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown("""---""")

st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até quaal valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium'] )
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Comunidade DS')

# Criação dos filtros para ligar o Dashboard à base de dados
# Filtro de dados
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#st.dataframe( df1 )

#------------------------------------------------------------------------------
#...... Layout no Streamlit ...................................................
#------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.header('Orders by Day')
        st.plotly_chart(fig, use_container_width=True)

    # ..... Duas colunas para dois gráficos
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            fig = traffic_order_city( df1 )
            st.header( 'Traffic Order City' )
            st.plotly_chart( fig, use_container_width=True )

with tab2:
    # ..... Quantidade de ordens por semana
    with st.container():
        fig = order_by_week( df1 )
        st.markdown('# Order by Week')
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        fig = order_share_by_week( df1 )
        st.markdown('# Order Share by Week')
        st.plotly_chart( fig, use_container_width=True )

with tab3:
    st.markdown('# Country Map')
    country_map( df1 )

