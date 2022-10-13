import arcade
import os
from Character import Character

SPRITE_SCALING = 0.5
COIN_SCALING = 0.5

# Константы минималиных ширины, высоты и названия игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Lucky Dave"

# Минимальный отступ между Дэйвом и границей окна
VIEWPORT_MARGIN = 40

MOVEMENT_SPEED = 5
CHARACTER_SCALING = 1
TILE_SCALING = 0.5

GRAVITY = 1.2
JUMP_SPEED = 20

SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Стартовая позиция
DAVE_START_X = 64
DAVE_START_Y = 225

# Константы, отслеживающие сторону, в которую смотрит игрок
RIGHT_FACING = 0
LEFT_FACING = 1

# Названия слоев из карты тайлов
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_DANGERS = "Dangers"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_FINISH = "Finish"
LAYER_NAME_ITEMS = "Items"
LAYER_NAME_DAVE = "Dave"
LAYER_NAME_BACKGROUND = "Back"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Отслеживаем какая кнопка нажата
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        width, height = self.get_size()
        self.set_viewport(0, width, 0, height)
        arcade.set_background_color(arcade.color.AMAZON)

        self.scene = None
        self.dave = None
        self.physics_engine = None
        self.camera = None
        self.menu = None

        # Камера для отображения GUI-элементов
        self.gui_camera = None

        # Записываем счет
        self.score = 0

        self.tile_map = None

        # Вычисляем правую границу карты
        self.end_of_map = 0

        # Уровень
        self.level = 1

        # Нужно ли обнулить счет
        self.reset_score = True

        # Добавляем звуки
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        # self.victory = arcade.load_sound(":resources:sounds/victory1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")


    def setup(self):
        """Сетап игры"""

        # Инициализация Сцены
        self.scene = arcade.Scene()

        # Устанавливаем камеру с фокусом на игрока
        self.camera = arcade.Camera(self.width, self.height)

        # Устанавливаем GUI-камеру
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Название карты
        map_name = f"dave_{self.level}.tmx"

        # if f"dave_3.tmx":
        #     arcade.draw_text("YOU WON!", 300, 300, arcade.color.WHITE, 50, anchor_x="center")

        # Опции слоев для карты тайлов
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DANGERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_FINISH: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_ITEMS: {
                "use_spatial_hash": True,
            },
        }

        # Читаем из файла карты тайлов
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Инициализируем Сцену с картой тайлов
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Отслеживаем счет и продолжаем его запись, если игрок переходит на следующий уровень
        if self.reset_score:
            self.score = 0
        self.reset_score = True

        # Добавляем персонажа
        self.dave = Character()
        self.dave.center_x = DAVE_START_X
        self.dave.center_y = DAVE_START_Y
        self.scene.add_sprite(LAYER_NAME_DAVE, self.dave)

        # Рассчитываем границы карты в пикселях
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.dave,
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS],
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS]
        )


    def on_draw(self):
        """
        Рендер окна
        """

        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

        # Получаем разрешение окна
        left, screen_width, bottom, screen_height = self.get_viewport()

        # Прописываем счет
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 15, 40, arcade.csscolor.WHITE, 18,)

    def process_keychange(self):
        """ Функция вызывается при смене кнопок вверх/вниз или при спуске/подъеме на лестнице """

        # Процесс нажатия кнопок вверх/вниз
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.dave.change_y = MOVEMENT_SPEED
            elif (
                    self.physics_engine.can_jump(y_distance=10)
                    and not self.jump_needs_reset
            ):
                self.dave.change_y = JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.dave.change_y = -MOVEMENT_SPEED

        # Процесс нажатия кнопок вверх/вниз на лестнице без движения
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.dave.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.dave.change_y = 0

        # Процесс нажатия кнопок влево/вправо
        if self.right_pressed and not self.left_pressed:
            self.dave.change_x = MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.dave.change_x = -MOVEMENT_SPEED
        else:
            self.dave.change_x = 0

    def on_key_press(self, key, modifiers):
        """Функция вызывается при нажатии кнопок """

        if key == arcade.key.ESCAPE:
            # Переключение между фуллскрином и оконным режимом
            self.set_fullscreen(not self.fullscreen)

            # Получаем координаты окна
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key: int, modifiers: int):
        """Проверка зажата ли клавиша"""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        """Настройка камеры"""

        screen_center_x = self.dave.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.dave.center_y - (self.camera.viewport_height / 2)

        # Не позволяем камере пройти дальше 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        dave_centered = screen_center_x, screen_center_y

        self.camera.move_to(dave_centered)

    def on_update(self, delta_time):
        """Обновление игры и ее логика"""

        self.physics_engine.update()

        # Условие для переменной состояния игрока в прыжке
        if self.physics_engine.can_jump():
            self.dave.can_jump = False
        else:
            self.dave.can_jump = True

        # Условие для переменной состояния игрока на лестнице
        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.dave.is_on_ladder = True
            self.process_keychange()
        else:
            self.dave.is_on_ladder = False
            self.process_keychange()

        # Обновление анимации
        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, LAYER_NAME_DAVE]
        )

        # Проверка находится ли игрок на карте или выпал за ее пределы
        if self.dave.center_y < -100:
            self.dave.center_x = DAVE_START_X
            self.dave.center_y = DAVE_START_Y
            arcade.play_sound(self.game_over)

        # Проверка на попадание игрока на слой с опасностями
        if arcade.check_for_collision_with_list(
                self.dave, self.scene[LAYER_NAME_DANGERS]
        ):
            self.dave.center_x = DAVE_START_X
            self.dave.center_y = DAVE_START_Y

            arcade.play_sound(self.game_over)
            self.score = 0
            self.level = 1
            self.setup()
            return

        # Обновление подвижных платформ и врагов
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        player_collision_list = arcade.check_for_collision_with_lists(
            self.dave,
            [
                self.scene[LAYER_NAME_COINS]
            ],
        )

        # Проходимся по каждой монете, которой касается игрок и убираем ее из спрайт-листа
        for collision in player_collision_list:
            points = int(collision.properties["Points"])
            self.score += points

            # Убираем монету
            collision.remove_from_sprite_lists()
            arcade.play_sound(self.coin_sound)

        # Проверка коснулся ли игрок монеты, если коснулся, записываем в переменную cin_hit_list
        coin_hit_list = arcade.check_for_collision_with_list(
            self.dave, self.scene["Coins"]
        )

        # При попадании на монету, начисляем поинты и убираем монету из спрайт листа
        for coin in coin_hit_list:
            points = int(coin.properties["Points"])
            self.score += points

            # Убираем монету
            coin.remove_from_sprite_lists()

            # Проигрываем звук
            arcade.play_sound(self.coin_sound)
            self.score += 1

        # Если игрок доходит до конца уровня (попадает на спрайт с дверью)
        if arcade.check_for_collision_with_list(
                self.dave, self.scene[LAYER_NAME_FINISH]
        ):
            self.level += 1
            self.reset_score = False

            # Загрузка следующего уровня
            self.setup()

        self.center_camera_to_player()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
