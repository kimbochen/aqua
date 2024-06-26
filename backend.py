import logging
import sqlite3
from pathlib import Path
from datetime import datetime as dt

from fastapi import FastAPI

from aqua import init_aqua


logging.basicConfig(level=logging.INFO)
DB_PATH = 'new_user_logs.db'

app = FastAPI()
query_aqua = init_aqua()
logging.info('Fast API app loaded.')


def run_sql_query(*sql_query):
    with (conn := sqlite3.connect(DB_PATH)):
        conn.cursor().execute(*sql_query)
    conn.close()


def log_record(user_id, qtype, query, answer, sources):
    qa_id = int(f'{dt.now():%Y%m%d%H%M%S}')
    entry = (qa_id, user_id, qtype, query, answer, sources, 0)
    run_sql_query('INSERT INTO user_logs VALUES(?, ?, ?, ?, ?, ?, ?)', entry)
    return qa_id


if not Path(DB_PATH).exists():
    run_sql_query('CREATE TABLE user_logs (qa_id, user_id, qtype, query, answer, sources, quality)')
    logging.info(f'Database {DB_PATH} created.')


@app.get('/query')
def query_fn(query: str, user_id: str, qtype: str):
    answer, sources = query_aqua(query, qtype)
    qa_id = log_record(query=query, user_id=user_id, qtype=qtype, answer=answer, sources=sources)
    return {
        'answer': answer,
        'sources': sources,
        'qa_id': qa_id
    }


@app.post('/feedback')
def feedback(qa_id: int, user_id: str, verdict: int):
    sql_query = f'UPDATE user_logs SET quality = {verdict} WHERE qa_id = ? AND user_id = ?'
    run_sql_query(sql_query, (qa_id, user_id))


@app.get('/')
def legacy_query_fn(query: str, user_id: str):
    response = query_fn(query, user_id, 'general')
    ans_src = response['answer'] + '\n\nSources:\n\n' + response['sources']
    return {'answer': ans_src, 'qa_id': response['qa_id']}
