from sqlalchemy import create_engine, text

# Assuming 'sqlite:///your_database_file.sqlite' is the URI for your SQLite database
engine = create_engine('sqlite:///dp5.sqlite')

# Establish a connection to the database
conn = engine.connect()

# Define the SQL query as a string
sql_query = ('\n'
             '    CREATE TABLE predictions (\n'
             '        id INTEGER PRIMARY KEY,\n'
             '        name TEXT,\n'
             '        place TEXT,\n'
             '        latitude FLOAT,\n'
             '        longitude FLOAT,\n'
             '        duration INTEGER,\n'
             '        user_id INTEGER\n'
             '    )\n')

# Execute the SQL query to create the table
conn.execute(text(sql_query))

# Close the connection
conn.close()
