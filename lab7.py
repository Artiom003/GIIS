import tkinter as tk
from tkinter import ttk
import numpy as np
import scipy.spatial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d


class ShapeVisualizer(tk.Tk):
    """
    Программа для построения триангуляции и диаграммы Вороного.
    """

    def __init__(self):
        super().__init__()

        self.title("Триангуляция и диаграмма Вороного")
        self.geometry("850x650")
        self.config(bg="#f0f0f0")  # Светлый фон для окна

        self.canvas_dimension = 600
        self.coords = []

        self._setup_ui()

    def _setup_ui(self):
        """Создает интерфейс пользователя."""
        control_panel = ttk.Frame(self, padding="10 5 10 5", style="TFrame")
        control_panel.pack(side="top", fill="x", padx=8, pady=10)

        # Настраиваем стиль для кнопок
        style = ttk.Style()
        style.configure("TButton",
                        font=("Helvetica", 12),
                        background="#4CAF50",  # Зеленый фон
                        foreground="black",
                        padding=10)
        style.map("TButton", background=[("active", "#45a049")])  # Изменение цвета при наведении

        self.btn_triangulate = ttk.Button(control_panel, text="Триангуляция", command=self.perform_triangulation)
        self.btn_triangulate.pack(side="left", padx=5)

        self.btn_voronoi = ttk.Button(control_panel, text="Вороной", command=self.draw_voronoi)
        self.btn_voronoi.pack(side="left", padx=5)

        self.btn_reset = ttk.Button(control_panel, text="Очистить", command=self.reset_canvas)
        self.btn_reset.pack(side="left", padx=5)

        # Создание области для графика
        self.figure, self.axis = plt.subplots(figsize=(6, 6))
        self.axis.set_xlim(0, self.canvas_dimension)
        self.axis.set_ylim(0, self.canvas_dimension)
        self.axis.set_aspect('equal')
        self.axis.set_facecolor('#e7f3ff')  # Светлый фон для осей

        # Добавляем рамку вокруг холста
        self.canvas_container = ttk.Frame(self, borderwidth=2, relief="solid", padding=5)
        self.canvas_container.pack(pady=20)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect("button_press_event", self.add_point)

    def add_point(self, event):
        """Добавление точки при клике."""
        if event.xdata is not None and event.ydata is not None:
            if 0 <= event.xdata <= self.canvas_dimension and 0 <= event.ydata <= self.canvas_dimension:
                self.coords.append((event.xdata, event.ydata))
                self.axis.plot(event.xdata, event.ydata, "ko")
                self.canvas.draw()

    def perform_triangulation(self):
        """Построение триангуляции."""
        if len(self.coords) < 3:
            print("Нужно хотя бы 3 точки!")
            return

        self.axis.clear()
        self.axis.set_xlim(0, self.canvas_dimension)
        self.axis.set_ylim(0, self.canvas_dimension)
        self.axis.set_title("Триангуляция", fontsize=16)

        points_array = np.array(self.coords)
        self.axis.plot(points_array[:, 0], points_array[:, 1], "ko")

        # Используем scipy для триангуляции
        delaunay_result = scipy.spatial.Delaunay(points_array)

        for triangle in delaunay_result.simplices:
            for i in range(3):
                p1 = points_array[triangle[i]]
                p2 = points_array[triangle[(i + 1) % 3]]
                self.axis.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', linewidth=1.5)

        self.canvas.draw()

    def draw_voronoi(self):
        """Строит диаграмму Вороного."""
        if len(self.coords) < 3:
            print("Нужно больше точек для диаграммы Вороного!")
            return

        try:
            # Используем SciPy для построения диаграммы Вороного
            points_array = np.array(self.coords)  # Преобразуем список точек в массив NumPy
            voronoi_result = Voronoi(points_array)

            # Отображаем диаграмму Вороного
            self.axis.clear()
            self.axis.set_xlim(0, self.canvas_dimension)
            self.axis.set_ylim(0, self.canvas_dimension)
            self.axis.set_title("Диаграмма Вороного", fontsize=16)

            # Параметры для отображения диаграммы
            voronoi_plot_2d(voronoi_result, ax=self.axis, show_vertices=False, line_colors='red', line_width=2, line_alpha=0.6)

            self.canvas.draw()

        except Exception as e:
            print(f"Ошибка при построении диаграммы Вороного: {e}")

    def reset_canvas(self):
        """Очистка экрана."""
        self.coords.clear()
        self.axis.clear()
        self.axis.set_xlim(0, self.canvas_dimension)
        self.axis.set_ylim(0, self.canvas_dimension)
        self.axis.set_aspect('equal')
        self.axis.set_facecolor('#e7f3ff')  # Восстанавливаем фон
        self.canvas.draw()


if __name__ == "__main__":
    app = ShapeVisualizer()
    app.mainloop()