import random
import sys


class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Options:  # класс для изменения настроек игры
    def __init__(self, bs=6, sa=[3, 2, 2, 1, 1, 1, 1]):
        self.board_size = bs  # размер полей
        self.ships_arr = sa  # набор кораблей


class OutOfBoardError(Exception):  # ошибка выхода за пределы доски
    def __init__(self, text):
        self.txt = text


class OccupiedDotError(Exception):  # ошибка, когда точка занята
    def __init__(self, text):
        self.txt = text


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # определяем методы __eq__ и __hash__ для использования объектов в множестве
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f'({self.x},{self.y})'


class Ship:
    def __init__(self, d, l, d_):
        self.dot = d  # стартовая точка коробля
        self.length = l  # длина коробля
        self.direction = d_  # 0 - горизонтальное положение, 1 - вертикальное
        self.life = l  # количество жизней равно длине корабля

    def dots(self):
        if self.direction:
            return [Dot(x, self.dot.y) for x in range(self.dot.x, self.dot.x + self.length)]
        else:
            return [Dot(self.dot.x, y) for y in range(self.dot.y, self.dot.y + self.length)]


class Board:
    def __init__(self, h, par):
        self.ships = []
        self.whole_ships = 0
        self.hide = h
        self.options = par
        self.field = [[0] * self.options.board_size for i in range(0, self.options.board_size)]

    def contour(self, c_ship):  # возвращает множество точек из контура коробля
        set_ = set()

        def add_dot(x1, y1):
            try:
                set_.add(Dot(x1, y1))
            except IndexError:
                pass

        for d in c_ship.dots():
            add_dot(d.x + 1, d.y)
            add_dot(d.x + 1, d.y + 1)
            add_dot(d.x, d.y + 1)
            add_dot(d.x - 1, d.y + 1)
            add_dot(d.x - 1, d.y)
            add_dot(d.x - 1, d.y - 1)
            add_dot(d.x, d.y - 1)
            add_dot(d.x + 1, d.y - 1)
        return set_.difference(c_ship.dots())

    def out(self, d):  # проверка на выход за границы игрового поля
        return (d.x < 0) or (d.x >= self.options.board_size) or (d.y < 0) or (d.y >= self.options.board_size)

    def add_ship(self, add_s):  # метод добавления корабля на игровое поле
        try:
            for d in add_s.dots():
                if self.out(d):
                    raise OutOfBoardError(f'Точка ({d.x + 1},{d.y + 1}) за пределами доски!')
                if self.field[d.x][d.y] != 0:
                    raise OccupiedDotError(f'Точка ({d.x + 1},{d.y + 1}) занята!')
                for ship_ in self.ships:
                    if d in self.contour(ship_):
                        raise OccupiedDotError(f'Точка ({d.x + 1},{d.y + 1}) занята!')
        except (OutOfBoardError, OccupiedDotError) as e:
            return False
        else:
            for d in add_s.dots():
                self.field[d.x][d.y] = 1
            self.ships.append(add_s)
            self.whole_ships += 1
            return True

    def shot(self, d):  # выстрел в точку
        if self.out(d):
            raise OutOfBoardError(f'Точка ({d.x + 1},{d.y + 1}) за пределами доски!')
        if self.field[d.x][d.y] >= 10:
            raise OccupiedDotError(f'В точку ({d.x + 1},{d.y + 1}) уже стреляли!')
        self.field[d.x][d.y] += 10
        if self.field[d.x][d.y] == 11:  # попадание в корабль
            for s in self.ships:
                if d in s.dots():  # находим корабль, в который попали
                    s.life -= 1  # отнимаем одну жизнь
                    if not s.life:  # если жизней не осталось
                        for d_ in s.dots():
                            self.field[d_.x][d_.y] += 10  # отдельно помечаем затопленный корабль
                        for d_ in self.contour(s):  # помечаем контур убитого корабля
                            if not self.out(d_):  # может быть выход за границы поля
                                if self.field[d_.x][d_.y] < 10:
                                    self.field[d_.x][d_.y] += 10

                        self.whole_ships -= 1
        return self.field[d.x][d.y]  # возвращаем значение выстрела


    def random_board(self):
        size_b = self.options.board_size
        count = 0
        for len_s in self.options.ships_arr:
            while True:
                x = random.randint(0, size_b - 1)
                y = random.randint(0, size_b - 1)
                d = random.randint(0, 1)
                if self.add_ship(Ship(Dot(x, y), len_s, d)):
                    break
                else:
                    count += 1
                if count > 2000:
                    return False
        return True


