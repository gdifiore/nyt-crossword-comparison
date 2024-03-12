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
                    'completion_time_in_sec INT,'
                    'timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'
                )

cur.execute('INSERT INTO puzzle_completion (completion_time_in_sec)'
            'VALUES (%s)',
            (103,)
            )
'''
postgresql to convert s to m:ss

SELECT
  completion_time_in_sec,
  TO_CHAR((completion_time_in_sec / 60)::integer, 'FM999') || ':' || TO_CHAR(completion_time_in_sec % 60, 'FM00') AS formatted_time
FROM
  puzzle_completion;

'''

conn.commit()

cur.close()
conn.close()