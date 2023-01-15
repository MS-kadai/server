from starlette.exceptions import HTTPException
from fastapi import FastAPI
import sqlite3
import datetime
import os

app = FastAPI()

route_db = "route.db"
tracker_db = "tracker.db"
main_db = "main.db"
session_db = "sessions.db"

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
    #TODO ちゃんと別ファイルで管理したい(できるとは言ってない)
    return {"version": "hoge"}

@app.get("/route/list") #TODO visibilityつくってるんだからそれはこっちで処理するべきかも？
async def route_all():

    if os.path.exists(route_db): #データベース存在チェック
        pass
    else:
        raise HTTPException(status_code=500, detail=route_db+"_DOES_NOT_EXIST")

    connection = sqlite3.connect(route_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT id, route_name, visibility FROM routes' 
    cursor.execute(sql_select_all)
    routes_result = cursor.fetchall()

    connection.close()
    return {"length": len(routes_result), "rotues": routes_result}

@app.get("/route/{route_id}")
async def get_route(route_id: str):
    targetdb_name = 'route_' + route_id + ".db"
    print("[DEBUG] Target: "+targetdb_name) #debug

    if os.path.exists(targetdb_name): #データベース存在チェック
        pass
    else:
        raise HTTPException(status_code=500, detail=targetdb_name+"_DOES_NOT_EXIST")

    connection = sqlite3.connect(targetdb_name)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT * FROM route'
    cursor.execute(sql_select_all)
    result = cursor.fetchall()

    connection.close()
    return {"length": len(result), "route": result}

@app.get("/tracker/list")
async def tracker_all():
    if os.path.exists(tracker_db): #データベース存在チェック
        pass
    else:
        raise HTTPException(status_code=500, detail=tracker_db+"_DOES_NOT_EXIST")

    connection = sqlite3.connect(tracker_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT * FROM trackers'
    cursor.execute(sql_select_all)
    result = cursor.fetchall()

    connection.close()
    return {"length": len(result), "trackers": result}

@app.get("/tracker/{tracker_id}")
async def get_tracker(tracker_id: str):
    if os.path.exists(tracker_db): #データベース存在チェック
        pass
    else:
        raise HTTPException(status_code=500, detail=tracker_db+"_DOES_NOT_EXIST")

    connection = sqlite3.connect(tracker_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT * FROM tracker_'+tracker_id
    cursor.execute(sql_select_all)
    result = cursor.fetchall()

    connection.close()
    return {"tracker_id": tracker_id, "detail": result} 

@app.post("/session/create")
async def create_session(session_id: str): #セッションIDはUUIDを想定
    connection = sqlite3.connect(session_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_create_table = 'CREATE TABLE IF NOT EXISTS "'+session_id+'" (eventId integer, point_id integer, timestamp datetime)' #テーブル作成
    cursor.execute(sql_create_table)
    connection.commit()

    connection.close()
    return {"result": "created"} #普通にレスポンスコードでやるべきだとおもう、というかこれだと作られなくてもわからなくなる(TODO そのうちなんとかする)

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    connection = sqlite3.connect(session_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_select_all = 'SELECT * FROM "'+session_id+'"' #TODO 並べ替え
    cursor.execute(sql_select_all)
    result = cursor.fetchall()

    connection.close()
    return {"length": len(result), "result": result}
    #TODO セッション作成日時とかを別のデータベースで管理するべきかも（今の仕様だと存在してるセッションを取得するのがめんどくさくなりそう）

#TODO セッション終了を作らないといけない（一定期間後に削除してほしい、時間があったら実装する）

