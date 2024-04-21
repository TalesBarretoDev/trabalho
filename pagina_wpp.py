import json
from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar

from crud import deleta_teletrabalho, le_todos_usuarios

from crud import Datas
from crud import le_teletrabalho, le_todos_usuarios, busca_datas_usuario

def update_value():
    pass


def tab_gestao_teletrabalho():
    usuario_atual = st.session_state['usuario']
    datas_usuario = busca_datas_usuario(usuario_atual.id)

    # Mostra apenas as datas em formato legível
    datas_formatadas = sorted([data.DATA for data in datas_usuario if data.wpp == True])

    tab_del = st.sidebar.selectbox("Delete", ["Delete"])

    if tab_del == "Delete":
        data_selecionada = st.selectbox(
            'Selecione a data para deletar',
            datas_formatadas
        )

        if st.button('Deletar'):
            # Aqui você precisa encontrar o objeto Datas correspondente à data selecionada
            data_para_deletar = next((data for data in datas_usuario if data.DATA == data_selecionada and data.wpp == True), None)

            if data_para_deletar:
                deleta_teletrabalho(data_para_deletar.id)
                st.success(f'Data {data_selecionada} deletada com sucesso!')
            else:
                st.error('Data selecionada não encontrada!')

        
        
    

def verifica_e_adiciona_data(data):
    usuario = st.session_state['usuario']

    usuario.adiciona_wpp(data)
    limpar_datas()

def limpar_datas():
     del st.session_state['data_wpp']
    
def pagina_wpp():
    usuarios = le_todos_usuarios()
    with st.sidebar:
        tab_gestao_teletrabalho()
        
    with open('calendar_options.json') as f:
        calendar_options = json.load(f)

    calendar_events = []
    for usuario in usuarios:
        calendar_events.extend(usuario.lista_datas_wpp())

    usuario = st.session_state['usuario']


    calendario_wpp = calendar(events=calendar_events, options=calendar_options)
    if ('callback' in calendario_wpp 
        and calendario_wpp['callback'] == 'dateClick'):
        
        raw_date = calendario_wpp['dateClick']['date'].split('T')[0]
        
        if st.session_state['ultimoclique2'] != raw_date:
              
            st.session_state["ultimoclique2"] = raw_date
            st.session_state["data_wpp"] = raw_date

            cols = st.columns([0.5, 0.2, 0.3])

            with cols[0]:
                st.warning(f'Data whatsapp selecionada: {raw_date}')
            with cols[1]:
                st.button(
                    'Limpar',
                    use_container_width=True,
                    on_click=limpar_datas
                    )
            with cols[2]:
                st.button(
                    'Adicionar plantão whatsapp',
                    use_container_width=True,
                    on_click=verifica_e_adiciona_data,
                    args=(st.session_state["data_wpp"],)
                    )

