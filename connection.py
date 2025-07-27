# import streamlit as st
# from databricks import sql


# connection = sql.connect(
#     server_hostname=st.secrets.database.HOSTNAME,
#     http_path=st.secrets.database.HOSTPATH,
#     access_token=st.secrets.database.HOSTTOKEN,
# )

# def get_state():
#     with connection.cursor() as cursor:
#         cursor.execute(f"SELECT state FROM {st.secrets.database.TABLENAME}")
#         result = cursor.fetchall()
#         return result[0].asDict()['state']

# def set_state(state):
#     with connection.cursor() as cursor:
#         cursor.execute(f"UPDATE {st.secrets.database.TABLENAME} SET state = ?", (state,))
#         connection.commit()
#         return True


import streamlit as st
from sqlalchemy import create_engine, text


# Função para criar e cachear a conexão com o banco de dados.
# `@st.cache_resource` garante que a conexão seja criada apenas uma vez.
def init_connection():
    """
    Inicializa a conexão com o banco de dados Neon Serverless.
    Usa o connection string armazenado nos segredos do Streamlit.
    """
    # Recupera a URL do banco de dados a partir dos segredos do Streamlit
    db_url = st.secrets.database.DATABASE_URL
    if not db_url:
        raise ValueError(
            'A URL do banco de dados (db_url) não foi encontrada nos segredos do Streamlit.'
        )

    # Cria a engine do SQLAlchemy
    engine = create_engine(db_url)
    return engine


# Inicializa a engine de conexão
engine = init_connection()


def get_state() -> str:
    """
    Busca o valor do campo 'state' no banco de dados.
    """
    table_name = st.secrets.database.NEON_TABLENAME
    with engine.connect() as conn:
        # Usa text() para definir a query e scalar_one() para obter um único resultado
        query = text(f'SELECT state FROM {table_name} LIMIT 1')
        result = conn.execute(query).scalar_one()
        return result


def set_state(state):
    engine = init_connection()
    table_name = st.secrets.database.NEON_TABLENAME

    query = text(f'UPDATE {table_name} SET state = :state')

    with (
        engine.begin() as conn
    ):  # engine.begin() inicia uma transação automaticamente
        conn.execute(query, {'state': state})
        return True
