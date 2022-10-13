import arcade

CHARACTER_SCALING = 1
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """
    Загружаем пару изображений, второе будет переворачиваться
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Character(arcade.Sprite):
    """Спрайт персонажа"""

    def __init__(self):

        super().__init__()

        # Дефолтное состояние
        self.character_face_direction = RIGHT_FACING

        # Переменные для анимации - переменной смене изображений
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Трекаем состояние
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # Загружаем текстуры
        main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"

        # Текстуры для различных действий
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Загружаем текстуры ходьбы
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Загружаем текстуры подъема по лестнице
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Устанавливаем текстуры для состояния idle
        self.texture = self.idle_texture_pair[0]

        # Хитбоксы равны размеру спрайтов
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Рассчитываем какой стороной повернуть спрайт
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Добавляем анимацию спуска и подъема по лестнице
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Добавляем анимацию прыжков
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Анимация состояния idle
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Анимация ходьбы
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]