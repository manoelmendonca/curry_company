#------------------------------------------------------------------------------
# FTC - Aula 54 - Visão Restaurantes, versão 2
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

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍒', layout='wide' )

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

def distance( df1, fig ):
    # Calculate distances
    colunas = ['Restaurant_latitude','Restaurant_longitude',
               'Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,colunas].apply( lambda x: 
                            haversine( 
                            (x['Restaurant_latitude'],x['Restaurant_longitude']), 
                            (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )

    # diferent returns
    if fig==False:
        # return distance
        avg_distance = np.round( df1['distance'].mean(), 2 )
        return avg_distance
    else:
        # return figure
        avg_distance = df1.loc[:, ['City','distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0] ) ] )
        return fig

def avg_std_time_delivery( df1, festival, op ):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
      Input:
        - df: Dataframe com os dados necessários para o cálculo
        - op: Tipo de operação que precisa ser calculada:
              'avg_time': calcula o tempo médio
              'std_time': calcula o desvio padrão do tempo
      Output:
        - df: Dataframe com 2 colunas e 1 linha.
    """
    df2 = (df1.loc[:,['Time_taken(min)', 'Festival']]
              .groupby('Festival')
              .agg( { 'Time_taken(min)' : ['mean','std'] } ))
    df2.columns = ['avg_time', 'std_time']
    df2 = df2.reset_index()
    df2 = np.round( df2.loc[df2['Festival'] == festival, op], 2 )
    return df2

def avg_std_time_graph( df1 ):
    colunas = ['Time_taken(min)','City']
    df2 = df1.loc[:, colunas].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df2.columns = ['avg_time','std_time']
    df2 = df2.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df2['City'], y=df2['avg_time'], 
                        error_y=dict( type='data', array=df2['std_time'] ) ) )
    fig.update_layout( barmode='group' )
    return fig

def avg_std_time_on_traffic( df1 ):
    colunas = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df2 = df1.loc[:, colunas].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df2.columns = ['avg_time','std_time']
    df2 = df2.reset_index()
    fig = px.sunburst(df2, path=['City','Road_traffic_density'], values='avg_time', 
                    color='std_time', color_continuous_scale='RdBu', 
                    color_continuous_midpoint=np.average(df2['std_time']))
    return fig


#------------------------------------------------------------------------------
# ..... VISÃO RESTAURANTES ..... (ver Aula 41)
#------------------------------------------------------------------------------

# Read dataset
df = pd.read_csv('train.csv')
df1 = clean_data( df )

#...... Barra Lateral no Streamlit ............................................
st.header('Marketplace - Visão Restaurantes')

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

# .......... Criação dos filtros para ligar o Dashboard à base de dados
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
        st.title('Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )  
            col1.metric( 'Entregadores únicos', delivery_unique )

        with col2:
            avg_distance = distance( df1, fig=False )
            col2.metric( 'A distância média das entregas', avg_distance )

        with col3:
            #col3.dataframe(df2)
            df2 = avg_std_time_delivery( df1, 'Yes ', 'avg_time' )
            col3.metric( 'Tempo Médio de Entrega c/ Festival', df2 )

        with col4:
            df2 = avg_std_time_delivery( df1, 'Yes ', 'std_time' )
            col4.metric( 'STD Entrega c/ Festival', df2 )

        with col5:
            df2 = avg_std_time_delivery( df1, 'No ', 'avg_time' )
            col5.metric( 'Tempo Médio de Entrega s/ Festival', df2 )

        with col6:
            df2 = avg_std_time_delivery( df1, 'No ', 'std_time' )
            col6.metric( 'STD Entrega s/ Festival', df2 )

    with st.container():
        st.markdown("""---""")

        col1, col2 = st.columns( 2 )

        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            colunas = ['Time_taken(min)', 'City', 'Type_of_order']
            df2 = (df1.loc[:, colunas].groupby(['City','Type_of_order'])
                                    .agg({'Time_taken(min)':['mean','std']}))
            df2.columns = ['TimeTaken_mean','TimeTaken_std']
            df2 = df2.reset_index()
            st.dataframe( df2 )

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2 = st.columns( 2 )

        with col1:
            fig = distance( df1, fig=True)
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig, use_container_width=True )

