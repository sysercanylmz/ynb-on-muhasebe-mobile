import sqlite3

from app import config


def get_connection():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.BELGE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def init_db():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.BELGE_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS cariler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cari_tipi TEXT DEFAULT 'genel',
            unvan TEXT NOT NULL,
            telefon TEXT,
            email TEXT,
            vergi_dairesi TEXT,
            vergi_no TEXT,
            tc_no TEXT,
            adres TEXT,
            aciklama TEXT,
            aktif INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS kasalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kasa_adi TEXT NOT NULL,
            kasa_tipi TEXT NOT NULL,
            acilis_bakiyesi REAL DEFAULT 0,
            aciklama TEXT,
            aktif INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        if not _column_exists(conn, "kasalar", "acilis_bakiyesi"):
            cur.execute("ALTER TABLE kasalar ADD COLUMN acilis_bakiyesi REAL DEFAULT 0")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS kategoriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategori_tipi TEXT NOT NULL,
            kategori_adi TEXT NOT NULL,
            ust_kategori_id INTEGER,
            aktif INTEGER DEFAULT 1,
            FOREIGN KEY (ust_kategori_id) REFERENCES kategoriler(id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS islem_kayitlari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            islem_tipi TEXT NOT NULL,
            cari_id INTEGER,
            kasa_id INTEGER,
            kategori_id INTEGER,
            tarih TEXT NOT NULL,
            belge_turu TEXT DEFAULT 'belgesiz',
            belge_no TEXT,
            belge_tarihi TEXT,
            baslik TEXT NOT NULL,
            aciklama TEXT,
            tutar REAL NOT NULL DEFAULT 0,
            kdv_orani REAL DEFAULT 0,
            kdv_tutari REAL DEFAULT 0,
            toplam_tutar REAL NOT NULL DEFAULT 0,
            odeme_durumu TEXT DEFAULT 'odendi',
            resmi_kayit INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cari_id) REFERENCES cariler(id),
            FOREIGN KEY (kasa_id) REFERENCES kasalar(id),
            FOREIGN KEY (kategori_id) REFERENCES kategoriler(id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS belge_dosyalari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            islem_id INTEGER NOT NULL,
            dosya_adi TEXT NOT NULL,
            dosya_yolu TEXT NOT NULL,
            dosya_tipi TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (islem_id) REFERENCES islem_kayitlari(id) ON DELETE CASCADE
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS kasa_hareketleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kasa_id INTEGER NOT NULL,
            islem_id INTEGER,
            tarih TEXT NOT NULL,
            hareket_tipi TEXT NOT NULL,
            tutar REAL NOT NULL,
            aciklama TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kasa_id) REFERENCES kasalar(id),
            FOREIGN KEY (islem_id) REFERENCES islem_kayitlari(id) ON DELETE SET NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS cari_hareketleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cari_id INTEGER NOT NULL,
            islem_id INTEGER,
            tarih TEXT NOT NULL,
            hareket_yonu TEXT NOT NULL,
            tutar REAL NOT NULL,
            aciklama TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cari_id) REFERENCES cariler(id),
            FOREIGN KEY (islem_id) REFERENCES islem_kayitlari(id) ON DELETE SET NULL
        )
        """)

        seed_defaults(conn)
        conn.commit()


def seed_defaults(conn):
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM kasalar")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO kasalar (kasa_adi, kasa_tipi, acilis_bakiyesi, aciklama) VALUES (?, ?, ?, ?)",
            [
                ("Nakit Kasa", "nakit", 0, "Varsayılan nakit kasa"),
                ("Banka", "banka", 0, "Varsayılan banka hesabı"),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM kategoriler")
    if cur.fetchone()[0] == 0:
        rows = [
            ("gelir", "Satış Geliri"),
            ("gelir", "Hizmet Geliri"),
            ("gelir", "Diğer Gelir"),
            ("gider", "Kira"),
            ("gider", "Elektrik"),
            ("gider", "Su"),
            ("gider", "İnternet"),
            ("gider", "Telefon"),
            ("gider", "Yakıt"),
            ("gider", "Yemek"),
            ("gider", "Kargo"),
            ("gider", "Personel"),
            ("gider", "Araç Bakım"),
            ("gider", "Ofis Gideri"),
            ("gider", "Malzeme Alımı"),
            ("gider", "Vergi / Harç"),
            ("gider", "Diğer Gider"),
        ]
        cur.executemany(
            "INSERT INTO kategoriler (kategori_tipi, kategori_adi) VALUES (?, ?)",
            rows,
        )
