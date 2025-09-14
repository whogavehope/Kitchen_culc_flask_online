-- Таблица категорий
DROP TABLE IF EXISTS categories;
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    subcategory TEXT NOT NULL
);

-- Таблица модулей
DROP TABLE IF EXISTS modules;
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    width_min INTEGER,
    width_max INTEGER,
    height_min INTEGER,
    height_max INTEGER,
    depth INTEGER,
    base_price REAL,
    image_filename TEXT,
    options TEXT, -- JSON строка
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Таблица материалов
DROP TABLE IF EXISTS materials;
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- Пленка, пластик, дерево и т.д.
    price REAL NOT NULL
);

-- Таблица цен (для модификаций модулей)
DROP TABLE IF EXISTS prices;
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    extra_price REAL NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- Таблица ставок труда
DROP TABLE IF EXISTS labor_rates;
CREATE TABLE IF NOT EXISTS labor_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    rate REAL NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Таблица заказов
DROP TABLE IF EXISTS orders;
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица позиций заказа
DROP TABLE IF EXISTS order_items;
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    width INTEGER,
    height INTEGER,
    depth INTEGER,
    material_id INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);
