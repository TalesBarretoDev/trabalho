from time import sleep

import streamlit as st

from crud import le_todos_usuarios
from pagina_gestao import pagina_gestao
from pagina_calendario import pagina_calendario
from pagina_wpp import pagina_wpp


def login():
    usuarios = le_todos_usuarios()
    usuarios = {usuario.nome: usuario for usuario in usuarios}
    with st.container(border=True):
        st.markdown('Escala Fiscalização ISS')
        nome_usuario = st.selectbox(
            'Selecione o seu usuário',
            usuarios.keys()
            )
        senha = st.text_input('Digite sua senha', type='password')
        if st.button('Acessar'):
            usuario = usuarios[nome_usuario]
            if usuario.verifica_senha(senha):
                st.success('Login efetuado com sucesso')
                st.session_state['logado'] = True
                st.session_state['usuario'] = usuario
                sleep(1)
                st.rerun()
            else:
                st.error('Senha incorreta')

def pagina_principal():
    st.title('Escala Fiscalização ISS')

    usuario = st.session_state['usuario']
    if usuario.acesso_gestor:
        cols = st.columns(3)
        with cols[0]:
            if st.button(
                'Gestão de Usuários',
                use_container_width=True):
                st.session_state['pag_gestao_usuarios'] = True
                st.session_state['pag_presencial'] = False
                st.session_state['pag_wpp'] = False
                st.rerun()
        with cols[1]:
            if st.button(
                'Escala Presencial',
                use_container_width=True
                ):
                st.session_state['pag_gestao_usuarios'] = False
                st.session_state['pag_presencial'] = True
                st.session_state['pag_wpp'] = False
                st.rerun()
        with cols[2]:
            if st.button(
                'Escala Whatsapp',
                use_container_width=True
                ):
                st.session_state['pag_gestao_usuarios'] = False
                st.session_state['pag_presencial'] = False
                st.session_state['pag_wpp'] = True
                st.rerun()
        
    if st.session_state['pag_gestao_usuarios']:
        pagina_gestao()
    elif st.session_state['pag_presencial']:
        pagina_calendario()
    elif st.session_state['pag_wpp']:
        pagina_wpp()

def main():

    if not 'logado' in st.session_state:
        st.session_state['logado'] = False
    if not 'pag_gestao_usuarios' in st.session_state:
        st.session_state['pag_gestao_usuarios'] = False
    if not 'pag_wpp' in st.session_state:
        st.session_state['pag_wpp'] = False
    if not 'pag_presencial' in st.session_state:
        st.session_state['pag_presencial'] = True
    if not 'ultimo_clique' in st.session_state:
        st.session_state['ultimo_clique'] = ''
    if not 'data_presencial' in st.session_state:
        st.session_state['data_presencial'] = ''
    if not 'ultimoclique2' in st.session_state:
        st.session_state['ultimoclique2'] = ''
    if not 'data_wpp' in st.session_state:
        st.session_state['data_wpp'] = ''
    if not st.session_state['logado']:
        login()
    else:
        pagina_principal()


if __name__ == '__main__':
    main()