from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from app import config
from app.database import get_connection
from app.helpers import today_str


# -----------------------------------------------------------------------------
# Genel yardımcı veritabanı fonksiyonları
# -----------------------------------------------------------------------------
def fetch_all(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


# -----------------------------------------------------------------------------
# Cari işlemleri
# -----------------------------------------------------------------------------
def list_cariler(include_inactive: bool = False):
    where = "" if include_inactive else "WHERE aktif = 1"
    return fetch_all(f"SELECT * FROM cariler {where} ORDER BY unvan COLLATE NOCASE")


def get_cari(cari_id):
    return fetch_one("SELECT * FROM cariler WHERE id = ?", (cari_id,))


def insert_cari(data):
    return execute(
        """
        INSERT INTO cariler
        (cari_tipi, unvan, telefon, email, vergi_dairesi, vergi_no, tc_no, adres, aciklama)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("cari_tipi"),
            data.get("unvan"),
            data.get("telefon"),
            data.get("email"),
            data.get("vergi_dairesi"),
            data.get("vergi_no"),
            data.get("tc_no"),
            data.get("adres"),
            data.get("aciklama"),
        ),
    )


def update_cari(cari_id, data):
    execute(
        """
        UPDATE cariler SET
            cari_tipi = ?,
            unvan = ?,
            telefon = ?,
            email = ?,
            vergi_dairesi = ?,
            vergi_no = ?,
            tc_no = ?,
            adres = ?,
            aciklama = ?
        WHERE id = ?
        """,
        (
            data.get("cari_tipi"),
            data.get("unvan"),
            data.get("telefon"),
            data.get("email"),
            data.get("vergi_dairesi"),
            data.get("vergi_no"),
            data.get("tc_no"),
            data.get("adres"),
            data.get("aciklama"),
            cari_id,
        ),
    )
    return cari_id


def delete_cari(cari_id):
    execute("UPDATE cariler SET aktif = 0 WHERE id = ?", (cari_id,))


# -----------------------------------------------------------------------------
# Kasa / banka işlemleri
# -----------------------------------------------------------------------------
def list_kasalar(include_inactive: bool = False):
    where = "" if include_inactive else "WHERE k.aktif = 1"
    return fetch_all(
        f"""
        SELECT
            k.*,
            COALESCE(
                SUM(
                    CASE
                        WHEN kh.hareket_tipi = 'giris' THEN kh.tutar
                        WHEN kh.hareket_tipi = 'cikis' THEN -kh.tutar
                        ELSE 0
                    END
                ),
                0
            ) AS bakiye
        FROM kasalar k
        LEFT JOIN kasa_hareketleri kh ON kh.kasa_id = k.id
        {where}
        GROUP BY k.id
        ORDER BY k.kasa_adi COLLATE NOCASE
        """
    )


def get_kasa(kasa_id):
    return fetch_one("SELECT * FROM kasalar WHERE id = ?", (kasa_id,))


def insert_kasa(data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO kasalar (kasa_adi, kasa_tipi, acilis_bakiyesi, aciklama)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.get("kasa_adi"),
                data.get("kasa_tipi"),
                data.get("acilis_bakiyesi") or 0,
                data.get("aciklama"),
            ),
        )
        kasa_id = cur.lastrowid
        _set_opening_balance(cur, kasa_id, data.get("acilis_bakiyesi") or 0)
        conn.commit()
        return kasa_id


def update_kasa(kasa_id, data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE kasalar SET
                kasa_adi = ?,
                kasa_tipi = ?,
                acilis_bakiyesi = ?,
                aciklama = ?
            WHERE id = ?
            """,
            (
                data.get("kasa_adi"),
                data.get("kasa_tipi"),
                data.get("acilis_bakiyesi") or 0,
                data.get("aciklama"),
                kasa_id,
            ),
        )
        _set_opening_balance(cur, kasa_id, data.get("acilis_bakiyesi") or 0)
        conn.commit()
        return kasa_id


def delete_kasa(kasa_id):
    execute("UPDATE kasalar SET aktif = 0 WHERE id = ?", (kasa_id,))


def _set_opening_balance(cur, kasa_id, amount):
    cur.execute(
        "DELETE FROM kasa_hareketleri WHERE kasa_id = ? AND islem_id IS NULL AND aciklama = ?",
        (kasa_id, "Açılış Bakiyesi"),
    )
    amount = float(amount or 0)
    if amount == 0:
        return

    hareket_tipi = "giris" if amount > 0 else "cikis"
    cur.execute(
        """
        INSERT INTO kasa_hareketleri
        (kasa_id, islem_id, tarih, hareket_tipi, tutar, aciklama)
        VALUES (?, NULL, ?, ?, ?, ?)
        """,
        (kasa_id, today_str(), hareket_tipi, abs(amount), "Açılış Bakiyesi"),
    )


# -----------------------------------------------------------------------------
# Kategori işlemleri
# -----------------------------------------------------------------------------
def list_kategoriler(include_inactive: bool = False):
    where = "" if include_inactive else "WHERE aktif = 1"
    return fetch_all(
        f"SELECT * FROM kategoriler {where} ORDER BY kategori_tipi, kategori_adi COLLATE NOCASE"
    )


def list_kategoriler_by_tip(kategori_tipi: str):
    return fetch_all(
        """
        SELECT * FROM kategoriler
        WHERE aktif = 1 AND kategori_tipi = ?
        ORDER BY kategori_adi COLLATE NOCASE
        """,
        (kategori_tipi,),
    )


def get_kategori(kategori_id):
    return fetch_one("SELECT * FROM kategoriler WHERE id = ?", (kategori_id,))


def insert_kategori(data):
    return execute(
        "INSERT INTO kategoriler (kategori_tipi, kategori_adi) VALUES (?, ?)",
        (data.get("kategori_tipi"), data.get("kategori_adi")),
    )


def update_kategori(kategori_id, data):
    execute(
        "UPDATE kategoriler SET kategori_tipi = ?, kategori_adi = ? WHERE id = ?",
        (data.get("kategori_tipi"), data.get("kategori_adi"), kategori_id),
    )
    return kategori_id


def delete_kategori(kategori_id):
    execute("UPDATE kategoriler SET aktif = 0 WHERE id = ?", (kategori_id,))


# -----------------------------------------------------------------------------
# İşlem kayıtları
# -----------------------------------------------------------------------------
def list_islemler(limit=200):
    return fetch_all(
        """
        SELECT
            i.*,
            c.unvan AS cari_unvan,
            k.kasa_adi,
            kt.kategori_adi,
            (
                SELECT COUNT(*) FROM belge_dosyalari bd WHERE bd.islem_id = i.id
            ) AS belge_sayisi
        FROM islem_kayitlari i
        LEFT JOIN cariler c ON c.id = i.cari_id
        LEFT JOIN kasalar k ON k.id = i.kasa_id
        LEFT JOIN kategoriler kt ON kt.id = i.kategori_id
        ORDER BY i.tarih DESC, i.id DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_islem(islem_id):
    return fetch_one(
        """
        SELECT
            i.*,
            c.unvan AS cari_unvan,
            k.kasa_adi,
            kt.kategori_adi
        FROM islem_kayitlari i
        LEFT JOIN cariler c ON c.id = i.cari_id
        LEFT JOIN kasalar k ON k.id = i.kasa_id
        LEFT JOIN kategoriler kt ON kt.id = i.kategori_id
        WHERE i.id = ?
        """,
        (islem_id,),
    )


def insert_islem(data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO islem_kayitlari
            (islem_tipi, cari_id, kasa_id, kategori_id, tarih, belge_turu, belge_no,
             belge_tarihi, baslik, aciklama, tutar, kdv_orani, kdv_tutari,
             toplam_tutar, odeme_durumu, resmi_kayit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            _islem_params(data),
        )
        islem_id = cur.lastrowid
        _create_related_movements(cur, islem_id, data)
        conn.commit()
        return islem_id


def update_islem(islem_id, data):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE islem_kayitlari SET
                islem_tipi = ?,
                cari_id = ?,
                kasa_id = ?,
                kategori_id = ?,
                tarih = ?,
                belge_turu = ?,
                belge_no = ?,
                belge_tarihi = ?,
                baslik = ?,
                aciklama = ?,
                tutar = ?,
                kdv_orani = ?,
                kdv_tutari = ?,
                toplam_tutar = ?,
                odeme_durumu = ?,
                resmi_kayit = ?
            WHERE id = ?
            """,
            _islem_params(data) + (islem_id,),
        )
        cur.execute("DELETE FROM kasa_hareketleri WHERE islem_id = ?", (islem_id,))
        cur.execute("DELETE FROM cari_hareketleri WHERE islem_id = ?", (islem_id,))
        _create_related_movements(cur, islem_id, data)
        conn.commit()
        return islem_id


def delete_islem(islem_id):
    belge_paths = [row["dosya_yolu"] for row in list_belge_dosyalari(islem_id)]
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM kasa_hareketleri WHERE islem_id = ?", (islem_id,))
        cur.execute("DELETE FROM cari_hareketleri WHERE islem_id = ?", (islem_id,))
        cur.execute("DELETE FROM belge_dosyalari WHERE islem_id = ?", (islem_id,))
        cur.execute("DELETE FROM islem_kayitlari WHERE id = ?", (islem_id,))
        conn.commit()

    for path_text in belge_paths:
        try:
            path = Path(path_text)
            if path.exists() and path.is_file():
                path.unlink()
        except OSError:
            pass


def _islem_params(data):
    return (
        data.get("islem_tipi"),
        data.get("cari_id"),
        data.get("kasa_id"),
        data.get("kategori_id"),
        data.get("tarih"),
        data.get("belge_turu"),
        data.get("belge_no"),
        data.get("belge_tarihi"),
        data.get("baslik"),
        data.get("aciklama"),
        data.get("tutar"),
        data.get("kdv_orani"),
        data.get("kdv_tutari"),
        data.get("toplam_tutar"),
        data.get("odeme_durumu"),
        data.get("resmi_kayit"),
    )


def _create_related_movements(cur, islem_id, data):
    kasa_id = data.get("kasa_id")
    odeme_durumu = data.get("odeme_durumu")
    islem_tipi = data.get("islem_tipi")
    toplam_tutar = data.get("toplam_tutar") or 0

    if kasa_id and odeme_durumu == "odendi":
        if islem_tipi in ("gelir", "tahsilat"):
            hareket_tipi = "giris"
        elif islem_tipi in ("gider", "odeme"):
            hareket_tipi = "cikis"
        else:
            hareket_tipi = None

        if hareket_tipi:
            cur.execute(
                """
                INSERT INTO kasa_hareketleri
                (kasa_id, islem_id, tarih, hareket_tipi, tutar, aciklama)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (kasa_id, islem_id, data.get("tarih"), hareket_tipi, toplam_tutar, data.get("baslik")),
            )

    cari_id = data.get("cari_id")
    if cari_id:
        hareket_yonu = None
        if islem_tipi == "gelir" and odeme_durumu != "odendi":
            hareket_yonu = "bana_borcu_artti"
        elif islem_tipi == "tahsilat":
            hareket_yonu = "bana_borcu_azaldi"
        elif islem_tipi == "gider" and odeme_durumu != "odendi":
            hareket_yonu = "benim_borcum_artti"
        elif islem_tipi == "odeme":
            hareket_yonu = "benim_borcum_azaldi"

        if hareket_yonu:
            cur.execute(
                """
                INSERT INTO cari_hareketleri
                (cari_id, islem_id, tarih, hareket_yonu, tutar, aciklama)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cari_id, islem_id, data.get("tarih"), hareket_yonu, toplam_tutar, data.get("baslik")),
            )


