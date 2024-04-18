import sqlite3


def main():
    DB_PATH = 'user_logs.db'
    with (conn := sqlite3.connect(DB_PATH)):
        user_logs = conn.cursor().execute('SELECT * from user_logs').fetchall()

    for log in user_logs:
        print(log)

    conn.close()


if __name__ == '__main__':
    main()
