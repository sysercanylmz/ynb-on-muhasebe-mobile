from app.helpers import money
from app.repositories import belge_turu_ozeti, cari_bakiye_ozeti, kategori_ozeti, kasa_bakiye_ozeti
from app.screens.base import RefreshableScreen
from app.widgets import card, label, scroll_container, title_label


class RaporlarScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)

    def on_pre_enter(self, *_args):
        self.reload()

    def reload(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("Raporlar"))

        self.content.add_widget(title_label("Kasa / Banka Özeti"))
        for row in kasa_bakiye_ozeti():
            box = card(padding=10, spacing=2)
            box.add_widget(label(f"[b]{row['kasa_adi']}[/b]", size=15, height=26))
            box.add_widget(label(f"Açılış: {money(row['acilis_bakiyesi'])}", size=12, height=22))
            box.add_widget(label(f"Güncel: {money(row['bakiye'])}", size=15, bold=True, height=28))
            self.content.add_widget(box)

        self.content.add_widget(title_label("Kategori Özeti"))
        for row in kategori_ozeti():
            box = card(padding=10, spacing=2)
            box.add_widget(label(f"[b]{row['kategori']}[/b]", size=14, height=25))
            box.add_widget(label(f"{row['islem_tipi']} • {money(row['toplam'])}", size=13, height=24))
            self.content.add_widget(box)

        self.content.add_widget(title_label("Belge Türü Özeti"))
        for row in belge_turu_ozeti():
            box = card(padding=10, spacing=2)
            box.add_widget(label(f"[b]{row['belge_turu']}[/b]", size=14, height=25))
            box.add_widget(label(f"{row['islem_tipi']} • {money(row['toplam'])}", size=13, height=24))
            self.content.add_widget(box)

        self.content.add_widget(title_label("Cari Borç / Alacak"))
        rows = cari_bakiye_ozeti()
        if not rows:
            self.content.add_widget(label("Açık cari bakiye yok.", size=14, height=30))
        for row in rows:
            box = card(padding=10, spacing=2)
            box.add_widget(label(f"[b]{row['unvan']}[/b]", size=14, height=25))
            box.add_widget(label(f"Bana Borcu: {money(row['bana_borcu'])}", size=13, height=24))
            box.add_widget(label(f"Benim Borcum: {money(row['benim_borcum'])}", size=13, height=24))
            self.content.add_widget(box)
