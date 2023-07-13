import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from CONFIG import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DATABASE, MYSQL_CHARSET

# 创建数据库 pricemonitor
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE pricemonitor CHARACTER SET utf8")

# 关闭游标和连接
cursor.close()
conn.close()

# 连接数据库 pricemonitor
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

# 初始化pricemonitor
excel_data = pd.read_excel("prices_onlyItem.xlsx",sheet_name=None)

cursor = conn.cursor()

# 遍历每个 sheet
for sheet_name, df in excel_data.items():
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {sheet_name} ("

    for column in df.columns:
        column_name = column.replace(" ", "_")  # 将空格替换为下划线，以防止在列名中引起问题
        column_type = "VARCHAR(255)"  
        create_table_sql += f"{column_name} {column_type}, "

    create_table_sql = create_table_sql.rstrip(", ")  
    create_table_sql += ")"

    cursor.execute(create_table_sql)

conn.commit()

conn = "mysql+pymysql://{}:{}@{}:{}/pricemonitor?charset={}".format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST,
                                                                          MYSQL_PORT, MYSQL_CHARSET)
engine = create_engine(conn)

# engine = create_engine("mysql+pymysql://root:1234@localhost:3306/pricemonitor")


# 写入excel数据
for sheet_name, df in excel_data.items():
    df.to_sql(sheet_name, con=engine, if_exists='append', index=False)

engine.dispose()