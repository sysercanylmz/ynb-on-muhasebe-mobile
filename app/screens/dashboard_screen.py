from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from app.helpers import money
from app.repositories import dashboard_totals, kasa_bakiye_ozeti, list_islemler
from app.screens.base import RefreshableScreen
from app.widgets import BG, CARD_BG, PRIMARY, TEXT, card, label, scroll_container, title_label


class DashboardScreen(RefreshableScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll, self.content = scroll_container()
        self.add_widget(self.scroll)

    def on_pre_enter(self, *_args):
        self.reload()

    def reload(self):
        self.content.clear_widgets()
        self.content.add_widget(title_label("Ana Sayfa"))

        totals = dashboard_totals()
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        cards = [
            ("Toplam Giriş", money(totals["gelir"])),
            ("Toplam Çıkış", money(totals["gider"])),
            ("Net Durum", money(totals["kar"])),
            ("Kasa/Banka", money(totals["kasa"])),
            ("Belgesiz Çıkış", money(totals["belgesiz"])),
        ]
        for title, value in cards:
            box = card(padding=10, spacing=4)
            box.add_widget(label(title, size=12, color=(0.38, 0.42, 0.50, 1), height=22))
            box.add_widget(label(value, size=17, bold=True, color=TEXT, height=32))
            grid.add_widget(box)
        self.content.add_widget(grid)

        self.content.add_widget(title_label("Kasa / Banka Bakiyeleri"))
        for row in kasa_bakiye_ozeti():
            box = card(padding=10, spacing=3)
            box.add_widget(label(f"[b]{row['kasa_adi']}[/b]  ({row['kasa_tipi']})", size=15, height=26))
            box.add_widget(label(f"Açılış: {money(row['acilis_bakiyesi'])}", size=12, color=(0.38, 0.42, 0.50, 1), height=22))
            box.add_widget(label(f"Güncel: {money(row['bakiye'])}", size=16, bold=True, height=28))
            self.content.add_widget(box)

        self.content.add_widget(title_label("Son İşlemler"))
        for row in list_islemler(limit=8):
            box = card(padding=10, spacing=3)
            box.add_widget(label(f"[b]{row['baslik']}[/b]", size=15, height=26))
            box.add_widget(label(f"{row['tarih']} • {row['islem_tipi']} • {money(row['toplam_tutar'])}", size=13, color=(0.38, 0.42, 0.50, 1), height=24))
            self.content.add_widget(box)
