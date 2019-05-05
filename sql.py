"""
Created on Mon Mar 19 20:47:10 2018
@author: frank
"""

from constants import SQL_IP_ADDR,SQL_USRNAME,SQL_PASSWD,DBNAME

import pymysql

def open(host=SQL_IP_ADDR,usr=SQL_USRNAME,pw=SQL_PASSWD,db_name=DBNAME):
    conn = pymysql.connect(host=host,
                            user=usr,
                            password=pw,
                            db=db_name,
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    return conn

def close(conn):
    conn.close()

def execute(conn,cmd):
    cur = conn.cursor()
    try:
        cur.execute(cmd)
    except Exception as e:
        return "%s"%e
    return cur.fetchall()

def run(cmd):
    conn = open()
    try:
        result = execute(conn,cmd)
    except Exception as e:
        result = "%s"%e    
    close(conn)
    return result

def get_column_values(conn,table_name,column_name):
    cmd = "SELECT {0} FROM {1}".format(column_name,table_name)
    try:
        return execute(conn,cmd)
    except Exception as e:
        return "%s"%e
    
def main():
    conn = open()
    print(get_column_values(conn,'t_eth_accounts','address'))
    close(conn)

if __name__ == "__main__":
    main()
    
    
