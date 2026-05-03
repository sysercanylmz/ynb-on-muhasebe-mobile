from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.scrollview import ScrollView

from app import config
from app.database import init_db
from app.screens.cariler_screen import CarilerScreen
from app.screens.dashboard_screen import DashboardScreen
from app.screens.islemler_screen import IslemlerScreen
from app.screens.kasalar_screen import KasalarScreen
from app.screens.kategoriler_screen import KategorilerScreen
from app.screens.raporlar_screen import RaporlarScreen
from app.widgets import BG, PRIMARY, PRIMARY_LIGHT, WHITE, btn, label


class AppScreenManager(ScreenManager):
    def app_refresh_all(self):
        for screen in self.screens:
            if hasattr(screen, "reload"):
                try:
                    screen.reload()
                except Exception:
                    pass


class YNBOnMuhasebeMobileApp(App):
    title = config.APP_NAME
    icon = str(config.ICON_PATH)

    def build(self):
        # Android'de bu klasör uygulamanın güvenli veri klasörüdür.
        config.set_data_dir(Path(self.user_data_dir))
        init_db()

        Window.clearcolor = BG
        root = BoxLayout(orientation="vertical")
        root.add_widget(self._header())
        self.manager = AppScreenManager(transition=NoTransition())
        self.manager.add_widget(DashboardScreen(name="dashboard"))
        self.manager.add_widget(IslemlerScreen(name="islemler"))
        self.manager.add_widget(CarilerScreen(name="cariler"))
        self.manager.add_widget(KasalarScreen(name="kasalar"))
        self.manager.add_widget(KategorilerScreen(name="kategoriler"))
        self.manager.add_widget(RaporlarScreen(name="raporlar"))
        root.add_widget(self.manager)
        root.add_widget(self._nav())
        return root

    def _header(self):
        box = BoxLayout(size_hint_y=None, height=dp(64), padding=[dp(10), dp(8)], spacing=dp(10))
        box.canvas.before.clear()
        if config.LOGO_PATH.exists():
            box.add_widget(Image(source=str(config.LOGO_PATH), size_hint_x=None, width=dp(50), allow_stretch=True))
        title_box = BoxLayout(orientation="vertical")
        title_box.add_widget(label("YNB Ön Muhasebe", size=18, bold=True, color=(0.08, 0.10, 0.16, 1)))
        title_box.add_widget(label("Mobil hesap takip", size=12, color=(0.38, 0.42, 0.50, 1)))
        box.add_widget(title_box)
        return box

    def _nav(self):
        outer = ScrollView(size_hint_y=None, height=dp(60), do_scroll_x=True, do_scroll_y=False)
        row = BoxLayout(orientation="horizontal", spacing=dp(6), padding=[dp(8), dp(8)], size_hint_x=None)
        row.bind(minimum_width=row.setter("width"))
        items = [
            ("Ana", "dashboard"),
            ("İşlem", "islemler"),
            ("Cari", "cariler"),
            ("Kasa", "kasalar"),
            ("Kategori", "kategoriler"),
            ("Rapor", "raporlar"),
        ]
        for text, screen in items:
            b = btn(text, lambda _b, s=screen: self.go(s), bg=PRIMARY, fg=WHITE, height=42)
            b.size_hint_x = None
            b.width = dp(92)
            row.add_widget(b)
        outer.add_widget(row)
        return outer

    def go(self, screen_name):
        self.manager.current = screen_name


if __name__ == "__main__":
    YNBOnMuhasebeMobileApp().run()
