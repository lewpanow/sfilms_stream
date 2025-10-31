import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except EnvironmentError:
    pass

sql_uri = os.getenv("DATABASE_URL")