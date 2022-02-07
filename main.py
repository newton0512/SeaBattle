import random


class Options:
    def __init__(self, bs=6, sa=[3, 2, 2, 1, 1, 1, 1]):
        self.board_size = bs
        self.ships_arr = sa


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

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __str__(self):
        return f'({self.x},{self.y})'


class Ship:
    def __init__(self, d, l, d_, l_):
        self.dot = d  # стартовая точка коробля
        self.length = l  # длина коробля
        self.direction = d_  # 0 - горизонтальное положение, 1 - вертикальное
        if l_ > l:
            l_ = l  # жизней у коробля не может быть больше его длины
        self.life = l_  # количество жизней

    def dots(self):
        set_ = set()
        if self.direction:
            return [Dot(x, self.dot.y) for x in range(self.dot.x, self.dot.x + self.length)]
        else:
            return [Dot(self.dot.x, y) for y in range(self.dot.y, self.dot.y + self.length)]


class Board:
    ships = []
    whole_ships = 0

    def __init__(self, h, par):
        self.hide = h
        self.options = par
        self.field = [[0] * self.options.board_size for i in range(0, self.options.board_size)]

    def add_ship(self, add_s):
        try:
            for d in add_s.dots():
                if self.field[d.x][d.y] != 0:
                    raise OccupiedDotError(f'Точка ({d.x},{d.y}) занята!')
                if (d.x < 0) or (d.x >= self.options.board_size) or (d.y < 0) or (d.y >= self.options.board_size):
                    raise OutOfBoardError(f'Точка ({d.x},{d.y}) за пределами доски!')
        except OutOfBoardError:
            return False
        else:
            for d in add_s.dots():
                self.field[d.x][d.y] = 1
            self.whole_ships += 1
            return True

    def print_(self):
        for k in range(0, 6):
            print(self.field[k])


if __name__ == '__main__':
    s = Ship(Dot(5, 5), 3, 0, 7)

    b = Board(False)
    b.print_()
    b.add_ship(s)
    b.print_()
