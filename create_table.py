from sqlalchemy import create_engine

# Assuming 'sqlite:///your_database_file.sqlite' is the URI for your SQLite database
engine = create_engine('sqlite:///database.sqlite')

# Establish a connection to the database
conn = engine.connect()

# Execute the SQL query to create the table
conn.execute('''
    CREATE TABLE predictions (
        id INTEGER PRIMARY KEY,
        name TEXT,
        place TEXT,
        latitude FLOAT,
        longitude FLOAT,
        duration INTEGER,
        user_id INTEGER
    )
''')

# Close the connection
conn.close()