class Player:
    def __init__(self, b_):
        self.board = b_
        self.last_shot_dot = []  # будем хранить координаты последних попаданий в очереди
        self.last_shot_value = 0  # и его результат

    def ask(self):  # должен быть переопределен в классе потомке и возвращать объект Dot
        pass

    def move(self, other):  # ход игрока
        try:
            d_ = self.ask()
            shot_value = other.board.shot(d_)
            if shot_value > 10:  # если было попадание, продолжаем стрелять
                self.last_shot_dot.append(d_)  # запоминаем точку с последним попаданием
                self.last_shot_value = shot_value
                if shot_value > 20:
                    print(f'Точка ({d_.x + 1},{d_.y + 1}) - КОРАБЛЬ ПОТОПЛЕН!')
                    self.last_shot_dot.clear()  # если потопили корабль, очищаем очередь стрельбы
                else:
                    print(f'Точка ({d_.x + 1},{d_.y + 1}) - ПОПАДАНИЕ!')
                if other.board.whole_ships:  # если остались корабли, продолжаем
                    return True
                else:
                    return False  # если это последние победный выстрел, завершаем ход
            else:
                print(f'Точка ({d_.x + 1},{d_.y + 1}) - промах!')
                return False  # если промазали, завершаем ход
        except (OutOfBoardError, OccupiedDotError) as e:
            if type(self) is User:  # выводим сообщения об ошибках только для ходов игрока
                print(e.txt + ' Ход не засчитан, повторите.')
            return True


class User(Player):
    def ask(self):
        while True:
            try:
                entered_list = list(map(int, input("Введите координаты клетки для выстрела: ").split()))
                if entered_list[0] == entered_list[1] == 0:
                    print('Игра завершена досрочно!')
                    sys.exit(0)  # досрочный выход при вводе 0 0
                entered_list[0] -= 1  # преобразуем координаты клетки к адресу в матрице
                entered_list[1] -= 1
                return Dot(entered_list[0], entered_list[1])
            except Exception:
                print('Ошибка при вводе. Ход не засчитан, повторите.')


class AI(Player):
    def ask(self):
        if self.last_shot_value == 11:  # если последним попаданием ранили корабль
            if len(self.last_shot_dot) == 1:  # если только одно попадание
                d_ = self.last_shot_dot[0]
                t = random.randint(1, 4)  # пробуем стрелять в соседние клетки
                if t == 1:
                    return Dot(d_.x, d_.y - 1)
                elif t == 2:
                    return Dot(d_.x + 1, d_.y)
                elif t == 3:
                    return Dot(d_.x, d_.y + 1)
                elif t == 4:
                    return Dot(d_.x - 1, d_.y)
            else:  # если имеем несколько попаданий (т.е. задели многопалубный корабль)
                # находим ту координату, которая будет изменяться (т.к. корабли стоят только по линии)
                if self.last_shot_dot[0].x == self.last_shot_dot[1].x:  # x - постоянный, изменяется y
                    # можем стрелять только в двух направлениях: min(y) - 1 и max(y) + 1
                    miny = self.last_shot_dot[0].y
                    maxy = miny
                    for d_ in self.last_shot_dot:
                        if miny > d_.y: miny = d_.y
                        if maxy < d_.y: maxy = d_.y
                    t = random.randint(0, 1)
                    if t:
                        return Dot(self.last_shot_dot[0].x, miny - 1)
                    else:
                        return Dot(self.last_shot_dot[0].x, maxy + 1)
                else:  # y - постоянный, изменяется x
                    # можем стрелять только в двух направлениях: min(x) - 1 и max(x) + 1
                    minx = self.last_shot_dot[0].x
                    maxx = minx
                    for d_ in self.last_shot_dot:
                        if minx > d_.x: minx = d_.x
                        if maxx < d_.x: maxx = d_.x
                    t = random.randint(0, 1)
                    if t:
                        return Dot(minx - 1, self.last_shot_dot[0].y)
                    else:
                        return Dot(maxx + 1, self.last_shot_dot[0].y)
        else:
            x = random.randint(0, self.board.options.board_size - 1)
            y = random.randint(0, self.board.options.board_size - 1)
            return Dot(x, y)


