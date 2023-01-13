'''
   Игра существенно доработана, включая реализацию ИИ противника.

    1) В игре реализован алгоритм искусственного интеллекта противника (компьютера).
    ИИ бота реализован в методе ask подкласса AI класса Player, метод ask класса AI существенно доработан.
    - бот отслеживает и добивает раненный корабль противника;
    - бот не стреляет в ранее стрелянные точки;
    - бот не стреляет в точки контура вокруг уничтоженного вражеского корабля, где по правилам не могут находиться другие вражеские корабли.
    В подкласс AI добавлен метод update_enemy_ship_data, принимающий состояния обстреливаемого вражеского корабля, изменяющий внутреннее состояние переменных бота и
    влияющий на его последующие действия.
    Метод shot класса Board теперь возвращает два булевых значения о состоянии вражеского корабля hit и kill.

    2) Доски пользователя и противника теперь печатаются горизонтально вдоль одной линии, с помощью меода print_boards в классе Game.

    3) Между ходами пользователя и противника введена задержка в 2 секунды, для лучшего восприятия хода игры.

    Бот получился достаточно серьезным противником с которым интересно поиграть, приятной игры!
'''



from time import sleep
from random import randint
import copy

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    
    @property
    def dots(self):
        ship_dots = []
        # cur_x = copy.copy(self.bow.x)
        # cur_y = copy.copy(self.bow.y)

        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0
        
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = []
        self.ships = []
    
    def add_ship(self, ship):
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:
            res = res.replace("■", "O")
        return res
    
    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    hit = True
                    kill = True
                    return hit, kill
                else:
                    print("Корабль ранен!")
                    hit = True
                    kill = False
                    return hit, kill
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        hit = False
        kill = False
        return hit, kill
    
    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def __init__(self, board, enemy):
        super().__init__(board, enemy)
        # добавляем в подкласс AI множества кортежей координат всех точек поля и множество стреляных координат точек, обновляемое после каждого выстрела
        self.field_dots_coords = {(x, y) for x in range(0, 6) for y in range(0, 6)} # множество точек поля
        self.shot_dots_coords = set() # множество стреляных точек
        self.enemy_hit_count = 0 # подсчет попаданий
        self.near_dots_list = [] # ближайшие к вражескому кораблю точки для обстрела
        self.detected_enemy_ship = [] # список точек обнаруженного обстреливаемого вражеского корабля
        self.killed_enemy_ships_contour_area_coords = set()  # множество точек контуров потопленных вражеских кораблей
        self.current_shot_dot = None # точка текущего выстрела

    def ask(self):
        # функция фильтрации списка кортежей координат точек (удаляются координаты вне поля, стреляные координаты и координаты контуров уничтоженных кораблей)
        def dots_coords_filter(dots_coords):
            all_used_dots = self.shot_dots_coords.union(self.killed_enemy_ships_contour_area_coords)
            for dot_coords in dots_coords:
                if dot_coords not in self.field_dots_coords or dot_coords in all_used_dots:
                    dots_coords.remove(dot_coords)
            return dots_coords

        # если нет раненных вражеских кораблей
        if self.enemy_hit_count == 0:
            # вычисляем доступные для выстрела кортежи координаты путем разницы множеств
            all_unused_dots_coords = self.field_dots_coords.difference(self.shot_dots_coords.union(self.killed_enemy_ships_contour_area_coords))
            dot_coords = list(all_unused_dots_coords)[randint(0, len(all_unused_dots_coords)-1)]
            self.shot_dots_coords.update([dot_coords])
            self.current_shot_dot = Dot(dot_coords[0], dot_coords[1])
            print(f"Ход компьютера: {self.current_shot_dot.x+1} {self.current_shot_dot.y+1}")
            return self.current_shot_dot

        # если есть одно ранение вражеского корабля
        elif self.enemy_hit_count == 1:
            if not self.near_dots_list:
                near = [        (-1, 0),
                        (0, -1),        (0, 1),
                                 (1, 0)
                        ]
                # вычисляем возможные варианты продолжения корабля
                near_dots_coords = [(self.current_shot_dot.x + dx, self.current_shot_dot.y + dy) for dx, dy in near]
                # удаляем возможные координаты вне поля, стрелянные координаты и координаты контуров уничтоженных кораблей
                near_dots_coords = dots_coords_filter(near_dots_coords)
                self.near_dots_list = [Dot(x, y) for x, y in near_dots_coords]
                self.current_shot_dot = self.near_dots_list.pop(randint(0, len(self.near_dots_list)-1))
                print(f"Ход компьютера: {self.current_shot_dot.x + 1} {self.current_shot_dot.y + 1}")
                return self.current_shot_dot
            else:
                self.current_shot_dot = self.near_dots_list.pop(randint(0, len(self.near_dots_list)-1))
                print(f"Ход компьютера: {self.current_shot_dot.x + 1} {self.current_shot_dot.y + 1}")
                return self.current_shot_dot

        # если есть более одного ранения вражеского корабля
        elif self.enemy_hit_count not in [0, 1]:
            if not self.near_dots_list:
                x_coords = []; y_coords = []
                for dot in self.detected_enemy_ship:
                    x_coords.append(dot.x)
                    y_coords.append(dot.y)
                if len(set(x_coords)) == 1:
                    near_dots_coords = [(x_coords[0], min(y_coords) - 1), (x_coords[0], max(y_coords) + 1)]
                elif len(set(y_coords)) == 1:
                    near_dots_coords = [(min(x_coords) - 1, y_coords[0]), (max(x_coords) + 1, y_coords[0])]
                # удаляем возможные координаты вне поля, стрелянные координаты и координаты контуров уничтоженных кораблей
                near_dots_coords = dots_coords_filter(near_dots_coords)
                self.near_dots_list = [Dot(x, y) for x, y in near_dots_coords]
                self.current_shot_dot = self.near_dots_list.pop(randint(0, len(self.near_dots_list)-1))
                print(f"Ход компьютера: {self.current_shot_dot.x + 1} {self.current_shot_dot.y + 1}")
                return self.current_shot_dot ##
            else:
                self.current_shot_dot = self.near_dots_list.pop(randint(0, len(self.near_dots_list)-1))
                print(f"Ход компьютера: {self.current_shot_dot.x + 1} {self.current_shot_dot.y + 1}")
                return self.current_shot_dot


    def update_enemy_ship_data(self, enemy_hit, enemy_kill):
        '''
        Метод обновления статусов обстреливаемого вражеского корабля.
        Вход:
            выходы из метода move противника
        '''
        if enemy_hit == True and enemy_kill == False:
            self.enemy_hit_count += 1
            self.near_dots_list = []
            self.detected_enemy_ship.append(self.current_shot_dot)
        elif enemy_hit == True and enemy_kill == True:
            self.enemy_hit_count = 0
            self.near_dots_list = []
            self.detected_enemy_ship.append(self.current_shot_dot)
            near = [
                    (-1, -1), (-1, 0), (-1, 1),
                     (0, -1),  (0, 0),  (0, 1),
                     (1, -1),  (1, 0),  (1, 1)
            ]
            contour_coords_list = []
            for dot in self.detected_enemy_ship:
                for dx, dy in near:
                    contour_coords = (dot.x + dx, dot.y + dy)
                    if contour_coords in self.field_dots_coords:
                        contour_coords_list.append(contour_coords)
            self.killed_enemy_ships_contour_area_coords.update(contour_coords_list)
            self.detected_enemy_ship = []
        else:
            pass

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print("-------------------")
        print()
    
    def print_boards(self):
        print("Доска пользователя:        ", ' ' * 10, "Доска компьютера:")
        for us_board_str, ai_board_str in zip(self.us.board.__str__().split('\n'), self.ai.board.__str__().split('\n')):
            print(f'{us_board_str}            {ai_board_str}')
        print()

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                if num != 0:
                    sleep(2)
                print("-"*20)
                print("Ходит пользователь!")
                enemy_hit, _ = self.us.move()
                print("-" * 20)
                print()
            else:
                sleep(2)
                print("-"*20)
                print("Ходит компьютер!")
                enemy_hit, enemy_kill = self.ai.move()
                self.ai.update_enemy_ship_data(enemy_hit, enemy_kill)
                print("-" * 20)
                print()
            if enemy_hit:
                num -= 1
            
            if self.ai.board.count == 7:
                self.print_boards()
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                self.print_boards()
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()