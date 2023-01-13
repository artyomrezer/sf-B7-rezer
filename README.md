# skillfactory-B7-rezer
Игра морской бой

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
