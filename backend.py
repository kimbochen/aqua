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


query_engine = aqua.StableLM3BQueryEngine('data/indexed')
logging.info('Query engine loaded.')


DEBUG = True
DB_PATH = 'debug_user_logs.db' if DEBUG else 'user_logs.db'

if not Path(DB_PATH).exists():
    with (conn := sqlite3.connect(DB_PATH)):
        conn.cursor().execute('CREATE TABLE user_logs(id, user_id, qtype, query, answer, sources, quality)')
    conn.close()
    logging.info(f'Database {DB_PATH} created.')


def save_to_database(user_id, qtype, query, answer, sources):
    qa_id = int(f'{dt.now():%Y%m%d%H%M%S}')

    with (conn := sqlite3.connect(DB_PATH)):
        entry = (qa_id, user_id, qtype, query, answer, sources, False)
        conn.cursor().execute('INSERT INTO user_logs VALUES(?, ?, ?, ?, ?, ?, ?)', entry)

    conn.close()

    return qa_id


@app.get('/')
def respond(query: str, user_id: str):
    answer, sources = query_engine.query(query)
    qa_id = save_to_database(user_id, 'general', query, answer, sources)
    response = f'{answer}\n\nSources:\n{sources}'
    return {'answer': response, 'qa_id': qa_id}


@app.post('/feedback')
def save_feedback(qa_id: int, user_id: str):
    with (conn := sqlite3.connect(DB_PATH)):
        sql_query = 'UPDATE user_logs SET quality = 1 WHERE id = ? AND user_id = ?'
        conn.cursor().execute(sql_query, (qa_id, user_id))
    conn.close()


@app.get('/asmtq')
def respond_asmtq(query: str, user_id: str, asmt_id: int, q_id: int):
    asmtq_file = f'data/asmts_test/asmt{asmt_id}-q{q_id}.txt'

    if Path(asmtq_file).exists():
        answer, asmtq = query_engine.query_asmt(query, asmtq_file)
        qa_id = save_to_database(user_id, 'asmtq', query, answer, asmtq)
        response = f'{answer}\n\nAssignment Question:\n{asmtq}'
    else:
        print(f'Invalid path {asmtq_file} ')
        response = 'Invalid assignment question.'
        qa_id = None

    return {'answer': response, 'qa_id': qa_id}