# -----------------------------------------------------------------------------
# Belge dosyaları
# -----------------------------------------------------------------------------
def list_belge_dosyalari(islem_id):
    return fetch_all(
        "SELECT * FROM belge_dosyalari WHERE islem_id = ? ORDER BY id DESC",
        (islem_id,),
    )


def add_belge_dosyasi(islem_id, source_file_path):
    source = Path(source_file_path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError("Seçilen belge dosyası bulunamadı.")

    config.BELGE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(source.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"islem_{islem_id}_{timestamp}_{safe_name}"
    dest_path = config.BELGE_DIR / dest_name

    shutil.copy2(source, dest_path)

    return execute(
        """
        INSERT INTO belge_dosyalari (islem_id, dosya_adi, dosya_yolu, dosya_tipi)
        VALUES (?, ?, ?, ?)
        """,
        (islem_id, source.name, str(dest_path), source.suffix.lower().replace(".", "")),
    )


def _safe_filename(filename):
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.()[] "
    cleaned = "".join(ch if ch in allowed else "_" for ch in filename)
    return cleaned.strip() or "belge"


# -----------------------------------------------------------------------------
# Raporlar
# -----------------------------------------------------------------------------
def dashboard_totals():
    para_girisi = fetch_one(
        """
        SELECT COALESCE(SUM(toplam_tutar), 0) AS toplam
        FROM islem_kayitlari
        WHERE islem_tipi IN ('gelir', 'tahsilat')
        """
    )["toplam"]

    para_cikisi = fetch_one(
        """
        SELECT COALESCE(SUM(toplam_tutar), 0) AS toplam
        FROM islem_kayitlari
        WHERE islem_tipi IN ('gider', 'odeme')
        """
    )["toplam"]

    kasa = fetch_one(
        """
        SELECT COALESCE(
            SUM(CASE WHEN hareket_tipi = 'giris' THEN tutar ELSE -tutar END),
            0
        ) AS bakiye
        FROM kasa_hareketleri
        """
    )["bakiye"]

    belgesiz = fetch_one(
        """
        SELECT COALESCE(SUM(toplam_tutar), 0) AS toplam
        FROM islem_kayitlari
        WHERE islem_tipi IN ('gider', 'odeme') AND belge_turu = 'belgesiz'
        """
    )["toplam"]

    return {
        "gelir": para_girisi,
        "gider": para_cikisi,
        "kar": para_girisi - para_cikisi,
        "kasa": kasa,
        "belgesiz": belgesiz,
    }


def kasa_bakiye_ozeti():
    return list_kasalar()


def kategori_ozeti():
    return fetch_all(
        """
        SELECT
            COALESCE(kt.kategori_adi, 'Kategorisiz') AS kategori,
            CASE
                WHEN i.islem_tipi IN ('gelir', 'tahsilat') THEN 'gelir/tahsilat'
                WHEN i.islem_tipi IN ('gider', 'odeme') THEN 'gider/odeme'
                ELSE i.islem_tipi
            END AS islem_tipi,
            SUM(i.toplam_tutar) AS toplam
        FROM islem_kayitlari i
        LEFT JOIN kategoriler kt ON kt.id = i.kategori_id
        GROUP BY
            COALESCE(kt.kategori_adi, 'Kategorisiz'),
            CASE
                WHEN i.islem_tipi IN ('gelir', 'tahsilat') THEN 'gelir/tahsilat'
                WHEN i.islem_tipi IN ('gider', 'odeme') THEN 'gider/odeme'
                ELSE i.islem_tipi
            END
        ORDER BY islem_tipi, toplam DESC
        """
    )


def belge_turu_ozeti():
    return fetch_all(
        """
        SELECT
            COALESCE(belge_turu, 'belgesiz') AS belge_turu,
            CASE
                WHEN islem_tipi IN ('gelir', 'tahsilat') THEN 'gelir/tahsilat'
                WHEN islem_tipi IN ('gider', 'odeme') THEN 'gider/odeme'
                ELSE islem_tipi
            END AS islem_tipi,
            SUM(toplam_tutar) AS toplam
        FROM islem_kayitlari
        GROUP BY
            COALESCE(belge_turu, 'belgesiz'),
            CASE
                WHEN islem_tipi IN ('gelir', 'tahsilat') THEN 'gelir/tahsilat'
                WHEN islem_tipi IN ('gider', 'odeme') THEN 'gider/odeme'
                ELSE islem_tipi
            END
        ORDER BY islem_tipi, toplam DESC
        """
    )


def cari_bakiye_ozeti():
    return fetch_all(
        """
        SELECT
            c.id,
            c.unvan,
            COALESCE(SUM(CASE
                WHEN ch.hareket_yonu = 'bana_borcu_artti' THEN ch.tutar
                WHEN ch.hareket_yonu = 'bana_borcu_azaldi' THEN -ch.tutar
                ELSE 0
            END), 0) AS bana_borcu,
            COALESCE(SUM(CASE
                WHEN ch.hareket_yonu = 'benim_borcum_artti' THEN ch.tutar
                WHEN ch.hareket_yonu = 'benim_borcum_azaldi' THEN -ch.tutar
                ELSE 0
            END), 0) AS benim_borcum
        FROM cariler c
        LEFT JOIN cari_hareketleri ch ON ch.cari_id = c.id
        WHERE c.aktif = 1
        GROUP BY c.id
        HAVING bana_borcu != 0 OR benim_borcum != 0
        ORDER BY c.unvan COLLATE NOCASE
        """
    )
