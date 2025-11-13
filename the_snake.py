from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
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

# Словарь кнопок управления
MOVE_BUTTONS_DICT = {
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Абстрактный класс GameObject"""

    def __init__(self,
        position=SCREEN_CENTER,
        body_color=BORDER_COLOR
    ) -> None:
        """Инициализация абстрактного класса GameObject"""
        self.body_color = body_color
        self.position = position

    def draw(self) -> None:
        """Абстрактный метод рисования"""
        pass


class Snake(GameObject):
    """Класс Snake. Основной игровой объект"""

    def __init__(
        self,
        position: list = SCREEN_CENTER,
        body_color: tuple = SNAKE_COLOR,
        length: int = 1,
        direction: tuple[int, int] = RIGHT,
        next_direction: tuple | None = None,
        last: list | None = None,
    ) -> None:
        """Метод инициализации"""
        super().__init__([position], body_color)
        self.length = length
        self.direction = direction
        self.next_direction = next_direction
        self.last = last

    def draw(self) -> None:
        """Метод для отрисовывания Змейки"""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
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

    def move(self) -> None:
        """Метод для передвижения Змейки по полю"""
        self.last = self.positions[-1] if self.positions else None

        # Обновляем направление
        self.update_direction()

        # Получаем текущую позицию головы
        head_x, head_y = self.positions[0]

        # Вычисляем новую позицию головы
        new_head = (
            (head_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self) -> None:
        """Метод, обновляющий направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> list:
        """Метод, возвращающий позицию головы"""
        return self.position[0]

    def reset(self) -> None:
        """Метод, сбрасывающий параметры змейки"""
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.position = [self.positions[0]]
        self.last = None

    def grow(self) -> None:
        """Метод, увеличивающий длину змейки"""
        self.length += 1

    def check_self_collision(self) -> bool:
        """Метод проверки 'самоукуса'"""
        return self.get_head_position() in self.positions[1:]

    @property
    def positions(self) -> list:
        """Свойство для доступа к позициям сегментов змейки"""
        return self.position


class Apple(GameObject):
    """Класс Apple. Второй игровой объект"""

    def __init__(
        self, position: list = SCREEN_CENTER, body_color: tuple = APPLE_COLOR
    ) -> None:
        """Метод инициализации"""
        super().__init__(self.randomize_position(), body_color)

    def draw(self) -> None:
        """Метод рисования яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, snake_positions=None):
        """
        Метод, определяющий случайное положение яблока.
        snake_positions - все позиции змейки.
        передается, для предотвращения появления яблока в змее
        """
        if snake_positions is None:
            snake_positions = []

        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in snake_positions:
                self.position = new_position
                return new_position


def handle_keys(game_object) -> None:
    """Функция обработчик событий"""
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    close_game()
                direction = MOVE_BUTTONS_DICT[event.key, game_object.direction]
                game_object.next_direction = (
                    direction if direction else game_object.next_direction
                )
    except KeyError:
        game_object.next_direction = game_object.next_direction


def close_game() -> None:
    """Функция выхода из игры"""
    pygame.quit()
    raise SystemExit


def main():
    """Основная программа"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.

    snake = Snake(SCREEN_CENTER, SNAKE_COLOR)
    apple = Apple(SCREEN_CENTER, APPLE_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position()

        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position()

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()
