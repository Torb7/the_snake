from random import choice, randrange

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTR = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

MOVEMENTS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Создаёт объекты игры, является супер классом для других классов."""

    def __init__(
        self,
        position: tuple[int, int] = SCREEN_CENTR,
        body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR,
    ) -> None:
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Метод определяет, как объект будет отрисовываться на
        экране, переопределяется в дочерних классах.
        """

    def draw_grid(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int] | None = None
    ) -> None:
        """Метод отрисовывает одну ячейку."""
        color = color if color else self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Создаёт и управляет объектом яблока."""

    def __init__(
        self,
        position: tuple[int, int] = SCREEN_CENTR,
        body_color: tuple[int, int, int] = APPLE_COLOR,
        filled_grids: tuple[tuple, ...] = (SCREEN_CENTR,),
    ) -> None:
        super().__init__(position, body_color)
        self.randomize_position(filled_grids)

    def randomize_position(self, filled_grids) -> None:
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            apple_X: int = randrange(0, SCREEN_WIDTH, GRID_SIZE)
            apple_Y: int = randrange(0, SCREEN_HEIGHT, GRID_SIZE)
            apple_grid: tuple[int, int] = (apple_X, apple_Y)
            if apple_grid not in filled_grids:
                break

        self.position = apple_grid

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_grid(self.position)


class Snake(GameObject):
    """Создаёт и управляет объектом змейки."""

    def __init__(
        self,
        position: tuple[int, int] = SCREEN_CENTR,
        body_color: tuple[int, int, int] = SNAKE_COLOR,
    ) -> None:
        super().__init__(position, body_color)
        self.last: tuple[int, int] | None = None
        self.reset()
        self.direction: tuple[int, int] = RIGHT

    def move(self) -> None:
        """Обновляет позицию змейки, добавляя новую голову в начало списка
        positions и удаляя последний элемент.
        """
        head_X, head_Y = self.get_head_position()
        dir_X, dir_Y = self.direction
        new_head_X: int = (head_X + dir_X * GRID_SIZE) % SCREEN_WIDTH
        new_head_Y: int = (head_Y + dir_Y * GRID_SIZE) % SCREEN_HEIGHT
        new_head: tuple[int, int] = (new_head_X, new_head_Y)

        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка головы змейки
        self.draw_grid(self.get_head_position())

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self, next_direction: tuple[int, int]) -> None:
        """Обновляет направление движения змейки после нажатия на кнопку."""
        self.direction = next_direction

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions: list[tuple] = [self.position]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки (первый элемент в списке
        positions).
        """
        return self.positions[0]

    def check_intersection(self, grid: tuple[int, int]) -> bool:
        """Проверка пересечений ячеек."""
        snake_X, snake_Y = self.get_head_position()
        grid_X, grid_Y = grid

        return (
            snake_X < grid_X + GRID_SIZE
            and snake_X + GRID_SIZE > grid_X
            and snake_Y < grid_Y + GRID_SIZE
            and snake_Y + GRID_SIZE > grid_Y
        )

    def elongation(self):
        """Увеличение змейки на одну ячейку."""
        self.positions.append(self.last)
        self.last = None


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            direction = MOVEMENTS.get(
                (game_object.direction, event.key), game_object.direction
            )
            game_object.update_direction(direction)


def main():
    """Функция с основным циклом игры."""
    pg.init()

    snake = Snake()
    apple = Apple(filled_grids=tuple(snake.positions))

    while True:
        handle_keys(snake)

        snake.move()
        # Проверка на столкновение змейки с самой собой.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        # Проверка на столкновение змейки с яблоком.
        elif snake.check_intersection(apple.position):
            snake.elongation()
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()

        clock.tick(SPEED)


if __name__ == '__main__':
    main()
