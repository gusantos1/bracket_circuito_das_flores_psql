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
@st.cache_resource
def init_connection():
    """
    Inicializa a conexão com o banco de dados Neon Serverless.
    Usa o connection string armazenado nos segredos do Streamlit.
    """
    # Recupera a URL do banco de dados a partir dos segredos do Streamlit
    db_url = st.secrets.database.DATABASE_URL
    if not db_url:
        raise ValueError("A URL do banco de dados (db_url) não foi encontrada nos segredos do Streamlit.")
    
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
        query = text(f"SELECT state FROM {table_name} LIMIT 1")
        result = conn.execute(query).scalar_one()
        return result

def set_state(new_state: str) -> bool:
    """
    Atualiza o valor do campo 'state' no banco de dados.
    """
    table_name = st.secrets.database.NEON_TABLENAME
    with engine.connect() as conn:
        # O bloco `with conn.begin() as tx:` inicia uma transação que é
        # automaticamente confirmada (commit) em caso de sucesso ou
        # desfeita (rollback) em caso de erro.
        with conn.begin() as tx:
            # Usa placeholders (:new_state) para prevenir SQL Injection
            query = text(f"UPDATE {table_name} SET state = :new_state")
            conn.execute(query, {"new_state": new_state})
    return True