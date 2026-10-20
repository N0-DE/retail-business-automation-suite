-- ============================================================
-- Retail Damage & Claims Management Database Schema
-- Compatible with SQLite and Microsoft SQL Server
-- ============================================================

-- Track Damage Items
CREATE TABLE IF NOT EXISTS DAMAGE (
    slno INTEGER PRIMARY KEY,
    barcode VARCHAR(100),
    item_name VARCHAR(255),
    supplier VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    entry_date VARCHAR(50),
    cash VARCHAR(10) DEFAULT 'no',
    taken VARCHAR(10) DEFAULT 'no'
);

-- Serial Number Counter
CREATE TABLE IF NOT EXISTS SLNO (
    current_val INTEGER DEFAULT 1
);

-- Retail ERP Product Batches (Lookup Table)
CREATE TABLE IF NOT EXISTS ProductBatches (
    ManualBarcode VARCHAR(100) PRIMARY KEY,
    RefItemName VARCHAR(255),
    SupplierLedgerID INTEGER
);

-- Suppliers & Parties
CREATE TABLE IF NOT EXISTS Parties (
    LedgerID INTEGER PRIMARY KEY,
    PartyName VARCHAR(255),
    PartyType VARCHAR(50)
);

-- Seed Initial Mock Data
INSERT OR IGNORE INTO SLNO (current_val) VALUES (1001);

INSERT OR IGNORE INTO Parties (LedgerID, PartyName, PartyType) VALUES 
(1, 'Nestle Distribution Ltd', 'supp'),
(2, 'Unilever Consumer Goods', 'supp'),
(3, 'Britannia Foods Supply', 'supp'),
(4, 'P&G Retail Distro', 'supp');

INSERT OR IGNORE INTO ProductBatches (ManualBarcode, RefItemName, SupplierLedgerID) VALUES 
('8901058852395', 'Nescafe Classic 50g Glass Jar', 1),
('8901030383749', 'Dove Deep Moisture Shampoo 340ml', 2),
('8901063012487', 'Britannia Good Day Butter Cookies', 3),
('8901234567890', 'Gillette Mach3 Razor Cartridge', 4);
