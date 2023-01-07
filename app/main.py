from starlette.exceptions import HTTPException
from fastapi import FastAPI
import sqlite3
import datetime

app = FastAPI()

route_db = "route.db"
main_db = "main.db"

@app.get("/meta/time")
async def server_time():
    return {"date_time": datetime.datetime.now()}

@app.get("/meta/version")
async def server_ver():
    # ちゃんと別ファイルで管理したい(できるとは言ってない)
    return {"version": "hoge"}

@app.get("/route/") #visibilityつくってるんだからそれはこっちで処理するべきかも？
async def route_all():
    connection = sqlite3.connect(route_db)
    cursor = connection.cursor()

    sql_select_all = 'SELECT id, route_name, visibility from routes' 
    cursor.execute(sql_select_all)
    routes_result = cursor.fetchall()

    return {"test": str(routes_result)}