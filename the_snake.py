from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Создаёт объекты игры, является супер классом для других классов."""

    def __init__(self,
                 position: tuple[int, int] = (SCREEN_WIDTH // 2,
                                              SCREEN_HEIGHT // 2),
                 body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR
                 ) -> None:
        self.position: tuple[int, int] = position
        self.body_color: tuple[int, int, int] = body_color

    def draw(self) -> None:
        """Метод определяет, как объект будет отрисовываться на
        экране, переопределяется в дочерних классах.
        """
        pass

    @staticmethod
    def check_intersection(first_grid: tuple[int, int],
                           *grids: tuple[int, int]) -> bool:
        """Проверка пересечений ячеек."""
        first_grid_X: int = first_grid[0]
        first_grid_Y: int = first_grid[1]

        for another_grid in grids:
            another_grid_X: int = another_grid[0]
            another_grid_Y: int = another_grid[1]

            if (first_grid_X < another_grid_X + GRID_SIZE
               and first_grid_X + GRID_SIZE > another_grid_X
               and first_grid_Y < another_grid_Y + GRID_SIZE
               and first_grid_Y + GRID_SIZE > another_grid_Y):
                return True

        return False


class Apple(GameObject):
    """Создаёт и управляет объектом яблока."""

    def __init__(self,
                 body_color: tuple[int, int, int] = APPLE_COLOR
                 ) -> None:
        super().__init__(body_color=body_color)
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайное положение яблока на игровом поле."""
        head_X: int = randint(0, SCREEN_WIDTH - GRID_SIZE)
        head_Y: int = randint(0, SCREEN_HEIGHT - GRID_SIZE)
        self.position: tuple[int, int] = (head_X, head_Y)

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Создаёт и управляет объектом змейки."""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(body_color=body_color)
        self.length: int = 1
        self.positions: list[tuple] = [self.position]
        self.last: tuple | None = None
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] | None = None

    def move(self) -> None:
        """Обновляет позицию змейки, добавляя новую голову в начало списка
        positions и удаляя последний элемент, если длина змейки не увеличилась.
        """
        head: tuple[int, int] = self.get_head_position
        head_X: int = (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        head_Y: int = (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        new_head: tuple[int, int] = (head_X, head_Y)

        self.positions.insert(0, new_head)
        self.last = self.positions[-1]

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self) -> None:
        """Обновляет направление движения змейки после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([UP, DOWN, RIGHT, LEFT])

    @property
    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки (первый элемент в списке
        positions).
        """
        return self.positions[0]


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Функция с основным циклом игры."""
    pygame.init()

    apple = Apple()
    snake = Snake()

    while True:
        handle_keys(snake)
        snake.update_direction()

        snake.move()
        # Проверка на столкновение змейки с самой собой.
        if snake.get_head_position in snake.positions[1:]:
            snake.reset()
        # Проверка на столкновение змейки с яблоком.
        if GameObject.check_intersection(snake.get_head_position,
                                         apple.position):
            snake.length += 1
            apple.randomize_position()
        # Проверка появления яблока на змейке.
        if GameObject.check_intersection(apple.position, *snake.positions):
            apple.randomize_position()
            continue

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()

        clock.tick(SPEED)


if __name__ == '__main__':
    main()
