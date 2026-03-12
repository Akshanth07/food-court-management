-- ============================================================
--   SMART FOOD COURT MANAGEMENT SYSTEM — MySQL Schema
--   Run this file in phpMyAdmin or MySQL CLI before starting
-- ============================================================

CREATE DATABASE IF NOT EXISTS foodcourt_db;
USE foodcourt_db;

-- ─────────────────────────────────────────
-- 1. USERS (customers, vendors, admins)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,           -- bcrypt hash
    role        ENUM('customer','vendor','admin') DEFAULT 'customer',
    phone       VARCHAR(15),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- 2. VENDORS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    emoji       VARCHAR(10) DEFAULT '🍽',
    is_open     TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────
-- 3. MENU ITEMS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS menu_items (
    item_id     INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id   INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(8,2) NOT NULL,
    emoji       VARCHAR(10) DEFAULT '🍱',
    is_veg      TINYINT(1) DEFAULT 0,
    is_spicy    TINYINT(1) DEFAULT 0,
    is_available TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────
-- 4. ORDERS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    token_number    INT NOT NULL,
    subtotal        DECIMAL(8,2) NOT NULL,
    tax             DECIMAL(8,2) DEFAULT 0,
    discount        DECIMAL(8,2) DEFAULT 0,
    total           DECIMAL(8,2) NOT NULL,
    status          ENUM('placed','confirmed','preparing','ready','collected','cancelled') DEFAULT 'placed',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────
-- 5. ORDER ITEMS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id   INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    item_id         INT NOT NULL,
    vendor_id       INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1,
    unit_price      DECIMAL(8,2) NOT NULL,
    item_status     ENUM('pending','preparing','ready','done') DEFAULT 'pending',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- ─────────────────────────────────────────
-- 6. TOKEN SEQUENCE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS token_sequence (
    id          INT PRIMARY KEY DEFAULT 1,
    last_token  INT DEFAULT 0
);
INSERT IGNORE INTO token_sequence VALUES (1, 40);

-- ─────────────────────────────────────────
-- SAMPLE DATA
-- ─────────────────────────────────────────

-- Users (passwords are bcrypt of "password123")
INSERT IGNORE INTO users (user_id, name, email, password, role, phone) VALUES
(1, 'Admin User',    'admin@foodcourt.com',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin',    '9000000001'),
(2, 'Ravi Kumar',    'ravi@spicegarden.com',  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'vendor',   '9000000002'),
(3, 'Priya Singh',   'priya@burgerbarn.com',  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'vendor',   '9000000003'),
(4, 'Chen Wei',      'chen@wokroll.com',      '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'vendor',   '9000000004'),
(5, 'Marco D',       'marco@sliceheaven.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'vendor',   '9000000005'),
(6, 'Test Customer', 'customer@test.com',     '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'customer', '9000000006');

-- Vendors
INSERT IGNORE INTO vendors (vendor_id, user_id, name, description, emoji, is_open) VALUES
(1, 2, 'Spice Garden',  'Authentic North Indian cuisine',      '🌶',  1),
(2, 3, 'Burger Barn',   'American burgers & fast food',        '🍔',  1),
(3, 4, 'Wok & Roll',    'Indo-Chinese stir fry & noodles',    '🥢',  1),
(4, 5, 'Slice Heaven',  'Wood-fired pizzas & garlic bread',   '🍕',  1);

-- Menu Items — Spice Garden
INSERT IGNORE INTO menu_items (item_id, vendor_id, name, description, price, emoji, is_veg, is_spicy) VALUES
(1,  1, 'Butter Chicken',   'Creamy tomato-based curry with tender chicken', 180.00, '🍛', 0, 1),
(2,  1, 'Paneer Tikka',     'Marinated cottage cheese grilled to perfection',140.00, '🧆', 1, 0),
(3,  1, 'Dal Makhani',      'Slow-cooked black lentils in butter and cream', 120.00, '🫕', 1, 0),
(4,  1, 'Chicken Biryani',  'Fragrant basmati with spiced chicken',          200.00, '🍱', 0, 1),
(5,  1, 'Palak Paneer',     'Spinach gravy with soft paneer cubes',          130.00, '🥘', 1, 0);

-- Menu Items — Burger Barn
INSERT IGNORE INTO menu_items (item_id, vendor_id, name, description, price, emoji, is_veg, is_spicy) VALUES
(6,  2, 'Classic Burger',  'Double patty with lettuce and house sauce',  130.00, '🍔', 0, 0),
(7,  2, 'Crispy Fries',    'Golden shoestring fries with seasoning',      70.00, '🍟', 1, 0),
(8,  2, 'Veggie Wrap',     'Grilled vegetables with hummus in tortilla',  110.00, '🌯', 1, 0),
(9,  2, 'Cheese Burger',   'Triple cheese smash burger',                  160.00, '🍔', 0, 0),
(10, 2, 'Milkshake',       'Thick creamy vanilla or chocolate shake',      90.00, '🥤', 1, 0);

-- Menu Items — Wok & Roll
INSERT IGNORE INTO menu_items (item_id, vendor_id, name, description, price, emoji, is_veg, is_spicy) VALUES
(11, 3, 'Hakka Noodles',   'Stir-fried noodles with vegetables and soy', 100.00, '🍜', 1, 1),
(12, 3, 'Chilli Chicken',  'Crispy chicken in spicy Indo-Chinese sauce',  160.00, '🍗', 0, 1),
(13, 3, 'Fried Rice',      'Wok-tossed basmati with egg and veggies',     90.00, '🍚', 0, 0),
(14, 3, 'Spring Rolls',    'Crispy vegetable spring rolls with sauce',     80.00, '🥟', 1, 0);

-- Menu Items — Slice Heaven
INSERT IGNORE INTO menu_items (item_id, vendor_id, name, description, price, emoji, is_veg, is_spicy) VALUES
(15, 4, 'Margherita Pizza',   'Classic thin-crust with mozzarella and basil', 200.00, '🍕', 1, 0),
(16, 4, 'BBQ Chicken Pizza',  'Smoky BBQ sauce with grilled chicken',          250.00, '🍕', 0, 0),
(17, 4, 'Garlic Bread',       'Toasted sourdough with herb garlic butter',      80.00, '🥖', 1, 0),
(18, 4, 'Pasta Arrabbiata',   'Penne in spicy tomato sauce',                   160.00, '🍝', 1, 1);

-- Sample orders
INSERT IGNORE INTO orders (order_id, user_id, token_number, subtotal, tax, discount, total, status) VALUES
(1, 6, 41, 300.00, 15.00, 0,     315.00, 'collected'),
(2, 6, 42, 420.00, 21.00, 42.00, 399.00, 'collected'),
(3, 6, 43, 180.00,  9.00, 0,     189.00, 'ready'),
(4, 6, 44, 500.00, 25.00, 50.00, 475.00, 'preparing'),
(5, 6, 45, 260.00, 13.00, 0,     273.00, 'placed');

INSERT IGNORE INTO order_items (order_id, item_id, vendor_id, quantity, unit_price, item_status) VALUES
(1, 1, 1, 1, 180.00, 'done'),
(1, 3, 1, 1, 120.00, 'done'),
(2, 6, 2, 2, 130.00, 'done'),
(2, 2, 1, 1, 140.00, 'done'),
(3, 1, 1, 1, 180.00, 'ready'),
(4, 1, 1, 2, 180.00, 'preparing'),
(4, 2, 1, 1, 140.00, 'preparing'),
(5, 11, 3, 1, 100.00, 'pending'),
(5, 15, 4, 1, 160.00, 'pending');
