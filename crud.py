from typing import List
from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine, String, Boolean, Integer, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship

from werkzeug.security import generate_password_hash, check_password_hash

pasta_atual = Path(__file__).parent
PATH_TO_BD = pasta_atual / 'bd_usuarios.sqlite'

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = 'usuarios_ISS'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(30))
    senha: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(30))
    acesso_gestor: Mapped[bool] = mapped_column(Boolean(), default=False)
    data_admissao: Mapped[str] = mapped_column(String(30))
    datas: Mapped[List["Datas"]] = relationship(
        back_populates='parent',
        lazy='subquery'
    )

    def __repr__(self):
        return f"Usuario({self.id=}, {self.nome=})"
    
    def define_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verifica_senha(self, senha):
        return check_password_hash(self.senha, senha)
    
    def adiciona_data(self, data):

        with Session(bind=engine) as session:
            linha = Datas(
                parent_id=self.id,
                DATA = data,
                presencial = True                
            )
            session.add(linha)
            session.commit()
    
    def adiciona_wpp(self, data):

        with Session(bind=engine) as session:
            linha = Datas(
                parent_id=self.id,
                DATA = data,
                wpp = True                
            )
            session.add(linha)
            session.commit()

        
    
    def lista_datas(self):
        lista_eventos = []
        for data in self.datas:
            lista_eventos.append({
                'title': f'{self.nome}',
                'allDay' : "true",
                'start': data.DATA,
                # 'end': "2024-04-10",
                'resourceId': self.id
            })
        return lista_eventos
    
    def lista_datas_presencial(self):
        lista_eventos = []
        for data in self.datas:
            if data.presencial:
                lista_eventos.append({
                    'title': f'{self.nome}',
                    'allDay' : "true",
                    'start': data.DATA,
                    # 'end': "2024-04-10",
                    'resourceId': self.id
                })
        return lista_eventos

    def lista_datas_wpp(self):
        lista_eventos = []
        for data in self.datas:
            if data.wpp:
                lista_eventos.append({
                    'title': f'{self.nome}',
                    'allDay' : "true",
                    'start': data.DATA,
                    # 'end': "2024-04-10",
                    'resourceId': self.id
                })
        return lista_eventos

class Datas(Base):
    __tablename__ = 'datas'

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('usuarios_ISS.id'))
    parent: Mapped["Usuario"] = relationship(lazy='subquery')
    DATA: Mapped[str] = mapped_column(String(30))
    presencial: Mapped[bool] = mapped_column(Boolean(), default=False)
    wpp: Mapped[bool] = mapped_column(Boolean(), default=False)

    
engine = create_engine(f'sqlite:///{PATH_TO_BD}')
Base.metadata.create_all(bind=engine)


# CRUD ======================
def cria_usuarios(
        nome,
        senha,
        email,
        **kwargs
):
    with Session(bind=engine) as session:
        usuario = Usuario(
            nome=nome,
            email=email,
            **kwargs
        )
        usuario.define_senha(senha)
        session.add(usuario)
        session.commit()

def le_todos_usuarios():
    with Session(bind=engine) as session:
        comando_sql = select(Usuario)
        usuarios = session.execute(comando_sql).fetchall()
        usuarios = [user[0] for user in usuarios]
        return usuarios

def le_usuario_por_id(id):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        return usuarios[0][0]

def modifica_usuario_old(
        id, 
        nome=None,
        senha=None,
        email=None,
        acesso_gestor=None
        ):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            if nome:
                usuario[0].nome = nome
            if senha:
                usuario[0].senha = senha
            if email:
                usuario[0].email = email
            if not acesso_gestor is None:
                usuario[0].acesso_gestor = acesso_gestor
        session.commit()

def modifica_usuario(
        id, 
        **kwargs
        ):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            for key, value in kwargs.items():
                if key == 'senha':
                    usuario[0].define_senha(value)
                else:
                    setattr(usuario[0], key, value)
        session.commit()

def deleta_usuario(id):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            session.delete(usuario[0])
        session.commit()

def le_teletrabalho():
    with Session(bind=engine) as session:
        comando_sql = select(Datas)
        teletrabalhos = session.execute(comando_sql).fetchall()
        return [teletrabalho[0] for teletrabalho in teletrabalhos]

    
def busca_datas_usuario(id_usuario):
    with Session(bind=engine) as session:
        comando_sql = select(Datas).filter_by(parent_id=id_usuario)
        datas_usuario = session.execute(comando_sql).fetchall()
        return [data[0] for data in datas_usuario]

    
# def deleta_teletrabalho(id):
#     with Session(bind=engine) as session:
#         comando_sql = select(Datas).filter_by(id=id)
#         teletrabalho = session.execute(comando_sql).fetchall()
#         for t in teletrabalho:
#             session.delete(t[0])
#         session.commit()

# def deleta_teletrabalho(data):
#     with Session(bind=engine) as session:
#         comando_sql = select(Datas).filter_by(datas=data)
#         teletrabalho = session.execute(comando_sql).fetchall()
#         for t in teletrabalho:
#             session.delete(t[0])
#         session.commit()
        
def deleta_teletrabalho(id):
    with Session(bind=engine) as session:
        comando_sql = select(Datas).filter_by(id=id)
  # Acessando o atributo DATA
        teletrabalhos = session.execute(comando_sql).fetchall()
        for t in teletrabalhos:
            session.delete(t[0])
        session.commit()

if __name__ == '__main__':

    pass


    cria_usuarios(
        'Tales Barreto',
        senha='adivinha',
        email='talesbarrreto@hotmail.com',
        data_admissao='2021-05-18',
        acesso_gestor=True
        )
    
    # cria_usuarios(
    #     'Juliano Faccioni',
    #     senha='juliano',
    #     email='juliano.com',
    #     data_admissao='2023-01-01',
    #     acesso_gestor=True
    #     )
    
    # cria_usuarios(
    #     'Mateus Kienzle',
    #     senha='mateus',
    #     email='mateus.com',
    #     data_admissao='2023-06-01',
    #     acesso_gestor=False
    #     )