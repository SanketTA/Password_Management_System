import sqlite3

# Connect to the database
conn = sqlite3.connect('passwords.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Select all rows from the 'users' table
cursor.execute('SELECT * FROM passwords')

# Fetch all the rows
rows = cursor.fetchall()

# Display the rows
for row in rows:
    print(row)

# Close the connection
conn.close()