class Game:
    symbol_dict = {
        0: bcolors.BLUE + '\u2591' + bcolors.ENDC,  # пустая клетка
        1: bcolors.GREEN + '\u2588' + bcolors.ENDC,  # корабль
        10: '\u2022',  # выстрел по пустой клетке
        11: bcolors.YELLOW + '\u2588' + bcolors.ENDC,  # раненый корабль
        21: bcolors.RED + '\u2588' + bcolors.ENDC,  # потопленный корабль
        -1: '\u2592'  # клетка на поле противника, в которую не стреляли
    }

    def __init__(self, options_):
        b1 = Board(False, options_)
        while not b1.random_board():
            b1 = Board(False, options_)
        b2 = Board(True, options_)
        while not b2.random_board():
            b2 = Board(True, options_)
        self.board_player1 = b1
        self.board_player2 = b2
        self.player1 = User(b1)
        self.player2 = AI(b2)

    def print_boards(self):
        size = self.board_player1.options.board_size

        def get_row(b):  # строка поля для вывода в зависимости от параметра hide
            if b.hide:
                return '\u2502'.join(
                    self.symbol_dict[b.field[i][j] if b.field[i][j] >= 10 else -1] for j in range(0, size))
            else:
                return '\u2502'.join(
                    self.symbol_dict[b.field[i][j]] for j in range(0, size))

        print('Ваше поле:' + ' ' * (size * 2 + 3) + 'Поле противника:')
        coord_numbers = ''.join(f'{str(s + 1):2}' for s in range(0, size))
        print('   ' + coord_numbers + ' ' * 13 + coord_numbers)

        header = '\u2554'  # верхняя часть игрового поля
        for i in range(0, size):
            header += '\u2550' + '\u2564'
        header = header[:-1] + '\u2557'

        footer = '\u255a'  # нижняя часть игрового поля
        for i in range(0, size):
            footer += '\u2550' + '\u2567'
        footer = footer[:-1] + '\u255d'

        print('  ' + header + ' ' * 12 + header)
        for i in range(0, size):
            print(f'{str(i + 1):2}' + '\u2551' + get_row(self.board_player1) +
                  '\u2551' + ' ' * 10 + f'{str(i + 1):2}' + '\u2551' +
                  get_row(self.board_player2) + '\u2551'
                  )
        print('  ' + footer + ' ' * 12 + footer)

    def greet(self):
        print('Вас приветствует игра "Морской бой"!')
        print('Вам необходимо потопить все корабли противника, до того как он потопил ваши.')
        print('Для выстрела в ячейку, укажите через пробел номер строки и номер столбца.')

    def loop(self, user_move):  # user_move = true - ходит игрок, false - противник
        if user_move:
            print('Ваш ход (для выхода введите "0 0"): ')
            while True:
                self.print_boards()
                if self.player1.move(self.player2):
                    continue
                else:
                    break
        else:
            print('Ход противника: ')
            while True:
                if self.player2.move(self.player1):
                    continue
                else:
                    break

    def start(self):
        self.greet()
        f_ = random.randint(0, 1)
        while True:
            self.loop(f_)
            f_ = not f_  # изменяем активного игрока
            if not self.board_player1.whole_ships:  # выиграл игрок 2
                self.print_boards()
                print('Компьютер победил!')
                break
            if not self.board_player2.whole_ships:  # выиграл игрок 1
                self.print_boards()
                print('Вы победили!')
                break

        if input('Для повторной игры введите "Y":').upper() == 'Y':
            return False
        else:
            return True


if __name__ == '__main__':
    options = Options()  # стандартное поле 6х6 и корабли [3, 2, 2, 1, 1, 1, 1]
    # options = Options(7, [3, 3, 3, 3]) # другой вариант настроек
    # options = Options(10, [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]) # другой вариант настроек
    while True:
        g = Game(options)   # создаем игру с выбранными настройками
        if g.start():
            break
        else:
            continue
