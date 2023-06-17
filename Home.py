#------------------------------------------------------------------------------
# Projeto de Dashboard "Curry Company"
#                                                Data inicial: 17.6.2023   MLMM
#------------------------------------------------------------------------------

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🪷",
    layout='wide'
)

#...... Barra Lateral no Streamlit ............................................

image_path = 'LOGO_MONKEY.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown("""---""")

st.write( "# Curry COmpany Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @meigaron
    """)







