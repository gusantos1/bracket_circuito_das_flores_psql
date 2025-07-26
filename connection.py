import streamlit as st
from databricks import sql


connection = sql.connect(
    server_hostname=st.secrets.database.HOSTNAME,
    http_path=st.secrets.database.HOSTPATH,
    access_token=st.secrets.database.HOSTTOKEN,
)

def get_state():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT state FROM {st.secrets.database.TABLENAME}")
        result = cursor.fetchall()
        return result[0].asDict()['state']

def set_state(state):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE {st.secrets.database.TABLENAME} SET state = ?", (state,))
        connection.commit()
        return True