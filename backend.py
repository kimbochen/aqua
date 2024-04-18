import logging
import random
import sqlite3
from datetime import datetime as dt
from pathlib import Path

from fastapi import FastAPI
import aqua

logging.basicConfig(level=logging.INFO)


app = FastAPI()
logging.info('Fast API app loaded.')


DEBUG = False
if not DEBUG:
    query_fn = aqua.StableLM3BQueryEngine('data/').query
    DB_PATH = 'user_logs.db'
else:
    query_fn = lambda query: ''.join(random.choice([str.upper, str.lower])(c) for c in query)
    DB_PATH = 'debug_user_logs.db'
logging.info('Query engine loaded.')


if not Path(DB_PATH).exists():
    with (conn := sqlite3.connect(DB_PATH)):
        conn.cursor().execute('CREATE TABLE user_logs(id, user_id, query, response, quality)')
    conn.close()
    logging.info(f'Database {DB_PATH} created.')


@app.get('/')
def respond(query: str, user_id: str):
    response = query_fn(query)

    qa_id = int(f'{dt.now():%Y%m%d%H%M%S}')
    entry = (qa_id, user_id, query, response, False)
    with (conn := sqlite3.connect(DB_PATH)):
        conn.cursor().execute('INSERT INTO user_logs VALUES(?, ?, ?, ?, ?)', entry)
    conn.close()

    return {'answer': response, 'qa_id': qa_id}


@app.post('/feedback')
def save_feedback(qa_id: int, user_id: str):
    with (conn := sqlite3.connect(DB_PATH)):
        sql_query = 'UPDATE user_logs SET quality = 1 WHERE id = ? AND user_id = ?'
        conn.cursor().execute(sql_query, (qa_id, user_id))
    conn.close()
