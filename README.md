# Double Subtitles

<p align="center">
  <img height=150 src="https://github.com/alexeykorevin/DoubleSubtitles/blob/master/DoubleSubtitles.ico">
</p>

Программа для создания двойных субтитров. Пригодится тем, кто изучает иностранный язык или смотрит сериалы/фильмы в оригинале. Объединение происходит по временному интервалу. Алгоритм основан на агломеративной иерархической кластеризации.

Интерфейс:
<p align="center">
  <img height=480 src="https://github.com/alexeykorevin/DoubleSubtitles/blob/master/Interface.png">
</p>

Основные настройки:
- Space between subs - добавление пробела между субтитрами для лучшего зрительного разделения при просмотре
- Remove uppercase subs - удаление субтитров с верхним регистром
- Remove SDH subs - удаление SDH субтитров (Субтитры для глухих и слабослышащих, передающие в текстовом виде, кроме диалогов, еще и звуковые эффекты.)
- Automatic clustering - автоматическая кластеризация, подбирающая оптимальное количество кластеров для последующего объединения субтитров.

Доступна функция Drag & Drop, а так же пакетное объединение субтитров (сразу несколько серий/фильмов).


Пример объединения двойных субтитров (Silicon Valley S01E01):

| Английские субтитры | Русские субтитры | Двойные субтитры |
|--|--|--|
|<table><tr><th>1<br>00:00:23,440 --> 00:00:24,440</th></tr><tr><td>Whoo!</td></tr></table><table><tr><th>2<br>00:00:24,525 --> 00:00:25,525</th></tr><tr><td>Yeah!</td></tr></table><table><tr><th>3<br>00:00:25,609 --> 00:00:28,861</th></tr><tr><td>Somebody make some motherfucking noise in here!</td></tr></table>|<table><tr><th>1<br>00:00:24,601 --> 00:00:28,897</th></tr><tr><td>Эй, чего вы все как неживые?</td></tr></table>|<table><tr><th>1<br>00:00:23,440 --> 00:00:28,861</th></tr><tr><td>Whoo! Yeah! Somebody make some motherfucking noise in here!<br><br>Эй, чего вы все как неживые?</td></tr></table>|
|<table><tr><th>4<br>00:00:31,949 --> 00:00:33,616</th></tr><tr><td>Fuck these people.</td></tr></table>|<table><tr><th>2<br>00:00:31,900 --> 00:00:33,151</th></tr><tr><td>Вот уроды.</td></tr></table>|<table><tr><th>2<br>00:00:31,949 --> 00:00:33,616</th></tr><tr><td>Fuck these people.<br><br>Вот уроды.</td></tr></table>|
|<table><tr><th>5<br>00:00:37,705 --> 00:00:39,997</th></tr><tr><td>Man, this place is unbelievable.</td></tr></table>|<table><tr><th>3<br>00:00:38,198 --> 00:00:39,908</th></tr><tr><td>Чумовое местечко.</td></tr></table>|<table><tr><th>3<br>00:00:37,705 --> 00:00:39,997</th></tr><tr><td>Man, this place is unbelievable.<br><br>Чумовое местечко.</td></tr></table>|
|<table><tr><th>6<br>00:00:40,499 --> 00:00:41,958</th></tr><tr><td>Fucking Goolybib, man.</td></tr></table><table><tr><th>7<br>00:00:42,042 --> 00:00:43,843</th></tr><tr><td>Those guys build a mediocre piece of software,</td></tr></table>|<table><tr><th>4<br>00:00:40,617 --> 00:00:44,120</th></tr><tr><td>Чертов Гулибиб. Состряпали средненький софт,</td></tr></table>|<table><tr><th>4<br>00:00:40,499 --> 00:00:43,843</th></tr><tr><td>Fucking Goolybib, man. Those guys build a mediocre piece of software,<br><br>Чертов Гулибиб. Состряпали средненький софт,</td></tr></table>|
|<table><tr><th>8<br>00:00:43,919 --> 00:00:47,004</th></tr><tr><td>that might be worth something someday, and now they live here.</td></tr></table>|<table><tr><th>5<br>00:00:44,120 --> 00:00:47,207</th></tr><tr><td>который когда-нибудь может выстрелит, и вот живут здесь.</td></tr></table>|<table><tr><th>5<br>00:00:43,919 --> 00:00:47,004</th></tr><tr><td>that might be worth something someday, and now they live here.<br><br>который когда-нибудь может выстрелит, и вот живут здесь.</td></tr></table>|

Дальнейшие планы:
- [ ] Улучшение качества субтитров с помощью разделения объединенных субтитров по предложениям
- [ ] Перевод субтитров, не вошедших в объединение, на основе Yandex Translate API
- [ ] Создание веб-сервиса для онлайн доступа
