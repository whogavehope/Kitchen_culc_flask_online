-- categories
DROP TABLE IF EXISTS categories;
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    subcategory TEXT NOT NULL
);

-- modules
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
    options TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- materials
DROP TABLE IF EXISTS materials;
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    price REAL NOT NULL
);

-- prices (extra by module/material)
DROP TABLE IF EXISTS prices;
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    extra_price REAL NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

-- labor rates
DROP TABLE IF EXISTS labor_rates;
CREATE TABLE IF NOT EXISTS labor_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    rate REAL NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- orders
DROP TABLE IF EXISTS orders;
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- order items (с колонкой options для хранения JSON с опциями)
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
    options TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);