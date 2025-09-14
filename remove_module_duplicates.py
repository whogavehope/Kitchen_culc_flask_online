import sqlite3

DB_FILE = "database.db"

def remove_module_duplicates():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    # Удаляем дубли по имени, оставляем запись с минимальным id
    cursor.execute("""
        DELETE FROM modules
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM modules
            GROUP BY name
        )
    """)
    connection.commit()
    connection.close()
    print("Дубликаты модулей удалены, оставлены только уникальные по имени.")

if __name__ == "__main__":
    remove_module_duplicates()
