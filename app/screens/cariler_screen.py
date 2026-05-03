from kivy.uix.boxlayout import BoxLayout

from app.helpers import format_phone_tr
from app.repositories import delete_cari, insert_cari, list_cariler, update_cari
from app.screens.base import RefreshableScreen
from app.widgets import DANGER, PRIMARY, PRIMARY_LIGHT, SUCCESS, btn, card, confirm, form_input, form_spinner, label, scroll_container, show_message, title_label


class CarilerScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_id = None
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)
        self._build()

    def on_pre_enter(self, *_args):
        self.reload()

    def _build(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("Cariler"))

        self.cari_tipi = form_spinner(["musteri", "tedarikci", "personel", "genel"], "musteri")
        self.unvan = form_input("Firma / Kişi Adı")
        self.telefon = form_input("Telefon - sadece rakam yazabilirsin")
        self.email = form_input("E-posta")
        self.vergi_dairesi = form_input("Vergi Dairesi")
        self.vergi_no = form_input("Vergi No")
        self.tc_no = form_input("TC No")
        self.adres = form_input("Adres", multiline=True)
        self.aciklama = form_input("Açıklama", multiline=True)

        for caption, widget in [
            ("Tip", self.cari_tipi),
            ("Unvan / Ad Soyad", self.unvan),
            ("Telefon", self.telefon),
            ("E-posta", self.email),
            ("Vergi Dairesi", self.vergi_dairesi),
            ("Vergi No", self.vergi_no),
            ("TC No", self.tc_no),
            ("Adres", self.adres),
            ("Açıklama", self.aciklama),
        ]:
            self.content.add_widget(label(caption, size=13, height=24))
            self.content.add_widget(widget)

        row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        row.add_widget(btn("Kaydet", self.save, bg=SUCCESS))
        row.add_widget(btn("Yeni", lambda *_: self.clear_form(), bg=PRIMARY_LIGHT))
        self.content.add_widget(row)
        self.content.add_widget(title_label("Kayıtlar"))
        self.list_box = card(padding=0, spacing=8)
        self.content.add_widget(self.list_box)

    def clear_form(self):
        self.edit_id = None
        self.cari_tipi.text = "musteri"
        for widget in [self.unvan, self.telefon, self.email, self.vergi_dairesi, self.vergi_no, self.tc_no, self.adres, self.aciklama]:
            widget.text = ""

    def collect(self):
        unvan = self.unvan.text.strip()
        if not unvan:
            raise ValueError("Unvan / Ad Soyad zorunlu.")
        return {
            "cari_tipi": self.cari_tipi.text,
            "unvan": unvan,
            "telefon": format_phone_tr(self.telefon.text),
            "email": self.email.text.strip(),
            "vergi_dairesi": self.vergi_dairesi.text.strip(),
            "vergi_no": self.vergi_no.text.strip(),
            "tc_no": self.tc_no.text.strip(),
            "adres": self.adres.text.strip(),
            "aciklama": self.aciklama.text.strip(),
        }

    def save(self, *_args):
        try:
            data = self.collect()
            if self.edit_id:
                update_cari(self.edit_id, data)
                show_message("Tamam", "Cari güncellendi.")
            else:
                insert_cari(data)
                show_message("Tamam", "Cari eklendi.")
            self.clear_form()
            self.reload()
        except Exception as exc:
            show_message("Hata", str(exc))

    def edit(self, row):
        self.edit_id = row["id"]
        self.cari_tipi.text = row["cari_tipi"] or "genel"
        self.unvan.text = row["unvan"] or ""
        self.telefon.text = row["telefon"] or ""
        self.email.text = row["email"] or ""
        self.vergi_dairesi.text = row["vergi_dairesi"] or ""
        self.vergi_no.text = row["vergi_no"] or ""
        self.tc_no.text = row["tc_no"] or ""
        self.adres.text = row["adres"] or ""
        self.aciklama.text = row["aciklama"] or ""

    def delete(self, row):
        confirm("Sil", f"{row['unvan']} pasifleştirilsin mi?", lambda: self._delete(row["id"]))

    def _delete(self, cari_id):
        delete_cari(cari_id)
        self.clear_form()
        self.reload()

    def reload(self):
        if not hasattr(self, "list_box"):
            return
        self.list_box.clear_widgets()
        for row in list_cariler():
            box = card(padding=10, spacing=4)
            box.add_widget(label(f"[b]{row['unvan']}[/b]", size=15, height=26))
            sub = f"{row['cari_tipi']}"
            if row["telefon"]:
                sub += f" • {row['telefon']}"
            box.add_widget(label(sub, size=12, height=24))
            actions = BoxLayout(size_hint_y=None, height=40, spacing=8)
            actions.add_widget(btn("Düzenle", lambda _b, r=row: self.edit(r), bg=PRIMARY))
            actions.add_widget(btn("Sil", lambda _b, r=row: self.delete(r), bg=DANGER))
            box.add_widget(actions)
            self.list_box.add_widget(box)
