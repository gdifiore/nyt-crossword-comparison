import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database=os.environ['DATABASE'],
        user=os.environ['DATABASE_USERNAME'],
        password=os.environ['DATABASE_PASSWORD'])

cur = conn.cursor()

# create nyt puzzle completion table
# id just counts input
# completion time is format 00:00:00, this is the user input
# timestamp is time entry was put in
cur.execute('DROP TABLE IF EXISTS puzzle_completion;')
cur.execute('CREATE TABLE puzzle_completion ('
                    'id SERIAL PRIMARY KEY,'
                    'completion_time INTERVAL,'
                    'timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'
                )

conn.commit()

cur.close()
conn.close()