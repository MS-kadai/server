from starlette.exceptions import HTTPException
from pydantic import BaseModel
from fastapi import FastAPI
import sqlite3
import datetime
import os

app = FastAPI()

route_db = "route.db"
tracker_db = "tracker.db"
main_db = "main.db"
session_db = "sessions.db"

class createSession(BaseModel):
    session_id: str
    route_id: str


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

    sql_select_all = 'SELECT id, route_name, visibility, active_session FROM routes' 
    cursor.execute(sql_select_all)
    routes_result = cursor.fetchall()

    connection.close()
    return {"length": len(routes_result), "routes": routes_result}

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
async def create_session(createSession: createSession): #セッションIDはUUIDを想定
    connection_route_db = sqlite3.connect(route_db)
    connection_route_db.row_factory = dict_factory
    cursor_route_db = connection_route_db.cursor()
    sql_select_active_session = "SELECT active_session FROM routes WHERE id = "+createSession.route_id
    cursor_route_db.execute(sql_select_active_session)
    result_route_db = cursor_route_db.fetchone()
    result_route_db_dict = dict(result_route_db)

    if result_route_db_dict["active_session"] != None: #既にセッションがある場合
        raise HTTPException(status_code=500, detail="SESSION_ALREADY_EXISTS")

    connection = sqlite3.connect(session_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_create_table = 'CREATE TABLE IF NOT EXISTS "'+createSession.session_id+'" (eventId integer, point_id integer, timestamp datetime)' #テーブル作成
    cursor.execute(sql_create_table)
    connection.commit()

    sql_update_active_session = 'UPDATE routes SET active_session = "'+createSession.session_id+'" WHERE id = '+createSession.route_id
    cursor_route_db.execute(sql_update_active_session)
    connection_route_db.commit()

    connection.close()
    connection_route_db.close()
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

@app.delete("/session/delete")  #即削除じゃなくてフラグ建ててあとから見返したりもできるようにするべきかも
async def delete_session(session_id: str):

    connection_route_db = sqlite3.connect(route_db)
    connection_route_db.row_factory = dict_factory
    cursor_route_db = connection_route_db.cursor()
    sql_delete_active_session = 'UPDATE routes SET active_session = NULL WHERE active_session = "'+session_id+'"'
    cursor_route_db.execute(sql_delete_active_session)
    connection_route_db.commit()

    connection = sqlite3.connect(session_db)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    sql_delete_table = 'DROP TABLE "'+session_id+'"' 
    cursor.execute(sql_delete_table)
    connection.commit()

    connection.close()
    connection_route_db.close()
    return {"result": "deleted"}



