from __future__ import annotations

import re
from datetime import date, datetime


def today_str() -> str:
    return date.today().isoformat()


def display_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.strptime(value[:10], "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        return str(value)


def to_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default

    # 50.000,25 veya 50000,25 veya 50000.25 girişlerini destekle.
    text = text.replace("TL", "").replace("₺", "").strip()
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"Sayısal değer hatalı: {value}") from exc


def money(value) -> str:
    value = float(value or 0)
    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def number_for_input(value) -> str:
    value = float(value or 0)
    if value.is_integer():
        return str(int(value))
    return str(value).replace(".", ",")


def kdv_ayir(toplam_tutar, kdv_orani) -> tuple[float, float]:
    toplam_tutar = float(toplam_tutar or 0)
    kdv_orani = float(kdv_orani or 0)
    if kdv_orani <= 0:
        return round(toplam_tutar, 2), 0.0
    net = toplam_tutar / (1 + (kdv_orani / 100))
    kdv = toplam_tutar - net
    return round(net, 2), round(kdv, 2)


def format_phone_tr(value: str | None) -> str:
    """Telefonu +90 5XX XXX XX XX formatına yaklaştırır.

    Kullanıcı 0532..., 532..., 90532... veya +90532... yazabilir.
    Sabit hat girilirse de +90 ile düzenlenir.
    """
    if not value:
        return ""

    digits = re.sub(r"\D+", "", value)
    if digits.startswith("90") and len(digits) >= 12:
        digits = digits[2:]
    if digits.startswith("0") and len(digits) >= 11:
        digits = digits[1:]

    if len(digits) < 10:
        return value.strip()

    digits = digits[-10:]
    return f"+90 {digits[0:3]} {digits[3:6]} {digits[6:8]} {digits[8:10]}"


def bool_int(value) -> int:
    return 1 if bool(value) else 0


def is_official_document(belge_turu: str) -> bool:
    return belge_turu in {"fatura", "fis", "makbuz", "dekont", "e_arsiv", "e_fatura"}
