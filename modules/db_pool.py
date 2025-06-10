from dbutils.pooled_db import PooledDB
import pymysql
from dotenv import load_dotenv
import os
def get_pool() :
    pool = PooledDB(
        creator = pymysql,
        maxconnections = 5,     
        mincached = 3,         
        blocking = True,
        host = "sql5.freesqldatabase.com",
        user = "sql5777334",
        password = os.getenv('DB_password'),
        port = 3306, 
        database = "sql5777334",
        charset = "utf8mb4"
    )