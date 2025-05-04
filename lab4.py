import pygame
from transformations import *

"""Настройки экрана"""
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

"""Камера"""
DISTANCE = 5

"""Доступные файлы и цвета"""
OBJECT_FILES = {
    1: ("Куб", "cube.txt"),
    2: ("Пирамида", "pyramid.txt"),
    3: ("Тетраэдр", "tetrahedron.txt"),
    4: ("Призма", "prism.txt")
}

OBJECT_COLORS = {
    "cube.txt": (0, 100, 255),
    "pyramid.txt": (0, 200, 0),
    "tetrahedron.txt": (200, 0, 200),
    "prism.txt": (255, 165, 0)
}

OBJECT_COLORS_NAME = {
    "Куб": (0, 100, 255),
    "Пирамида": (0, 200, 0),
    "Тетраэдр": (200, 0, 200),
    "Призма": (255, 165, 0)
}

"""Рёбра фигур"""
EDGES_MAP = {
    "cube.txt": [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)],
    "pyramid.txt": [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (4, 1)],
    "tetrahedron.txt": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "prism.txt": [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
}

def load_object(filename):
    """Загружает вершины объекта из файла"""
    points = []
    with open(filename, 'r') as file:
        for line in file:
            x, y, z = map(float, line.split())
            points.append([x, y, z, 1])
    return np.array(points)

def project(points):
    """Проецирует 3D-точки на 2D"""
    projected = transform_points(points, create_perspective_matrix(DISTANCE))
    projected[:, :2] /= projected[:, 3].reshape(-1, 1)
    return projected[:, :2]

def draw_edges(screen, projected, edges, color):
    """Рисует рёбра объекта"""
    for start, end in edges:
        p1, p2 = projected[start], projected[end]
        pygame.draw.line(
            screen,
            color,
            (p1[0] + WIDTH // 2, -p1[1] + HEIGHT // 2),
            (p2[0] + WIDTH // 2, -p2[1] + HEIGHT // 2),
            2
        )


def draw_text(screen, text, x, y, size=25, color=(0, 0, 0)):
    """Отображает текст на экране"""
    font = pygame.font.SysFont("Arial", size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def create_initial_transform():
    """Создаёт начальное масштабирование"""
    return create_scale_matrix(140, 140, 140)


def load_figure(number):
    """Загружает фигуру по её номеру"""
    name, filename = OBJECT_FILES[number]
    points = load_object(filename)
    edges = EDGES_MAP[filename]
    color = OBJECT_COLORS[filename]
    return points, edges, color, name

def main():
    """Главный цикл программы"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Viewer")
    clock = pygame.time.Clock()

    """Изначально загружаем Куб"""
    current_number = 1
    points, edges, color, name = load_figure(current_number)
    transform = create_initial_transform()

    mirror_delay_ms = 300  # Более явное название единиц измерения
    last_mirror_time_ms = pygame.time.get_ticks()

    running = True  # Более понятное имя переменной

    while running:
        screen.fill(WHITE)

        transformed_points = transform_points(points, transform)
        projected_points = project(transformed_points)

        draw_edges(screen, projected_points, edges, color)

        draw_text(screen, "1.Куб", 10, 10, size=20, color=(0, 100, 255))
        draw_text(screen, "2.Пирамида", 10, 30, size=20, color=(0, 200, 0))
        draw_text(screen, "3.Тетраэдр", 10, 50, size=20, color=(200, 0, 200))
        draw_text(screen, "4.Призма", 10, 70, size=20, color=(255, 165, 0))
        draw_text(screen, f"Текущая фигура: {name}", 10, 100, size=20, color=OBJECT_COLORS_NAME[name])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_number = 1
                    points, edges, color, name = load_figure(current_number)
                    transform = create_initial_transform()
                if event.key == pygame.K_2:
                    current_number = 2
                    points, edges, color, name = load_figure(current_number)
                    transform = create_initial_transform()
                if event.key == pygame.K_3:
                    current_number = 3
                    points, edges, color, name = load_figure(current_number)
                    transform = create_initial_transform()
                if event.key == pygame.K_4:
                    current_number = 4
                    points, edges, color, name = load_figure(current_number)
                    transform = create_initial_transform()

        keys = pygame.key.get_pressed()
        current_time_ms = pygame.time.get_ticks()

        rotation_speed = 0.05  # Радианы за кадр
        translation_speed = 0.1 # Единицы за кадр
        scale_factor = 0.05    #Процент маштаба в каждом кадре

        if keys[pygame.K_LEFT]:
            transform = transform @ create_rotation_matrix_y(rotation_speed)
        if keys[pygame.K_RIGHT]:
            transform = transform @ create_rotation_matrix_y(-rotation_speed)
        if keys[pygame.K_UP]:
            transform = transform @ create_rotation_matrix_x(rotation_speed)
        if keys[pygame.K_DOWN]:
            transform = transform @ create_rotation_matrix_x(-rotation_speed)

        if keys[pygame.K_w]:
            transform = transform @ create_translation_matrix(0, 0, translation_speed)
        if keys[pygame.K_s]:
            transform = transform @ create_translation_matrix(0, 0, -translation_speed)
        if keys[pygame.K_a]:
            transform = transform @ create_translation_matrix(-translation_speed, 0, 0)
        if keys[pygame.K_d]:
            transform = transform @ create_translation_matrix(translation_speed, 0, 0)

        if keys[pygame.K_q]:
            transform = transform @ create_scale_matrix(1 + scale_factor, 1 + scale_factor, 1 + scale_factor)
        if keys[pygame.K_e]:
            transform = transform @ create_scale_matrix(1 - scale_factor, 1 - scale_factor, 1 - scale_factor)

        if keys[pygame.K_x] and current_time_ms - last_mirror_time_ms > mirror_delay_ms:
            transform = transform @ create_mirror_x_matrix()
            last_mirror_time_ms = current_time_ms

        if keys[pygame.K_y] and current_time_ms - last_mirror_time_ms > mirror_delay_ms:
            transform = transform @ create_mirror_y_matrix()
            last_mirror_time_ms = current_time_ms

        if keys[pygame.K_z] and current_time_ms - last_mirror_time_ms > mirror_delay_ms:
            transform = transform @ create_mirror_z_matrix()
            last_mirror_time_ms = current_time_ms

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
