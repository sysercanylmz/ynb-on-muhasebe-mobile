from kivy.uix.boxlayout import BoxLayout

from app.repositories import delete_kategori, insert_kategori, list_kategoriler, update_kategori
from app.screens.base import RefreshableScreen
from app.widgets import DANGER, PRIMARY, PRIMARY_LIGHT, SUCCESS, btn, card, confirm, form_input, form_spinner, label, scroll_container, show_message, title_label


class KategorilerScreen(RefreshableScreen):
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
        self.content.add_widget(title_label("Kategoriler"))
        self.kategori_tipi = form_spinner(["gelir", "gider"], "gider")
        self.kategori_adi = form_input("Kategori Adı")
        self.content.add_widget(label("Tip", size=13, height=24))
        self.content.add_widget(self.kategori_tipi)
        self.content.add_widget(label("Kategori Adı", size=13, height=24))
        self.content.add_widget(self.kategori_adi)
        row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        row.add_widget(btn("Kaydet", self.save, bg=SUCCESS))
        row.add_widget(btn("Yeni", lambda *_: self.clear_form(), bg=PRIMARY_LIGHT))
        self.content.add_widget(row)
        self.content.add_widget(title_label("Kayıtlar"))
        self.list_box = card(padding=0, spacing=8)
        self.content.add_widget(self.list_box)

    def clear_form(self):
        self.edit_id = None
        self.kategori_tipi.text = "gider"
        self.kategori_adi.text = ""

    def save(self, *_args):
        name = self.kategori_adi.text.strip()
        if not name:
            show_message("Eksik", "Kategori adı zorunlu.")
            return
        data = {"kategori_tipi": self.kategori_tipi.text, "kategori_adi": name}
        if self.edit_id:
            update_kategori(self.edit_id, data)
        else:
            insert_kategori(data)
        self.clear_form()
        self.reload()

    def edit(self, row):
        self.edit_id = row["id"]
        self.kategori_tipi.text = row["kategori_tipi"]
        self.kategori_adi.text = row["kategori_adi"]

    def delete(self, row):
        confirm("Sil", f"{row['kategori_adi']} pasifleştirilsin mi?", lambda: self._delete(row["id"]))

    def _delete(self, kategori_id):
        delete_kategori(kategori_id)
        self.clear_form()
        self.reload()

    def reload(self):
        if not hasattr(self, "list_box"):
            return
        self.list_box.clear_widgets()
        for row in list_kategoriler():
            box = card(padding=10, spacing=4)
            box.add_widget(label(f"[b]{row['kategori_adi']}[/b]", size=15, height=25))
            box.add_widget(label(row["kategori_tipi"], size=12, height=22))
            actions = BoxLayout(size_hint_y=None, height=40, spacing=8)
            actions.add_widget(btn("Düzenle", lambda _b, r=row: self.edit(r), bg=PRIMARY))
            actions.add_widget(btn("Sil", lambda _b, r=row: self.delete(r), bg=DANGER))
            box.add_widget(actions)
            self.list_box.add_widget(box)
