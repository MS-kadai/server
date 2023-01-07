from starlette.exceptions import HTTPException
from fastapi import FastAPI
import sqlite3
import datetime

app = FastAPI()

route_db = "route.db"
main_db = "main.db"

# https://qiita.com/nekobake/items/aebd40e07037fc7911bc
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/meta/time")
async def server_time():
    return {"date_time": datetime.datetime.now()}

@app.get("/meta/version")
async def server_ver():
    # ちゃんと別ファイルで管理したい(できるとは言ってない)
    return {"version": "hoge"}

@app.get("/routes/") #visibilityつくってるんだからそれはこっちで処理するべきかも？
async def route_all():
    connection = sqlite3.connect(route_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT id, route_name, visibility FROM routes' 
    cursor.execute(sql_select_all)
    routes_result = cursor.fetchall()

    return {"rotues": routes_result}

@app.get("/routes/{route_id}")
async def get_route(route_id: str):
    targetdb_name = 'route_' + route_id + ".db"
    print("[DEBUG] Target: "+targetdb_name) #debug

    connection = sqlite3.connect(targetdb_name)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT * FROM route'
    cursor.execute(sql_select_all)
    result = cursor.fetchall()

    return {"routeId": route_id, "route": result}