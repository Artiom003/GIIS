import tkinter as tk
from tkinter import ttk, BooleanVar, colorchooser


class ShapePainter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Редактор фигур")
        self.geometry("700x500")

        self.canvas_width = 640
        self.canvas_height = 400

        self.points = []
        self.is_closed = False
        self.debug_mode = BooleanVar(value=False)
        self.fill_strategy = tk.StringVar(value="Упорядоченный список рёбер")
        self.fill_color = "red"

        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", padx=8, pady=4)

        ttk.Button(toolbar, text="Очистить", command=self._clear_canvas).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Завершить", command=self._finish_shape).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Заливка", command=self._fill_shape).pack(side="left", padx=5)
        ttk.Checkbutton(toolbar, text="Режим отладки", variable=self.debug_mode).pack(side="left", padx=5)

        ttk.Combobox(toolbar, textvariable=self.fill_strategy, values=[
            "Упорядоченный список рёбер",
            "Активный список рёбер",
            "Затравочный (пиксельный)",
            "Затравочный (построчный)"
        ], state="readonly", width=30).pack(side="left", padx=5)

        ttk.Button(toolbar, text="Цвет", command=self._select_color).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", cursor="cross")
        self.canvas.pack(pady=10)

        self.image = tk.PhotoImage(width=self.canvas_width, height=self.canvas_height)
        self.canvas.create_image((0, 0), image=self.image, anchor="nw")

        self.canvas.bind("<Button-1>", self._add_point)
        self.canvas.bind("<Button-3>", self._start_fill)

    def _center_window(self):
        self.update_idletasks()
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        window_width, window_height = self.winfo_width(), self.winfo_height()
        x, y = (screen_width - window_width) // 2, (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _select_color(self):
        color = colorchooser.askcolor(title="Выберите цвет заливки")[1]
        if color:
            self.fill_color = color

    def _add_point(self, event):
        if self.is_closed:
            return

        self.points.append((event.x, event.y))
        self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="black")

        if len(self.points) > 1:
            self.canvas.create_line(self.points[-2], self.points[-1], fill="black")

    def _finish_shape(self):
        if len(self.points) > 2 and not self.is_closed:
            self.is_closed = True
            self.canvas.create_line(self.points[-1], self.points[0], fill="black")

    def _clear_canvas(self):
        self.canvas.delete("all")
        self.image = tk.PhotoImage(width=self.canvas_width, height=self.canvas_height)
        self.canvas.create_image((0, 0), image=self.image, anchor="nw")
        self.points.clear()
        self.is_closed = False

    def _fill_shape(self):
        if not self.is_closed:
            print("Сначала завершите фигуру!")
            return

        strategy = self.fill_strategy.get()
        edges = self._extract_edges()

        if strategy == "Упорядоченный список рёбер":
            self._scanline_fill(edges, active_list=False)
        elif strategy == "Активный список рёбер":
            self._scanline_fill(edges, active_list=True)
        elif "Затравочный" in strategy:
            print("Кликните правой кнопкой мыши внутри фигуры для затравочной заливки.")

    def _extract_edges(self):
        edges = []
        for i in range(len(self.points)):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % len(self.points)]
            if y1 != y2:
                if y1 > y2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                edges.append({
                    "y_min": y1,
                    "y_max": y2,
                    "x": x1,
                    "inv_slope": (x2 - x1) / (y2 - y1)
                })
        edges.sort(key=lambda e: e["y_min"])
        return edges

    def _scanline_fill(self, edges, active_list=False):
        if not edges:
            return

        edges = edges.copy()
        y = edges[0]["y_min"]
        active_edge_table = []

        def step():
            nonlocal y, active_edge_table, edges

            active_edge_table.extend([e for e in edges if e["y_min"] == y])
            edges[:] = [e for e in edges if e["y_min"] != y]

            active_edge_table[:] = [e for e in active_edge_table if e["y_max"] > y]

            if not active_edge_table and not edges:
                return

            if active_list:
                for edge in active_edge_table:
                    edge["x"] += edge["inv_slope"]
            else:
                for edge in active_edge_table:
                    edge["x"] = edge["x0"] + (y - edge["y_min"]) * edge["inv_slope"]

            active_edge_table.sort(key=lambda e: e["x"])

            for i in range(0, len(active_edge_table), 2):
                if i + 1 < len(active_edge_table):
                    x1, x2 = int(active_edge_table[i]["x"]), int(active_edge_table[i + 1]["x"])
                    self.canvas.create_line(x1, y, x2, y, fill=self.fill_color)
                    if self.debug_mode.get():
                        print(f"({x1}, {y}) -> ({x2}, {y})")

            y += 1
            self.after(30 if self.debug_mode.get() else 1, step)

        for edge in edges:
            edge["x0"] = edge["x"]

        step()

    def _start_fill(self, event):
        strategy = self.fill_strategy.get()
        if strategy == "Затравочный (пиксельный)":
            self._flood_fill(event.x, event.y, mode="pixel")
        elif strategy == "Затравочный (построчный)":
            self._flood_fill(event.x, event.y, mode="line")

    def _flood_fill(self, x, y, mode="pixel"):
        if not self._is_inside_polygon(x, y):
            print("Клик вне фигуры.")
            return

        stack = [(x, y)]
        visited = set()

        def step():
            if not stack:
                return

            px, py = stack.pop()
            if (px, py) in visited or not self._is_inside_polygon(px, py):
                self.after(1, step)
                return

            visited.add((px, py))

            if mode == "pixel":
                self.image.put(self.fill_color, (px, py))
                stack.extend([(px + dx, py + dy) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))])
            else:
                left, right = px, px
                while left > 0 and self._is_inside_polygon(left - 1, py) and (left - 1, py) not in visited:
                    left -= 1
                while right < self.canvas_width - 1 and self._is_inside_polygon(right + 1, py) and (right + 1, py) not in visited:
                    right += 1

                for i in range(left, right + 1):
                    self.image.put(self.fill_color, (i, py))
                    visited.add((i, py))

                for ny in [py - 1, py + 1]:
                    if 0 <= ny < self.canvas_height:
                        for i in range(left, right + 1):
                            if (i, ny) not in visited and self._is_inside_polygon(i, ny):
                                stack.append((i, ny))
                                break

            if self.debug_mode.get():
                self.update()
            self.after(1, step)

    def _is_inside_polygon(self, x, y):
        n = len(self.points)
        inside = False
        px1, py1 = self.points[0]

        for i in range(n + 1):
            px2, py2 = self.points[i % n]
            if min(py1, py2) < y <= max(py1, py2) and x <= max(px1, px2):
                if py1 != py2:
                    xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                if px1 == px2 or x <= xinters:
                    inside = not inside
            px1, py1 = px2, py2

        return inside


if __name__ == "__main__":
    app = ShapePainter()
    app.mainloop()