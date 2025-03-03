
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import time


class PaintApp(tk.Tk):
    # Приложение для рисования графических фигур.

    def __init__(self):
        # Инициализация графического редактора.
        super().__init__()

        self.title("Графический редактор")
        self.geometry("800x550")  # Размер окна

        self.draw_area_width = 600
        self.draw_area_height = 400
        self.is_debugging = False
        self.debug_pause = 10
        self.selected_color = "black"  # Цвет фигур
        self.is_drawing = False
        self.selected_figure = "Окружность"  # Тип фигуры по умолчанию
        self.grid_visible = True
        self.grid_step = 10

        self._setup_ui()
        self._center_window()
        self._draw_grid()  # Сетка при запуске

    def _center_window(self):
        # Размещает окно приложения в центре экрана.
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        x_coord = (screen_width // 2) - (window_width // 2)
        y_coord = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x_coord}+{y_coord}")

    def _draw_grid(self):
        # Отображает сетку на холсте.
        if self.grid_visible:
            for i in range(self.grid_step, self.draw_area_width, self.grid_step):
                self.canvas.create_line(i, 0, i, self.draw_area_height, fill="lightgray", tags="grid_line")
            for i in range(self.grid_step, self.draw_area_height, self.grid_step):
                self.canvas.create_line(0, i, self.draw_area_width, i, fill="lightgray", tags="grid_line")

    def clear_canvas(self):
        # Очищает холст от всех изображений и перерисовывает сетку.
        self.canvas.delete("all")
        self._draw_grid()

    def draw_point(self, x, y):
        # Рисует единичную точку на холсте.
        self.canvas.create_oval(x, y, x + 1, y + 1, fill=self.selected_color, outline="")
        if self.is_debugging:
            print(f"{self.selected_figure.capitalize()}: (x={x}, y={y})")
        self._pause_if_debugging()

    def draw_circle(self, x0, y0, radius):
        # Рисует окружность, используя алгоритм Брезенхема.
        x, y, delta = 0, radius, 3 - 2 * radius
        while x <= y:
            for dx, dy in [(x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)
            x += 1
            if delta > 0:
                y -= 1
                delta += 4 * (x - y) + 10
            else:
                delta += 4 * x + 6

    def draw_ellipse(self, x0, y0, a, b):
        # Рисует эллипс, используя алгоритм построения.
        x, y = 0, b
        d1 = b ** 2 - a ** 2 * b + 0.25 * a ** 2

        while (a ** 2) * (y - 0.5) > (b ** 2) * (x + 1):
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)
            x += 1
            if d1 < 0:
                d1 += (2 * b ** 2) * x + b ** 2
            else:
                y -= 1
                d1 += (2 * b ** 2) * x - (2 * a ** 2) * y + b ** 2

        d2 = b ** 2 * (x + 0.5) ** 2 + a ** 2 * (y - 1) ** 2 - a ** 2 * b ** 2
        while y >= 0:
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)
            y -= 1
            if d2 > 0:
                d2 += a ** 2 - 2 * a ** 2 * y
            else:
                x += 1
                d2 += (2 * b ** 2) * x - (2 * a ** 2) * y + a ** 2

    def draw_hyperbola(self, x0, y0, a, b):
        # Рисует гиперболу, используя алгоритм построения.

        x, y = a, 0

        d1 = b ** 2 * (x + 0.5) ** 2 - a ** 2 * (y + 1) ** 2 - a ** 2 * b ** 2
        while (b ** 2) * (x - 0.5) > (a ** 2) * (y + 1):
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)

            y += 1
            if d1 < 0:
                d1 += (2 * a ** 2) * y + a ** 2
            else:
                x += 1
                d1 += (2 * a ** 2) * y - (2 * b ** 2) * x + a ** 2

        d2 = b ** 2 * (x + 1) ** 2 - a ** 2 * (y + 0.5) ** 2 - a ** 2 * b ** 2
        while x < 200:
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)

            x += 1
            if d2 > 0:
                d2 += b ** 2 - (2 * b ** 2) * x
            else:
                y += 1
                d2 += (2 * a ** 2) * y - (2 * b ** 2) * x + b ** 2

    def draw_parabola(self, x0, y0, p):
        # Рисует параболу, вычисляя координаты точек.
        step = 1
        x = 0
        while x <= 200:
            y = (x ** 2) / (4 * p)
            self.draw_point(x0 + x, y0 - y)
            self.draw_point(x0 - x, y0 - y)
            x += step

    def _setup_ui(self):
        # Настраивает пользовательский интерфейс, создавая и размещая элементы.
        # Фрейм для кнопок управления
        button_panel = ttk.Frame(self)
        button_panel.pack(side="top", fill="x", padx=10, pady=5)

        # Фрейм для полей ввода размеров фигуры
        size_panel = ttk.Frame(self)
        size_panel.pack(side="top", fill="x", padx=10, pady=5)

        # Выбор типа фигуры из выпадающего списка
        self.figure_types = ["Окружность", "Эллипс", "Гипербола", "Парабола"]
        self.figure_selector = ttk.Combobox(button_panel, values=self.figure_types, state="readonly", width=13)
        self.figure_selector.set(self.selected_figure)  # Выбор фигуры по умолчанию
        self.figure_selector.pack(side="left", padx=5)
        self.figure_selector.bind("<<ComboboxSelected>>", self._set_figure_type)  # Обработка выбора

        # Кнопка для очистки холста
        self.clear_button = ttk.Button(button_panel, text="Очистить", command=self.clear_canvas)
        self.clear_button.pack(side="left", padx=5)

        # Кнопка для включения/выключения режима отладки
        self.debug_button = ttk.Button(button_panel, text="Отладка", command=self._toggle_debug_mode)
        self.debug_button.pack(side="left", padx=5)

        # Кнопка для выбора цвета
        self.color_button = ttk.Button(button_panel, text="Выбрать цвет", command=self._choose_color)
        self.color_button.pack(side="left", padx=5)

        # Фрейм для размеров справа от кнопок
        right_panel = ttk.Frame(button_panel)
        right_panel.pack(side="left", padx=5)

        self._create_labeled_input(right_panel, "Радиус/a:", 100, "size1_entry")  # Изменено название
        self._create_labeled_input(right_panel, "Высота/b:", 50, "size2_entry")   # Изменено название

        # Холст для рисования
        self.canvas = tk.Canvas(self, width=self.draw_area_width, height=self.draw_area_height, bg="white",
                                cursor="crosshair")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Фрейм для слайдера скорости отладки
        slider_panel = ttk.Frame(self)
        slider_panel.pack(side="bottom", padx=(10, 10), pady=5)

        # Фрейм для скорости отладки
        left_panel = ttk.Frame(slider_panel)
        left_panel.pack(side="left", fill="x")
        delay_label = ttk.Label(left_panel, text="Скорость отладки:")
        delay_label.pack(padx=(0, 0))  # Отрегулировано
        self.delay_slider = ttk.Scale(left_panel, from_=1, to=501, orient="horizontal", command=self._update_delay,
                                     length=200)
        self.delay_slider.set(250)
        self.delay_slider.pack(padx=(0, 0))  # Отрегулировано

    def _create_labeled_input(self, parent, label_text, default_value, attribute_name):
        # Создает label с полем ввода и сохраняет ссылку на поле ввода.
        frame = ttk.Frame(parent)
        frame.pack(side="left", padx=5)
        label = ttk.Label(frame, text=label_text)
        label.pack()
        entry = ttk.Entry(frame, width=5)
        entry.insert(0, str(default_value))
        entry.pack()
        setattr(self, attribute_name, entry)

    def _set_figure_type(self, event=None):
        # Обрабатывает выбор типа фигуры из выпадающего списка.
        self.selected_figure = self.figure_selector.get()

    def _toggle_debug_mode(self):
        # Переключает режим отладки и отображает соответствующее сообщение.
        self.is_debugging = not self.is_debugging
        if self.is_debugging:
            messagebox.showinfo("Отладка", "Режим отладки включен. Рисование будет отображаться пошагово.")
        else:
            messagebox.showinfo("Отладка", "Режим отладки выключен.")

    def _choose_color(self):
        # Открывает диалог выбора цвета и устанавливает выбранный цвет.
        color_code = colorchooser.askcolor(title="Выбрать цвет фигуры")[1]
        if color_code:
            self.selected_color = color_code

    def _update_delay(self, value):
        # Обновляет значение задержки для режима отладки на основе положения слайдера.
        self.debug_pause = int(501 - float(value))

    def _pause_if_debugging(self):
        # Приостанавливает выполнение программы в режиме отладки для визуализации.
        if self.is_debugging:
            self.update()  # Обновляем окно
            time.sleep(self.debug_pause / 1000)

    def _get_figure_sizes(self):
        # Извлекает размеры фигуры из полей ввода и возвращает их.
        # Если введены некорректные значения, отображает сообщение об ошибке и использует значения по умолчанию.
        try:
            size1 = int(self.size1_entry.get())  # Изменено название
            size2 = int(self.size2_entry.get())  # Изменено название
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные размеры. Используются значения по умолчанию (100, 50).")
            size1, size2 = 100, 50
        return size1, size2

    def _on_canvas_click(self, event):
        # Обработчик события клика на холсте.
        if self.is_drawing:
            return

        self.is_drawing = True
        size1, size2 = self._get_figure_sizes()

        if self.selected_figure == "Окружность":
            self.draw_circle(event.x, event.y, size1)
        elif self.selected_figure == "Эллипс":
            self.draw_ellipse(event.x, event.y, size1, size2)
        elif self.selected_figure == "Гипербола":
            if size1 < size2:
                messagebox.showerror("Ошибка", "Некорректные размеры: a<b")
            else:
                self.draw_hyperbola(event.x, event.y, size1, size2)
        elif self.selected_figure == "Парабола":
            self.draw_parabola(event.x, event.y, size1)

        self.is_drawing = False


if __name__ == "__main__":
    app = PaintApp()
    app.mainloop()
