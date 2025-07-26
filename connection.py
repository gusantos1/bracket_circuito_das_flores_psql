import tomllib
import base64
from databricks import sql

def load_config(path="config.toml"):
    with open(path, "rb") as f:
            return tomllib.load(f)
    

config = load_config().get('database')

connection = sql.connect(
    server_hostname=config.get('HOSTNAME'),
    http_path=config.get('HOSTPATH'),
    access_token=config.get('HOSTTOKEN'),
)

def get_state():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT state FROM {config.get('TABLENAME')}")
        result = cursor.fetchall()
        return result[0].asDict()['state']

def set_state(state):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE {config.get('TABLENAME')} SET state = ?", (state,))
        connection.commit()
        return True
