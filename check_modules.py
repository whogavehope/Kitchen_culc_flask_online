import sqlite3

def check_modules():
    # Подключаемся к базе
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Выполняем запрос
    cursor.execute("SELECT id, name, image_filename FROM modules LIMIT 5;")
    rows = cursor.fetchall()

    # Выводим результат
    print("id | name | image")
    print("-" * 40)
    for row in rows:
        print(row)

    # Закрываем соединение
    conn.close()

if __name__ == "__main__":
    check_modules()