# Importing necessary libraries
from sqlalchemy import create_engine

# defining constant string for database credentials.
HOST = ""
USER = ""
PASSWORD = ""
PORT = 3306
DATABASE = "project_purchase_pattern_analysis"
TABLE = "mytable"

# Function to get database connection
def db_connect():
    connection_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

    engine = create_engine(connection_url)

    return engine