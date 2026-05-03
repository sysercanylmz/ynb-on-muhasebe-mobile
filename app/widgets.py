from __future__ import annotations

import calendar
from datetime import date

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from app.helpers import display_date


PRIMARY = (0.07, 0.12, 0.23, 1)
PRIMARY_LIGHT = (0.13, 0.22, 0.40, 1)
ACCENT = (0.20, 0.50, 0.95, 1)
DANGER = (0.78, 0.16, 0.16, 1)
SUCCESS = (0.10, 0.55, 0.30, 1)
BG = (0.95, 0.96, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
TEXT = (0.08, 0.10, 0.16, 1)
MUTED = (0.38, 0.42, 0.50, 1)
WHITE = (1, 1, 1, 1)


def label(text: str, size=15, bold=False, color=TEXT, halign="left", height=None):
    w = Label(
        text=text,
        font_size=dp(size),
        bold=bold,
        color=color,
        halign=halign,
        valign="middle",
        markup=True,
    )
    if height:
        w.size_hint_y = None
        w.height = dp(height)
    w.bind(size=lambda inst, _value: setattr(inst, "text_size", (inst.width, None)))
    return w


def title_label(text: str):
    return label(text, size=20, bold=True, color=TEXT, height=38)


def small_label(text: str):
    return label(text, size=12, color=MUTED, height=24)


def btn(text: str, on_press=None, bg=PRIMARY, fg=WHITE, height=44):
    b = Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_color=bg,
        color=fg,
        font_size=dp(14),
    )
    if on_press:
        b.bind(on_press=on_press)
    return b


def form_input(hint="", text="", multiline=False, input_filter=None):
    ti = TextInput(
        text=str(text or ""),
        hint_text=hint,
        multiline=multiline,
        size_hint_y=None,
        height=dp(92 if multiline else 44),
        input_filter=input_filter,
        font_size=dp(15),
        padding=[dp(10), dp(10), dp(10), dp(10)],
    )
    return ti


def form_spinner(values, text=None):
    sp = Spinner(
        text=text or (values[0] if values else "Seçiniz"),
        values=values,
        size_hint_y=None,
        height=dp(44),
        font_size=dp(14),
    )
    return sp


def card(orientation="vertical", padding=12, spacing=8):
    box = BoxLayout(
        orientation=orientation,
        padding=[dp(padding)] * 4,
        spacing=dp(spacing),
        size_hint_y=None,
    )
    box.bind(minimum_height=box.setter("height"))
    return box


def scroll_container():
    scroll = ScrollView(size_hint=(1, 1))
    content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10), size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    scroll.add_widget(content)
    return scroll, content


def make_choice(row, title_field):
    return f"{row['id']} | {row[title_field]}"


def choice_id(text):
    if not text or "|" not in text:
        return None
    try:
        return int(text.split("|", 1)[0].strip())
    except ValueError:
        return None


def set_spinner_by_id(spinner: Spinner, row_id, title: str | None = None):
    if not row_id:
        return
    prefix = f"{row_id} |"
    for value in spinner.values:
        if value.startswith(prefix):
            spinner.text = value
            return
    if title:
        spinner.text = f"{row_id} | {title}"


def show_message(title: str, message: str):
    layout = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
    layout.add_widget(label(message, size=15))
    close = btn("Tamam", bg=PRIMARY)
    layout.add_widget(close)
    popup = Popup(title=title, content=layout, size_hint=(0.88, None), height=dp(220))
    close.bind(on_press=popup.dismiss)
    popup.open()


def confirm(title: str, message: str, on_yes):
    layout = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
    layout.add_widget(label(message, size=15))
    row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
    no = btn("Vazgeç", bg=PRIMARY_LIGHT)
    yes = btn("Evet", bg=DANGER)
    row.add_widget(no)
    row.add_widget(yes)
    layout.add_widget(row)
    popup = Popup(title=title, content=layout, size_hint=(0.9, None), height=dp(230))
    no.bind(on_press=popup.dismiss)

    def _yes(_btn):
        popup.dismiss()
        on_yes()

    yes.bind(on_press=_yes)
    popup.open()


class DateButton(Button):
    def __init__(self, date_value=None, **kwargs):
        super().__init__(**kwargs)
        self.date_value = date_value or date.today().isoformat()
        self.size_hint_y = None
        self.height = dp(44)
        self.background_color = (0.90, 0.94, 1, 1)
        self.color = TEXT
        self.font_size = dp(14)
        self.update_text()
        self.bind(on_press=self.open_picker)

    def set_date(self, value):
        self.date_value = value or date.today().isoformat()
        self.update_text()

    def update_text(self):
        self.text = display_date(self.date_value) or "Tarih seç"

    def open_picker(self, *_args):
        DatePickerPopup(self.date_value, self.set_date).open()


class DatePickerPopup(Popup):
    def __init__(self, selected_date, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Tarih Seç"
        self.size_hint = (0.96, 0.82)
        self.callback = callback
        try:
            parts = [int(x) for x in str(selected_date).split("-")]
            self.current = date(parts[0], parts[1], 1)
            self.selected_day = parts[2]
        except Exception:
            today = date.today()
            self.current = date(today.year, today.month, 1)
            self.selected_day = today.day
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.content = self.root_box
        self.render()

    def render(self):
        self.root_box.clear_widgets()
        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        header.add_widget(btn("‹", self.prev_month, bg=PRIMARY_LIGHT))
        header.add_widget(label(f"{self.current.month:02d}/{self.current.year}", size=18, bold=True, halign="center"))
        header.add_widget(btn("›", self.next_month, bg=PRIMARY_LIGHT))
        self.root_box.add_widget(header)

        names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        grid = GridLayout(cols=7, spacing=dp(4), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for name in names:
            grid.add_widget(label(name, size=12, bold=True, halign="center", height=30))

        cal = calendar.Calendar(firstweekday=0)
        for day in cal.itermonthdays(self.current.year, self.current.month):
            if day == 0:
                grid.add_widget(label("", height=42))
            else:
                b = btn(str(day), bg=ACCENT if day == self.selected_day else (0.88, 0.90, 0.94, 1), fg=WHITE if day == self.selected_day else TEXT, height=42)
                b.bind(on_press=lambda _b, d=day: self.select_day(d))
                grid.add_widget(b)
        self.root_box.add_widget(grid)
        self.root_box.add_widget(btn("Bugün", self.select_today, bg=SUCCESS))
        self.root_box.add_widget(btn("Kapat", lambda _b: self.dismiss(), bg=PRIMARY_LIGHT))

    def prev_month(self, *_args):
        year = self.current.year
        month = self.current.month - 1
        if month == 0:
            month = 12
            year -= 1
        self.current = date(year, month, 1)
        self.selected_day = min(self.selected_day, calendar.monthrange(year, month)[1])
        self.render()

    def next_month(self, *_args):
        year = self.current.year
        month = self.current.month + 1
        if month == 13:
            month = 1
            year += 1
        self.current = date(year, month, 1)
        self.selected_day = min(self.selected_day, calendar.monthrange(year, month)[1])
        self.render()

    def select_day(self, day):
        self.callback(date(self.current.year, self.current.month, day).isoformat())
        self.dismiss()

    def select_today(self, *_args):
        self.callback(date.today().isoformat())
        self.dismiss()
