from kivy.uix.boxlayout import BoxLayout

from app.helpers import money, number_for_input, to_float
from app.repositories import delete_kasa, insert_kasa, list_kasalar, update_kasa
from app.screens.base import RefreshableScreen
from app.widgets import DANGER, PRIMARY, PRIMARY_LIGHT, SUCCESS, btn, card, confirm, form_input, form_spinner, label, scroll_container, show_message, title_label


class KasalarScreen(RefreshableScreen):
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
        self.content.add_widget(title_label("Kasa / Banka"))

        self.kasa_adi = form_input("Kasa/Banka Adı")
        self.kasa_tipi = form_spinner(["nakit", "banka", "kredi_karti", "pos", "diger"], "nakit")
        self.acilis_bakiyesi = form_input("Açılış Bakiyesi Örn: 50000")
        self.aciklama = form_input("Açıklama", multiline=True)

        for caption, widget in [
            ("Ad", self.kasa_adi),
            ("Tip", self.kasa_tipi),
            ("Açılış Bakiyesi", self.acilis_bakiyesi),
            ("Açıklama", self.aciklama),
        ]:
            self.content.add_widget(label(caption, size=13, height=24))
            self.content.add_widget(widget)

        row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        row.add_widget(btn("Kaydet", self.save, bg=SUCCESS))
        row.add_widget(btn("Yeni", lambda *_: self.clear_form(), bg=PRIMARY_LIGHT))
        self.content.add_widget(row)
        self.list_box = card(padding=0, spacing=8)
        self.content.add_widget(title_label("Kayıtlar"))
        self.content.add_widget(self.list_box)

    def clear_form(self):
        self.edit_id = None
        self.kasa_adi.text = ""
        self.kasa_tipi.text = "nakit"
        self.acilis_bakiyesi.text = ""
        self.aciklama.text = ""

    def collect(self):
        name = self.kasa_adi.text.strip()
        if not name:
            raise ValueError("Kasa/Banka adı zorunlu.")
        return {
            "kasa_adi": name,
            "kasa_tipi": self.kasa_tipi.text,
            "acilis_bakiyesi": to_float(self.acilis_bakiyesi.text),
            "aciklama": self.aciklama.text.strip(),
        }

    def save(self, *_args):
        try:
            data = self.collect()
            if self.edit_id:
                update_kasa(self.edit_id, data)
                show_message("Tamam", "Kasa/Banka güncellendi.")
            else:
                insert_kasa(data)
                show_message("Tamam", "Kasa/Banka eklendi.")
            self.clear_form()
            self.reload()
        except Exception as exc:
            show_message("Hata", str(exc))

    def edit(self, row):
        self.edit_id = row["id"]
        self.kasa_adi.text = row["kasa_adi"] or ""
        self.kasa_tipi.text = row["kasa_tipi"] or "nakit"
        self.acilis_bakiyesi.text = number_for_input(row["acilis_bakiyesi"])
        self.aciklama.text = row["aciklama"] or ""

    def delete(self, row):
        confirm("Sil", f"{row['kasa_adi']} pasifleştirilsin mi?", lambda: self._delete(row["id"]))

    def _delete(self, kasa_id):
        delete_kasa(kasa_id)
        self.clear_form()
        self.reload()

    def reload(self):
        if not hasattr(self, "list_box"):
            return
        self.list_box.clear_widgets()
        for row in list_kasalar():
            box = card(padding=10, spacing=4)
            box.add_widget(label(f"[b]{row['kasa_adi']}[/b] ({row['kasa_tipi']})", size=15, height=25))
            box.add_widget(label(f"Açılış: {money(row['acilis_bakiyesi'])}", size=12, height=22))
            box.add_widget(label(f"Güncel Bakiye: [b]{money(row['bakiye'])}[/b]", size=15, height=28))
            actions = BoxLayout(size_hint_y=None, height=40, spacing=8)
            actions.add_widget(btn("Düzenle", lambda _b, r=row: self.edit(r), bg=PRIMARY))
            actions.add_widget(btn("Sil", lambda _b, r=row: self.delete(r), bg=DANGER))
            box.add_widget(actions)
            self.list_box.add_widget(box)
