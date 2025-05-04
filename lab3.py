import tkinter as tk
from tkinter import ttk
import numpy as np


class CurveDesigner(tk.Tk):
    """
    Программа для построения кривых Безье, Эрмита и B-сплайнов.
    """

    def __init__(self):
        super().__init__()

        self.title("Редактор кривых")
        self.geometry("850x600")

        self.canvas_width = 640
        self.canvas_height = 480

        self.points = []
        self.active_point_idx = None
        self.curve_kind = "Безье"
        self.grid_enabled = True

        self._init_interface()
        self._position_window_center()
        self._draw_grid()

    def _init_interface(self):
        """Создает интерфейс пользователя."""
        controls = ttk.Frame(self)
        controls.pack(side="top", fill="x", padx=8, pady=4)

        self.curve_selector = ttk.Combobox(controls, values=["Безье", "Эрмит", "B-сплайн"], state="readonly", width=15)
        self.curve_selector.set(self.curve_kind)
        self.curve_selector.pack(side="left", padx=5)
        self.curve_selector.bind("<<ComboboxSelected>>", self._update_curve_kind)

        self.btn_clear = ttk.Button(controls, text="Очистить", command=self._clear_canvas)
        self.btn_clear.pack(side="left", padx=5)

        self.btn_toggle_grid = ttk.Button(controls, text="Сетка", command=self._toggle_grid)
        self.btn_toggle_grid.pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", cursor="cross")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._canvas_click)
        self.canvas.bind("<B1-Motion>", self._move_point)
        self.canvas.bind("<ButtonRelease-1>", self._release_point)

    def _position_window_center(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        ww, wh = self.winfo_width(), self.winfo_height()
        x, y = (sw - ww) // 2, (sh - wh) // 2
        self.geometry(f"{ww}x{wh}+{x}+{y}")

    def _draw_grid(self):
        """Рисует сетку на холсте."""
        if not self.grid_enabled:
            return
        spacing = 20
        for x in range(0, self.canvas_width, spacing):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="#eee", tags="grid")
        for y in range(0, self.canvas_height, spacing):
            self.canvas.create_line(0, y, self.canvas_width, y, fill="#eee", tags="grid")

    def _clear_canvas(self):
        """Очищает холст и список точек."""
        self.points.clear()
        self.canvas.delete("all")
        self._draw_grid()

    def _toggle_grid(self):
        """Включает или выключает отображение сетки."""
        self.grid_enabled = not self.grid_enabled
        self._redraw_all()

    def _canvas_click(self, event):
        """Добавление новой точки или выделение существующей."""
        nearest = None
        min_dist_sq = float('inf')
        for idx, (px, py) in enumerate(self.points):
            dist_sq = (px - event.x)**2 + (py - event.y)**2
            if dist_sq < 100 and dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = idx

        if nearest is not None:
            self.active_point_idx = nearest
        else:
            self.points.append((event.x, event.y))
            self._redraw_all()

    def _move_point(self, event):
        """Перемещение точки мышью."""
        if self.active_point_idx is not None:
            self.points[self.active_point_idx] = (event.x, event.y)
            self._redraw_all()

    def _release_point(self, event):
        """Отпускание точки."""
        self.active_point_idx = None

    def _update_curve_kind(self, event=None):
        """Изменяет тип текущей кривой."""
        self.curve_kind = self.curve_selector.get()
        self._redraw_all()

    def _redraw_all(self):
        """Перерисовывает весь холст."""
        self.canvas.delete("all")
        self._draw_grid()

        for x, y in self.points:
            self._draw_marker(x, y)

        if self.curve_kind == "Безье":
            self._draw_bezier()
        elif self.curve_kind == "Эрмит":
            self._draw_hermite()
        elif self.curve_kind == "B-сплайн":
            self._draw_bspline()

    def _draw_marker(self, x, y):
        """Рисует маркер точки."""
        r = 4
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="black")

    def _draw_bezier(self):
        if len(self.points) < 4:
            return
        step_count = 120
        for i in range(len(self.points) - 3):
            pts = self.points[i:i+4]
            for t in np.linspace(0, 1, step_count):
                x, y = self._bezier_coords(pts, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="black", outline="")

    def _draw_hermite(self):
        if len(self.points) < 4:
            return
        step_count = 120
        for i in range(0, len(self.points) - 3, 3):
            pts = self.points[i:i+4]
            for t in np.linspace(0, 1, step_count):
                x, y = self._hermite_coords(pts, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="blue", outline="")

    def _draw_bspline(self):
        if len(self.points) < 4:
            return
        step_count = 120
        for i in range(len(self.points) - 3):
            pts = self.points[i:i+4]
            for t in np.linspace(0, 1, step_count):
                x, y = self._bspline_coords(pts, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="green", outline="")

    def _bezier_coords(self, pts, t):
        """Вычисляет координаты Безье."""
        M = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 3, 0, 0], [1, 0, 0, 0]])
        T = np.array([t**3, t**2, t, 1])
        P = np.array(pts)
        return T @ M @ P

    def _hermite_coords(self, pts, t):
        """Вычисляет координаты Эрмита."""
        h1 = 2*t**3 - 3*t**2 + 1
        h2 = -2*t**3 + 3*t**2
        h3 = t**3 - 2*t**2 + t
        h4 = t**3 - t**2
        x = h1 * pts[0][0] + h2 * pts[3][0] + h3 * (pts[1][0] - pts[0][0]) + h4 * (pts[2][0] - pts[3][0])
        y = h1 * pts[0][1] + h2 * pts[3][1] + h3 * (pts[1][1] - pts[0][1]) + h4 * (pts[2][1] - pts[3][1])
        return x, y

    def _bspline_coords(self, pts, t):
        """Вычисляет координаты B-сплайна."""
        B = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]]) / 6
        T = np.array([t**3, t**2, t, 1])
        P = np.array(pts)
        return T @ B @ P


if __name__ == "__main__":
    app = CurveDesigner()
    app.mainloop()
