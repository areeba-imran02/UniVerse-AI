import json
from .auth import connect
def save_project(user_id,title,discipline,task_type,prompt,result):
    with connect() as c:
        cur=c.execute("INSERT INTO projects(user_id,title,discipline,task_type,prompt,result_json,status) VALUES(?,?,?,?,?,?,?)",(int(user_id),title[:160],discipline,task_type,prompt,json.dumps(result,ensure_ascii=False),"completed"))
        return cur.lastrowid
def list_projects(user_id):
    with connect() as c: rows=c.execute("SELECT * FROM projects WHERE user_id=? ORDER BY id DESC",(int(user_id),)).fetchall()
    return [{"id":r["id"],"title":r["title"],"discipline":r["discipline"],"task_type":r["task_type"],"prompt":r["prompt"],"result":json.loads(r["result_json"]),"status":r["status"],"created_at":r["created_at"]} for r in rows]
def delete_project(user_id,project_id):
    with connect() as c:c.execute("DELETE FROM projects WHERE user_id=? AND id=?",(int(user_id),int(project_id)))
