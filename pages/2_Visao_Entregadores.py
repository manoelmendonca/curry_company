#------------------------------------------------------------------------------
# FTC - Aula 54 - Visão Entregadores, versão 2
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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚗', layout='wide' )

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

def top_delivers( df1, AscendingTrueDescendingFalse ):
    colunas = ['City','Delivery_person_ID','Time_taken(min)']
    df2 = (df1.loc[:, colunas]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending=AscendingTrueDescendingFalse)
              .reset_index())
    df_aux1 = df2.loc[df2['City']=='Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City']=='Urban', :].head(10)
    df_aux3 = df2.loc[df2['City']=='Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
    return df3

#------------------------------------------------------------------------------
# ..... VISÃO ENTREGADORES ..... (ver Aula 39)
#------------------------------------------------------------------------------

# Read dataset
df = pd.read_csv('train.csv')
df1 = clean_data( df )

#------------------------------------------------------------------------------
#...... Barra Lateral no Streamlit ............................................
#------------------------------------------------------------------------------
st.header('Marketplace - Visão Entregadores')

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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior Idade', maior_idade )
        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric( 'Menor Idade', menor_idade )
        with col3:
            Melhor_Condicao = df1['Vehicle_condition'].max()
            col3.metric( 'Melhor condição', Melhor_Condicao )
        with col4:
            Pior_Condicao = df1['Vehicle_condition'].min()
            col4.metric( 'Pior condição', Pior_Condicao )

    with st.container():
        st.markdown( """---""" )
        st.title('Avaliações')
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            colunas = ['Delivery_person_ID','Delivery_person_Ratings']
            df2 = ( df1.loc[:, colunas]
                       .groupby('Delivery_person_ID')
                       .mean()
                       .reset_index() )
            st.dataframe( df2 )

        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            colunas = ['Road_traffic_density','Delivery_person_Ratings']
            # DICA: função de agregação ".agg" recebe um dicionário {} aonde...
            df2 = ( df1.loc[:, colunas]
                       .groupby('Road_traffic_density')
                       .agg( {'Delivery_person_Ratings' : ['mean','std']} ) )
            # renomeando as colunas...
            df2.columns = ['delivery_mean','delivery_std']
            df2 = df2.reset_index()
            st.dataframe( df2 )
            #
            st.markdown('##### Avaliação média por Clima')
            colunas = ['Weatherconditions','Delivery_person_Ratings']
            df2 = ( df1.loc[:, colunas].groupby('Weatherconditions')
                       .agg( {'Delivery_person_Ratings' : ['mean','std']} ) )
            df2.columns = ['weather_mean','weather_std']
            df2 = df2.reset_index()
            st.dataframe( df2 )

    with st.container():
        st.markdown( """---""" )
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers( df1, AscendingTrueDescendingFalse=True )
            st.dataframe( df3 )

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers( df1, AscendingTrueDescendingFalse=False )
            st.dataframe( df3 )

