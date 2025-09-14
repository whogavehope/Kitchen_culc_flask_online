import sqlite3
import pandas as pd
import json

DB_FILE = "database.db"
EXCEL_FILE_MODULES = "modules_data.xlsx"
EXCEL_FILE_ADDITIONAL = "additional_data.xlsx"

def update_modules():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Создаём таблицу modules, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category_id INTEGER NOT NULL,
        width_min INTEGER,
        width_max INTEGER,
        height_min INTEGER,
        height_max INTEGER,
        depth INTEGER,
        base_price REAL,
        image_filename TEXT,
        options TEXT
    )
    """)
    connection.commit()

    # Загружаем данные модулей
    try:
        df_modules = pd.read_excel(EXCEL_FILE_MODULES)
        for _, row in df_modules.iterrows():
            options = row.get('options', '{}')
            if isinstance(options, dict):
                options = json.dumps(options)
            elif pd.isna(options):
                options = '{}'

            # Проверяем, есть ли модуль с таким именем
            cursor.execute("SELECT id FROM modules WHERE name = ?", (row['name'],))
            existing = cursor.fetchone()

            if existing:
                # Обновляем существующий модуль
                cursor.execute("""
                    UPDATE modules
                    SET category_id=?, width_min=?, width_max=?, height_min=?, height_max=?, depth=?, base_price=?, image_filename=?, options=?
                    WHERE id=?
                """, (
                    row['category_id'],
                    row.get('width_min'),
                    row.get('width_max'),
                    row.get('height_min'),
                    row.get('height_max'),
                    row.get('depth'),
                    row.get('base_price'),
                    row.get('image_filename', ''),
                    options,
                    existing[0]
                ))
            else:
                # Вставляем новый модуль
                cursor.execute("""
                    INSERT INTO modules (name, category_id, width_min, width_max, height_min, height_max, depth, base_price, image_filename, options)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['name'],
                    row['category_id'],
                    row.get('width_min'),
                    row.get('width_max'),
                    row.get('height_min'),
                    row.get('height_max'),
                    row.get('depth'),
                    row.get('base_price'),
                    row.get('image_filename', ''),
                    options
                ))

    except FileNotFoundError:
        print(f"Файл {EXCEL_FILE_MODULES} не найден. Пропускаем модули.")

    # Загружаем новые таблицы из additional_data.xlsx
    try:
        xls = pd.ExcelFile(EXCEL_FILE_ADDITIONAL)

        # materials
        if "materials" in xls.sheet_names:
            df_materials = pd.read_excel(EXCEL_FILE_ADDITIONAL, sheet_name="materials")
            for _, row in df_materials.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO materials (name, type, price) VALUES (?, ?, ?)
                """, (row['name'], row['type'], row['price']))

        # prices
        if "prices" in xls.sheet_names:
            df_prices = pd.read_excel(EXCEL_FILE_ADDITIONAL, sheet_name="prices")
            for _, row in df_prices.iterrows():
                cursor.execute("""
                    INSERT INTO prices (module_id, material_id, extra_price) VALUES (?, ?, ?)
                """, (row['module_id'], row['material_id'], row['extra_price']))

        # labor_rates
        if "labor_rates" in xls.sheet_names:
            df_rates = pd.read_excel(EXCEL_FILE_ADDITIONAL, sheet_name="labor_rates")
            for _, row in df_rates.iterrows():
                cursor.execute("""
                    INSERT INTO labor_rates (module_id, rate) VALUES (?, ?)
                """, (row['module_id'], row['rate']))

    except FileNotFoundError:
        print(f"Файл {EXCEL_FILE_ADDITIONAL} не найден. Пропускаем дополнительные таблицы.")

    connection.commit()
    connection.close()
    print("Данные из Excel успешно загружены и обновлены во всех таблицах!")

if __name__ == "__main__":
    update_modules()
