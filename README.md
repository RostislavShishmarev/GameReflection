<table bordercolor="none">
  <tr>
    <td>
      <img src="https://thumb.cloud.mail.ru/weblink/thumb/xw1/xufG/NTsCn9B5R" alt="Логотип" width="75" height="75" />
    </td>
    <td>
      <h1>Игра "Отражение"</h1>
    </td>
  </tr>
</table>

## _Проект для Яндекс Лицея по модулю pygame_

![Игровое окно](https://thumb.cloud.mail.ru/weblink/thumb/xw1/mqaw/V33Ntjdj7)

### Суть
Отражение – аркадная игра, основанная на столкновениях. По окну летает триплекс (шарик), который нужно отбивать платформой, сбивая блоки. Иногда из них выпадают сокровища, которые можно поймать. И то, и другое имеет свои эффекты.
В процессе игры открываются новые уровни, появляются новые типы блоков и накапливаются рекорды. Все правила подробно описаны в окне информации.

Окна:
- Главное — в нём мы выбираем уровень и сохранение, из него открываются настройки.
Выбор - нажатие на элемент листа, снятие выбора - нажатие на его заголовок.
Открыть настройки - нажатие на шестерёнку в правом верхнем углу. Кнопка "Играть" запускает выбранный уровень.
- Игровое — сама по себе игра, подсчёт очков и функция сохранения.
- Настройки — смена имени пользователя, регулирование музыки, стирание данных, отсюда кнопкой "i" открывается окно информации.
- Информация — три блока правил и описания эффектов в одном окне.

Переключение между окнами осуществляется стрелками, возвращающими на шаг назад.

![Информационное окно](https://thumb.cloud.mail.ru/weblink/thumb/xw1/s8Xs/G8kYmY9oj)

### Сборка
##### Вариант №1 (для пользователей):
1. Загрузить Reflection_exe.zip
2. Перенести его содержимое в свободную папку
3. Запустить Reflection.exe

Примечание: в папке Reflection_data расположены все пользовательский данные, без неё программа не будет работать.

##### Вариант №2 (для разработчиков):
1. Загрузить последний релиз и файл Game_no_code_files.zip
2. Перенести содержимое релиза в свободную папку
3. Перенести папки DataBases, Reflection_data, Images и Sounds из Game_no_code_files.zip в корень проекта (туда, где находится main.py)
4. Установить зависимости:
```sh
pip install -r requirements.txt
```
5. Запустить файл main.py

### Код

В проекте использован язык python, а имено его библиотека pygame. Код написан в стиле ООП.
Была создана новая технология работы с pygame — каждое окно является классом. В нём есть инициализатор, сохраняющий в себе большинство атрибутов, и метод run(), в котором находится сам игровой цикл.
Пример:
```python
import pygame


class Window:
    def __init__(self):
        self.FPS = 30
        self.size = (300, 300)
        self.running = True

    def run(self):
        pygame.init()
        pygame.display.set_caption('Пример')
        self.screen = pygame.display.set_mode(self.size)
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            clock.tick(self.FPS)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    window = Window()
    window.run()
```

Для окон были написаны виджеты (файл widgets.py). Они сами обрабатывают события и отрисовывают свои элементы, достаточно лишь вызвать нужный метод.
Созданные виджеты:
- Кнопка (Button);
- Строка ввода (InputBox);
- Надпись (Label);
- Картинка (Image);
- Оконник (TabWidget);
- Лист (ScrollList);
- Отображатели: 
- - Текста (TextDisplay)
- - Рекордов (ResultsTextDisplay)

### Дополнительно
Все звуковые файлы и изображения созданы авторами проекта или взяты из свободных интернет-ресурсов.
