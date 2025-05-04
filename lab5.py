import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np


class ShapeDesigner(tk.Tk):
    """
    Редактор фигур с алгоритмами выпуклой оболочки и отрисовки.
    """

    def __init__(self):
        super().__init__()

        self.title("Редактор фигур")
        self.geometry("800x600")

        self.vertices = []
        self.hull = []
        self.intersection_point = None
        self.selected_method = tk.StringVar(value="ЦДА")
        self.grid_enabled = tk.BooleanVar(value=True)

        self._setup_ui()
        self._bind_events()
        self.bind("<Configure>", self._on_resize)

    def _setup_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side="top", fill="x", padx=5, pady=5)

        ttk.Button(control_frame, text="Грэхем", command=self._execute_graham).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Джарвис", command=self._execute_jarvis).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Проверить выпуклость", command=self._verify_convexity).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Нарисовать линию", command=self._start_intersection_mode).pack(side="left", padx=2)
        ttk.Button(control_frame, text="Сбросить", command=self._reset_canvas).pack(side="left", padx=2)

        ttk.Label(control_frame, text="Метод:").pack(side="left", padx=5)
        method_menu = ttk.Combobox(control_frame, textvariable=self.selected_method,
                                    values=["ЦДА", "Брезенхем", "Ву"], state="readonly", width=10)
        method_menu.pack(side="left")

        ttk.Checkbutton(control_frame, text="Сетка", variable=self.grid_enabled, command=self._toggle_grid).pack(side="left", padx=5)

        self.drawing_area = tk.Canvas(self, bg="white")
        self.drawing_area.pack(fill="both", expand=True)

        self.after(100, self._draw_grid)

    def _bind_events(self):
        self.drawing_area.bind("<Button-1>", self._add_vertex)
        self.drawing_area.bind("<Button-3>", self._check_inside)

    def _add_vertex(self, event):
        self.vertices.append((event.x, event.y))
        self.drawing_area.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="black")
        if len(self.vertices) > 1:
            self.drawing_area.create_line(self.vertices[-2], self.vertices[-1], fill="black")

    def _check_inside(self, event):
        if not self.vertices:
            return
        point = (event.x, event.y)
        color = "green" if self._point_in_shape(point, self.vertices) else "red"
        self.drawing_area.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill=color)

    def _execute_graham(self):
        if len(self.vertices) < 3:
            return
        self.hull = self._graham_algorithm(self.vertices)
        self._render_hull("blue")

    def _execute_jarvis(self):
        if len(self.vertices) < 3:
            return
        self.hull = self._jarvis_algorithm(self.vertices)
        self._render_hull("purple")

    def _render_hull(self, color):
        if len(self.hull) >= 2:
            self.drawing_area.create_line(self.hull, fill=color, width=2)
            self.drawing_area.create_line(self.hull[-1], self.hull[0], fill=color, width=2)

    def _reset_canvas(self):
        self.drawing_area.delete("all")
        self.vertices.clear()
        self.hull.clear()
        if self.grid_enabled.get():
            self._draw_grid()

    def _toggle_grid(self):
        if self.grid_enabled.get():
            self._draw_grid()
        else:
            self.drawing_area.delete("grid")

    def _draw_grid(self, spacing=20):
        self.drawing_area.delete("grid")
        width = self.drawing_area.winfo_width()
        height = self.drawing_area.winfo_height()

        for x in range(0, width, spacing):
            self.drawing_area.create_line(x, 0, x, height, fill="#ddd", tags="grid")

        for y in range(0, height, spacing):
            self.drawing_area.create_line(0, y, width, y, fill="#ddd", tags="grid")

    def _on_resize(self, event):
        if self.grid_enabled.get():
            self._draw_grid()

    def _start_intersection_mode(self):
        if len(self.vertices) < 3:
            messagebox.showerror("Ошибка", "Недостаточно точек для фигуры")
            return

        def first_click(event):
            self.intersection_point = (event.x, event.y)
            self.drawing_area.bind("<Button-1>", second_click)

        def second_click(event):
            x1, y1 = self.intersection_point
            x2, y2 = event.x, event.y

            points = []
            if self.selected_method.get() == "ЦДА":
                points = self._draw_dda(x1, y1, x2, y2)
            elif self.selected_method.get() == "Брезенхем":
                points = self._draw_bresenham(x1, y1, x2, y2)
            elif self.selected_method.get() == "Ву":
                points = self._draw_wu(x1, y1, x2, y2)

            for px, py in points:
                self.drawing_area.create_line(px, py, px + 1, py, fill="blue")

            intersects = self._find_intersections((x1, y1), (x2, y2), self.vertices)
            if intersects:
                for x, y in intersects:
                    self.drawing_area.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red")
                msg = "\n".join([f"({x:.2f}, {y:.2f})" for x, y in intersects])
                messagebox.showinfo("Пересечения", msg)
            else:
                messagebox.showinfo("Пересечения", "Нет пересечений")

            self.drawing_area.bind("<Button-1>", self._add_vertex)

        self.drawing_area.bind("<Button-1>", first_click)

    def _verify_convexity(self):
        if not self.vertices:
            messagebox.showwarning("Ошибка", "Фигура не задана!")
            return
        if self._is_convex(self.vertices):
            messagebox.showinfo("Результат", "Фигура выпуклая ✅")
        else:
            messagebox.showwarning("Результат", "Фигура НЕ выпуклая ❌")

    @staticmethod
    def _draw_dda(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy))
        x_inc, y_inc = dx / steps, dy / steps
        x, y = x1, y1
        return [(round(x + i * x_inc), round(y + i * y_inc)) for i in range(int(steps) + 1)]

    @staticmethod
    def _draw_bresenham(x1, y1, x2, y2):
        points = []
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
        err = dx - dy
        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    @staticmethod
    def _draw_wu(x1, y1, x2, y2):
        points = []
        dx, dy = x2 - x1, y2 - y1
        steep = abs(dy) > abs(dx)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dx, dy = x2 - x1, y2 - y1
        gradient = dy / dx if dx else 1
        y = y1 + 0.5
        for x in range(x1, x2 + 1):
            yi = int(y)
            points.append((yi, x) if steep else (x, yi))
            y += gradient
        return points

    @staticmethod
    def _orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        return 0 if val == 0 else (1 if val > 0 else -1)

    def _is_convex(self, vertices):
        if len(vertices) < 3:
            return False
        dir = None
        for i in range(len(vertices)):
            p1, p2, p3 = vertices[i], vertices[(i + 1) % len(vertices)], vertices[(i + 2) % len(vertices)]
            turn = self._orientation(p1, p2, p3)
            if turn != 0:
                if dir is None:
                    dir = turn
                elif turn != dir:
                    return False
        return True

    @staticmethod
    def _point_in_shape(point, vertices):
        x, y = point
        inside = False
        x0, y0 = vertices[-1]
        for x1, y1 in vertices:
            if min(y0, y1) < y <= max(y0, y1) and x <= max(x0, x1):
                xinters = (y - y0) * (x1 - x0) / (y1 - y0 + 1e-9) + x0 if y0 != y1 else x0
                if x <= xinters:
                    inside = not inside
            x0, y0 = x1, y1
        return inside

    def _graham_algorithm(self, points):
        points = sorted(points, key=lambda p: (p[1], p[0]))
        first_point = points[0]
        sorted_points = sorted(points[1:], key=lambda p: np.arctan2(p[1] - first_point[1], p[0] - first_point[0]))
        stack = [first_point, sorted_points[0]]
        for p in sorted_points[1:]:
            while len(stack) > 1 and self._orientation(stack[-2], stack[-1], p) != -1:
                stack.pop()
            stack.append(p)
        return stack

    def _jarvis_algorithm(self, points):
        if len(points) < 3:
            return points
        hull = []
        leftmost = min(points, key=lambda p: p[0])
        current = leftmost
        while True:
            hull.append(current)
            next_point = points[0]
            for candidate in points[1:]:
                if candidate == current:
                    continue
                orient = self._orientation(current, next_point, candidate)
                if orient == -1 or (orient == 0 and np.linalg.norm(np.array(candidate) - np.array(current)) > np.linalg.norm(np.array(next_point) - np.array(current))):
                    next_point = candidate
            current = next_point
            if current == leftmost:
                break
        return hull

    def _find_intersections(self, p1, p2, vertices):
        intersections = []
        x1, y1 = p1
        x2, y2 = p2
        for i in range(len(vertices)):
            x3, y3 = vertices[i]
            x4, y4 = vertices[(i + 1) % len(vertices)]
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if d == 0:
                continue
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / d
            if 0 <= t <= 1 and 0 <= u <= 1:
                ix = x1 + t * (x2 - x1)
                iy = y1 + t * (y2 - y1)
                intersections.append((ix, iy))
        return intersections


if __name__ == "__main__":
    app = ShapeDesigner()
    app.mainloop()