from __future__ import annotations

from pathlib import Path

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

from app.helpers import is_official_document, kdv_ayir, money, number_for_input, to_float, today_str
from app.repositories import (
    add_belge_dosyasi,
    delete_islem,
    insert_islem,
    list_belge_dosyalari,
    list_cariler,
    list_islemler,
    list_kasalar,
    list_kategoriler_by_tip,
    update_islem,
)
from app.screens.base import RefreshableScreen
from app.widgets import (
    ACCENT,
    DANGER,
    PRIMARY,
    PRIMARY_LIGHT,
    SUCCESS,
    DateButton,
    btn,
    card,
    choice_id,
    confirm,
    form_input,
    form_spinner,
    label,
    make_choice,
    scroll_container,
    set_spinner_by_id,
    show_message,
    title_label,
)

ISLEM_TIPLERI = ["gelir", "gider", "tahsilat", "odeme"]
BELGE_TURLERI = ["belgesiz", "fatura", "fis", "makbuz", "dekont", "e_arsiv", "e_fatura", "diger"]
ODEME_DURUMLARI = ["odendi", "odenmedi", "kismi"]


class IslemlerScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_id = None
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)
        self._build()

    def on_pre_enter(self, *_args):
        self.reload_options()
        self.reload_list()

    def _build(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("Gelir / Gider / Tahsilat / Ödeme"))

        self.islem_tipi = form_spinner(ISLEM_TIPLERI, "gider")
        self.islem_tipi.bind(text=lambda *_: self.on_type_change())
        self.tarih = DateButton(today_str())
        self.baslik = form_input("Başlık")
        self.toplam_tutar = form_input("Toplam Tutar")
        self.kdv_orani = form_spinner(["0", "1", "8", "10", "18", "20"], "0")
        self.belge_turu = form_spinner(BELGE_TURLERI, "belgesiz")
        self.belge_no = form_input("Belge No")
        self.odeme_durumu = form_spinner(ODEME_DURUMLARI, "odendi")
        self.kasa = form_spinner(["Seçiniz"], "Seçiniz")
        self.cari = form_spinner(["Seçiniz"], "Seçiniz")
        self.kategori = form_spinner(["Seçiniz"], "Seçiniz")
        self.aciklama = form_input("Açıklama", multiline=True)

        fields = [
            ("İşlem Tipi", self.islem_tipi),
            ("Tarih", self.tarih),
            ("Başlık", self.baslik),
            ("Toplam Tutar", self.toplam_tutar),
            ("KDV Oranı", self.kdv_orani),
            ("Belge Türü", self.belge_turu),
            ("Belge No", self.belge_no),
            ("Ödeme Durumu", self.odeme_durumu),
            ("Kasa / Banka", self.kasa),
            ("Cari", self.cari),
            ("Kategori", self.kategori),
            ("Açıklama", self.aciklama),
        ]
        for caption, widget in fields:
            self.content.add_widget(label(caption, size=13, height=24))
            self.content.add_widget(widget)

        row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        row.add_widget(btn("Kaydet", self.save, bg=SUCCESS))
        row.add_widget(btn("Yeni", lambda *_: self.clear_form(), bg=PRIMARY_LIGHT))
        self.content.add_widget(row)

        self.content.add_widget(title_label("Kayıtlar"))
        self.list_box = card(padding=0, spacing=8)
        self.content.add_widget(self.list_box)

    def reload_options(self):
        self.kasa_rows = list_kasalar()
        self.cari_rows = list_cariler()
        self.kasa.values = ["Seçiniz"] + [make_choice(r, "kasa_adi") for r in self.kasa_rows]
        self.cari.values = ["Seçiniz"] + [make_choice(r, "unvan") for r in self.cari_rows]
        if self.kasa.text not in self.kasa.values:
            self.kasa.text = "Seçiniz"
        if self.cari.text not in self.cari.values:
            self.cari.text = "Seçiniz"
        self.on_type_change()

    def on_type_change(self):
        kategori_tip = "gelir" if self.islem_tipi.text in ("gelir", "tahsilat") else "gider"
        self.kategori_rows = list_kategoriler_by_tip(kategori_tip)
        self.kategori.values = ["Seçiniz"] + [make_choice(r, "kategori_adi") for r in self.kategori_rows]
        if self.kategori.text not in self.kategori.values:
            self.kategori.text = "Seçiniz"

    def clear_form(self):
        self.edit_id = None
        self.islem_tipi.text = "gider"
        self.tarih.set_date(today_str())
        self.baslik.text = ""
        self.toplam_tutar.text = ""
        self.kdv_orani.text = "0"
        self.belge_turu.text = "belgesiz"
        self.belge_no.text = ""
        self.odeme_durumu.text = "odendi"
        self.kasa.text = "Seçiniz"
        self.cari.text = "Seçiniz"
        self.kategori.text = "Seçiniz"
        self.aciklama.text = ""

    def collect(self):
        baslik = self.baslik.text.strip()
        if not baslik:
            raise ValueError("Başlık zorunlu.")
        toplam = to_float(self.toplam_tutar.text)
        if toplam <= 0:
            raise ValueError("Toplam tutar 0'dan büyük olmalı.")
        kdv_orani = to_float(self.kdv_orani.text)
        tutar, kdv_tutari = kdv_ayir(toplam, kdv_orani)
        belge_turu = self.belge_turu.text
        resmi_kayit = 1 if is_official_document(belge_turu) else 0
        return {
            "islem_tipi": self.islem_tipi.text,
            "cari_id": choice_id(self.cari.text),
            "kasa_id": choice_id(self.kasa.text),
            "kategori_id": choice_id(self.kategori.text),
            "tarih": self.tarih.date_value,
            "belge_turu": belge_turu,
            "belge_no": self.belge_no.text.strip(),
            "belge_tarihi": self.tarih.date_value,
            "baslik": baslik,
            "aciklama": self.aciklama.text.strip(),
            "tutar": tutar,
            "kdv_orani": kdv_orani,
            "kdv_tutari": kdv_tutari,
            "toplam_tutar": toplam,
            "odeme_durumu": self.odeme_durumu.text,
            "resmi_kayit": resmi_kayit,
        }

    def save(self, *_args):
        try:
            data = self.collect()
            if data["odeme_durumu"] == "odendi" and not data["kasa_id"]:
                raise ValueError("Ödendi seçiliyse kasa/banka seçmelisin.")
            if self.edit_id:
                update_islem(self.edit_id, data)
                show_message("Tamam", "İşlem güncellendi.")
            else:
                self.edit_id = insert_islem(data)
                show_message("Tamam", "İşlem eklendi. Belge eklemek istersen listeden Belge butonunu kullan.")
            self.clear_form()
            self.reload_list()
            self.manager.app_refresh_all()
        except Exception as exc:
            show_message("Hata", str(exc))

    def edit(self, row):
        self.edit_id = row["id"]
        self.islem_tipi.text = row["islem_tipi"] or "gider"
        self.tarih.set_date(row["tarih"])
        self.baslik.text = row["baslik"] or ""
        self.toplam_tutar.text = number_for_input(row["toplam_tutar"])
        self.kdv_orani.text = number_for_input(row["kdv_orani"])
        self.belge_turu.text = row["belge_turu"] or "belgesiz"
        self.belge_no.text = row["belge_no"] or ""
        self.odeme_durumu.text = row["odeme_durumu"] or "odendi"
        self.reload_options()
        set_spinner_by_id(self.kasa, row["kasa_id"], row["kasa_adi"])
        set_spinner_by_id(self.cari, row["cari_id"], row["cari_unvan"])
        set_spinner_by_id(self.kategori, row["kategori_id"], row["kategori_adi"])
        self.aciklama.text = row["aciklama"] or ""
        self.scroll.scroll_y = 1

    def detail(self, row):
        docs = list_belge_dosyalari(row["id"])
        doc_text = "\n".join([f"- {d['dosya_adi']}" for d in docs]) or "Belge yok"
        message = (
            f"Başlık: {row['baslik']}\n"
            f"Tarih: {row['tarih']}\n"
            f"Tip: {row['islem_tipi']}\n"
            f"Tutar: {money(row['toplam_tutar'])}\n"
            f"KDV: {money(row['kdv_tutari'])}\n"
            f"Belge: {row['belge_turu']} {row['belge_no'] or ''}\n"
            f"Kasa: {row['kasa_adi'] or '-'}\n"
            f"Cari: {row['cari_unvan'] or '-'}\n"
            f"Kategori: {row['kategori_adi'] or '-'}\n\n"
            f"Ekler:\n{doc_text}"
        )
        show_message("İşlem Detayı", message)

    def delete(self, row):
        confirm("Sil", f"{row['baslik']} kaydı silinsin mi?", lambda: self._delete(row["id"]))

    def _delete(self, islem_id):
        delete_islem(islem_id)
        self.clear_form()
        self.reload_list()
        self.manager.app_refresh_all()

    def attach(self, row):
        AttachmentPopup(row["id"], on_done=lambda: self.reload_list()).open()

    def reload_list(self):
        if not hasattr(self, "list_box"):
            return
        self.list_box.clear_widgets()
        for row in list_islemler():
            box = card(padding=10, spacing=4)
            box.add_widget(label(f"[b]{row['baslik']}[/b]", size=15, height=27))
            meta = f"{row['tarih']} • {row['islem_tipi']} • {row['belge_turu']} • {money(row['toplam_tutar'])}"
            box.add_widget(label(meta, size=12, height=24))
            if row["cari_unvan"] or row["kasa_adi"]:
                box.add_widget(label(f"{row['cari_unvan'] or '-'} / {row['kasa_adi'] or '-'}", size=12, height=22))
            actions1 = BoxLayout(size_hint_y=None, height=40, spacing=6)
            actions1.add_widget(btn("Düzenle", lambda _b, r=row: self.edit(r), bg=PRIMARY))
            actions1.add_widget(btn("Detay", lambda _b, r=row: self.detail(r), bg=ACCENT))
            box.add_widget(actions1)
            actions2 = BoxLayout(size_hint_y=None, height=40, spacing=6)
            actions2.add_widget(btn(f"Belge ({row['belge_sayisi']})", lambda _b, r=row: self.attach(r), bg=PRIMARY_LIGHT))
            actions2.add_widget(btn("Sil", lambda _b, r=row: self.delete(r), bg=DANGER))
            box.add_widget(actions2)
            self.list_box.add_widget(box)


