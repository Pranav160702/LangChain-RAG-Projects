import sqlite3


# Connect to sqlite
connection = sqlite3.connect("student.db")


# Create a Cursor object to insert record, create table
cursor = connection.cursor()

# Create the Table
table_info = """
CREATE TABLE STUD(NAME VARCHAR(25), CLASS VARCHAR(20),
SECTION VARCHAR(25), MARKS INT)
"""


# Executing the Query Over Database
cursor.execute(table_info)


# Insert Some more Records
cursor.execute('''Insert Into STUDENT values('Pranav', 'Data Science', 'A',90)''')
cursor.execute('''Insert Into STUDENT values('John', 'Data Science', 'B', 100)''')
cursor.execute('''Insert Into STUDENT values('Mukesh', 'Data Science', 'A', 86)''')
cursor.execute('''Insert Into STUDENT values('Jacob', 'DEVOPS', 'A', 50)''')
cursor.execute('''Insert Into STUDENT values('Dipesh', 'DEVOPS', 'A', 35)''')
cursor.execute('''Insert Into STUDENT values('Prakash', 'Data Science', 'A', 88)''')
cursor.execute('''Insert Into STUDENT values('Viraj', 'DEVOPS', 'A', 59)''')
cursor.execute('''Insert Into STUDENT values('Akash', 'DEVOPS', 'A', 75)''')


# Display All the Records
print("The Inserted Records are: ")
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)


# Commit Changes in the Database
connection.close()
