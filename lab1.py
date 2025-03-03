import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw


class LineEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Line Drawing Editor")
        self.geometry("800x650")
        self.resizable(False, False)

        self.canvas_width = 600
        self.canvas_height = 500
        self.current_algorithm = None
        self.points = []
        self.debug_mode = False
        self.delay = 10
        self.line_width = 1
        self.is_drawing = False
        self.button_states = {}
        self.buttons = {}
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.algorithm_combobox = None
        self.line_color = "black"
        self.init_ui()
        self.center_window()
        self.draw_grid()
        self.update_canvas_image()

    def center_window(self):
        """Центрирует окно приложения."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def init_ui(self):
        button_frame = ttk.Frame(self)
        button_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.algorithm_var = tk.StringVar(self)
        self.algorithm_var.set("ЦДА")
        self.algorithm_combobox = ttk.Combobox(button_frame, textvariable=self.algorithm_var,
                                               values=["ЦДА", "Брезенхем", "Ву"],
                                               state="readonly")
        self.algorithm_combobox.bind("<<ComboboxSelected>>", self.on_algorithm_selected)

        self.buttons["draw_line_btn"] = ttk.Button(button_frame, text="Нарисовать линию", command=self.enable_drawing)
        self.buttons["draw_line_btn"].pack(side="left", padx=5)

        self.buttons["debug_btn"] = ttk.Button(button_frame, text="Отладка", command=self.toggle_debug_mode)
        self.buttons["debug_btn"].pack(side="left", padx=5)

        self.buttons["clear_btn"] = ttk.Button(button_frame, text="Очистить", command=self.clear_canvas)
        self.buttons["clear_btn"].pack(side="left", padx=5)

        self.buttons["color_btn"] = ttk.Button(button_frame, text="Выбрать цвет", command=self.choose_color)
        self.buttons["color_btn"].pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white",
                                cursor="crosshair")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        slider_frame = ttk.Frame(self)
        slider_frame.pack(side="bottom", padx=(10, 10), pady=5)

        # Фрейм для координат
        coord_frame = ttk.Frame(self)
        coord_frame.pack(padx=(300, 0), fill="x", pady=5)
        self.coord_label = tk.Label(coord_frame, text="Координаты: ")
        self.coord_label.pack(side="left")
        empty_label_right = tk.Label(coord_frame, text="")  # пустой label для выравнивания
        empty_label_right.pack(padx=(150, 0))

        # Фрейм для ползунков
        slider_frame = ttk.Frame(self)
        slider_frame.pack(side="top", fill="x", pady=5)

        # Левый фрейм (скорость отладки)
        left_frame = ttk.Frame(slider_frame)
        left_frame.pack(side="left", fill="x")  # Убрали expand=True
        delay_label = ttk.Label(left_frame, text="Скорость отладки:")
        delay_label.pack(padx=(150, 0))
        self.delay_scale = ttk.Scale(left_frame, from_=1, to=501, orient="horizontal", command=self.update_delay,
                                     length=200)
        self.delay_scale.set(250)
        self.delay_scale.pack(padx=(150, 0))

        # Правый фрейм (толщина линии)
        right_frame = ttk.Frame(slider_frame)
        right_frame.pack(side="right", fill="x")  # Убрали expand=True
        line_width_label = ttk.Label(right_frame, text="Толщина линии:")
        line_width_label.pack(padx=(0, 150))
        self.line_width_scale = ttk.Scale(right_frame, from_=1, to=10, orient="horizontal",
                                          command=self.update_line_width, length=200)
        self.line_width_scale.set(5)
        self.line_width_scale.pack(padx=(0, 150))

        for key, btn in self.buttons.items():
            self.button_states[key] = btn['state']

    def enable_drawing(self):
        if self.algorithm_combobox is not None:
            self.algorithm_combobox.pack(side="left", padx=5)
            self.on_algorithm_selected(None)
            self.buttons["draw_line_btn"].config(state="disabled")

    def update_delay(self, value):
        self.delay = int(501 - float(value))

    def update_line_width(self, value):
        self.line_width = int(float(value))

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            messagebox.showinfo("Отладка", "Отладочный режим включен. Рисование будет отображаться пошагово.")
            self.draw_grid()
        else:
            self.draw_grid()
            messagebox.showinfo("Отладка", "Отладочный режим выключен.")

    def on_algorithm_selected(self, event):
        selected_algorithm = self.algorithm_var.get()
        self.current_algorithm = selected_algorithm.lower()

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выбрать цвет линии")[1]
        if color_code:
            self.line_color = color_code

    def on_canvas_click(self, event):
        if self.is_drawing:
            return

        if not self.current_algorithm:
            messagebox.showwarning("Внимание", "Выберите алгоритм перед рисованием!")
            return

        x = event.x
        y = event.y

        self.points.append((x, y))
        self.update_coord_label()
        if self.debug_mode:
            self.draw_grid()

        self.update_canvas_image()

        if len(self.points) == 2:
            self.is_drawing = True
            self.lock_buttons()
            self.draw_line()
            self.points = []
            self.is_drawing = False
            self.unlock_buttons()
            self.update_canvas_image()

    def update_coord_label(self):
        coords_str = ", ".join(f"({x}, {y})" for x, y in self.points)
        self.coord_label.config(text=f"Координаты: {coords_str}")

    def draw_grid(self):
        for i in range(0, self.canvas_width, 10):
            self.draw.line((i, 0, i, self.canvas_height), fill="lightgray")
        for j in range(0, self.canvas_height, 10):
            self.draw.line((0, j, self.canvas_width, j), fill="lightgray")

    def clear_canvas(self):
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.points = []
        self.update_coord_label()
        self.draw_grid()
        self.is_drawing = False
        self.update_canvas_image()

    def lock_buttons(self):
        for key, btn in self.buttons.items():
            btn.config(state="disabled")

    def unlock_buttons(self):
        for key, btn in self.buttons.items():
            btn.config(state=self.button_states[key])

    def update_canvas_image(self):
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def draw_line(self):
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]

        if x1 == x2 and y1 == y2:
            messagebox.showwarning("Внимание", "Выберите разные точки для отрисовки линии!")
            self.is_drawing = False
            self.unlock_buttons()
            self.points = []
            self.update_coord_label()
            return

        if self.current_algorithm == "цда":
            segment = dda_line(x1, y1, x2, y2, debug=self.debug_mode)
            self.draw_line_segments(segment, self.line_color)
        elif self.current_algorithm == "брезенхем":
            segment = bresenham_line(x1, y1, x2, y2, debug=self.debug_mode)
            self.draw_line_segments(segment, self.line_color)
        elif self.current_algorithm == "ву":
            segment = wu_line(x1, y1, x2, y2, debug=self.debug_mode)
            self.draw_line_segments(segment, self.line_color)

    def draw_line_segments(self, segments, color):
        for x, y in segments:
            self.draw_pixel(x, y, color)
            if self.debug_mode:
                self.update_canvas_image()
                self.update()
                self.after(self.delay)

    def draw_pixel(self, x, y, color="black"):
        # Отрисовка пикселя с учетом размера grid_size и толщины линии
        for i in range(x - self.line_width // 2, x + (self.line_width + 1) // 2):
            for j in range(y - self.line_width // 2, y + (self.line_width + 1) // 2):
                if 0 <= i < self.canvas_width and 0 <= j < self.canvas_height:
                    self.draw.rectangle((i, j, i, j), fill=color)


def dda_line(x1, y1, x2, y2, debug=False):
    if debug:
        print("Начало построения DDA")

    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    x_inc = dx / float(steps)  # приращение по x
    y_inc = dy / float(steps)
    x = x1
    y = y1
    points = []
    for _ in range(int(steps) + 1):
        point = (round(x), round(y))
        points.append(point)
        if debug:
            print(f"DDA: {point}")
        x += x_inc
        y += y_inc

    if debug:
        print("Завершение построения DDA")
    return points


def bresenham_line(x1, y1, x2, y2, debug=False):
    if debug:
        print("Начало построения Bresenham")

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1  # направление слева направо если 1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    points = []
    x = x1
    y = y1

    while True:
        point = (x, y)
        points.append(point)
        if debug:
            print(f"Bresenham: {point}")
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    if debug:
        print("Завершение построения Bresenham")
    return points


def wu_line(x1, y1, x2, y2, debug=False):
    def ipart(x):
        return int(x)

    def fpart(x):
        return x - int(x)

    def rfpart(x):
        return 1 - fpart(x)

    if x1 == x2 and y1 == y2:
        return []

    points = []

    def plot(x, y, c):
        point = (int(round(x)), int(round(y)))
        points.append(point)
        if debug:
            print(f"Wu: {point}, {round(c, 2)}")

    if debug:
        print("Начало построения Wu")

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > abs(dy):
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        gradient = dy / dx
        x_end = round(x1)
        y_end = y1 + gradient * (x_end - x1)
        xpxl1 = x_end
        ypxl1 = ipart(y_end)
        plot(xpxl1, ypxl1, rfpart(y_end))
        plot(xpxl1, ypxl1 + 1, fpart(y_end))
        intery = y_end + gradient

        x_end = round(x2)
        y_end = y2 + gradient * (x_end - x2)
        xpxl2 = x_end
        ypxl2 = ipart(y_end)
        plot(xpxl2, ypxl2, rfpart(y_end))
        plot(xpxl2, ypxl2 + 1, fpart(y_end))
        for x in range(xpxl1 + 1, xpxl2):
            plot(x, ipart(intery), rfpart(intery))
            plot(x, ipart(intery) + 1, fpart(intery))
            intery += gradient
    else:
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        gradient = dx / dy
        y_end = round(y1)
        x_end = x1 + gradient * (y_end - y1)
        ypxl1 = y_end
        xpxl1 = ipart(x_end)
        plot(xpxl1, ypxl1, rfpart(x_end))
        plot(xpxl1 + 1, ypxl1, fpart(x_end))
        interx = x_end + gradient

        y_end = round(y2)
        x_end = x2 + gradient * (y_end - y2)
        ypxl2 = y_end
        xpxl2 = ipart(x_end)
        plot(xpxl2, ypxl2, rfpart(x_end))
        plot(xpxl2 + 1, ypxl2, fpart(x_end))
        for y in range(ypxl1 + 1, ypxl2):
            plot(ipart(interx), y, rfpart(interx))
            plot(ipart(interx) + 1, y, fpart(interx))
            interx += gradient

    if debug:
        print("Завершение построения Wu")
    return points


if __name__ == "__main__":
    app = LineEditor()
    app.mainloop()