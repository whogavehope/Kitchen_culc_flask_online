import sqlite3

# Подключаемся к базе данных (файл database.db будет создан автоматически)
connection = sqlite3.connect('database.db')

# Открываем файл schema.sql и выполняем его скрипт
with open('schema.sql') as f:
    connection.executescript(f.read())

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