class AttachmentPopup(Popup):
    def __init__(self, islem_id, on_done=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Belge Ekle"
        self.islem_id = islem_id
        self.on_done = on_done
        self.size_hint = (0.96, 0.88)
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(label("Fiş/fatura/dekont dosya yolunu yazabilir veya aşağıdan dosya seçebilirsin.", size=13, height=46))
        self.path_input = form_input("/storage/emulated/0/Download/fis.jpg")
        root.add_widget(self.path_input)
        row = BoxLayout(size_hint_y=None, height=42, spacing=8)
        row.add_widget(btn("Ekle", self.add_manual, bg=SUCCESS))
        row.add_widget(btn("Kapat", lambda *_: self.dismiss(), bg=PRIMARY_LIGHT))
        root.add_widget(row)
        try:
            self.filechooser = FileChooserListView(path=str(Path.home()))
            root.add_widget(self.filechooser)
            root.add_widget(btn("Seçili Dosyayı Ekle", self.add_selected, bg=PRIMARY))
        except Exception:
            pass
        self.content = root

    def add_selected(self, *_args):
        selected = getattr(self, "filechooser", None).selection if hasattr(self, "filechooser") else []
        if not selected:
            show_message("Eksik", "Dosya seçilmedi.")
            return
        self._add_path(selected[0])

    def add_manual(self, *_args):
        self._add_path(self.path_input.text.strip())

    def _add_path(self, path):
        try:
            add_belge_dosyasi(self.islem_id, path)
            show_message("Tamam", "Belge eklendi.")
            if self.on_done:
                self.on_done()
            self.dismiss()
        except Exception as exc:
            show_message("Hata", str(exc))
