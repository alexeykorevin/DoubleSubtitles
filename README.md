# Double Subtitles

<p align="center">
  <img height=150 src="https://github.com/alexeykorevin/DoubleSubtitles/blob/master/DoubleSubtitles.ico">
</p>

Программа для создания двойных субтитров на основе агломеративной иерархической кластеризации.
Объединение происходит не по номеру субтитров, а по временному интервалу.

Пример (Silicon Valley S01E01):

<table>
<tr><th>Английские субтитры</th><th>Русские субтитры</th><th>Двойные субтитры</th></tr>
<tr><td>

|1<br>00:00:23,440 --> 00:00:24,440|
|-|
|Whoo!|

|2<br>00:00:24,525 --> 00:00:25,525|
|-|
|Yeah!|

|3<br>00:00:25,609 --> 00:00:28,861|
|-|
|Somebody make some motherfucking noise in here!|

|4<br>00:00:31,949 --> 00:00:33,616|
|-|
|Fuck these people.|

|5<br>00:00:37,705 --> 00:00:39,997|
|-|
|Man, this place is unbelievable.|

|6<br>00:00:40,499 --> 00:00:41,958|
|-|
|Fucking Goolybib, man.|

|7<br>00:00:42,042 --> 00:00:43,843|
|-|
|Those guys build a mediocre piece of software,|

|8<br>00:00:43,919 --> 00:00:47,004|
|-|
|that might be worth something someday, and now they live here.|

</td><td>

|1<br>00:00:24,601 --> 00:00:28,897|
|-|
|- Эй, чего вы все как неживые?|

|2<br>00:00:31,900 --> 00:00:33,151|
|-|
|Вот уроды.|

|3<br>00:00:38,198 --> 00:00:39,908|
|-|
|- Чумовое местечко.|

|4<br>00:00:40,617 --> 00:00:44,120|
|-|
|- Чертов Гулибиб. Состряпали средненький софт,|

|5<br>00:00:44,120 --> 00:00:47,207|
|-|
|который когда-нибудь может выстрелит, и вот живут здесь.|

<br><br><br><br><br><br><br><br><br><br><br><br>
</td><td>

|1<br>00:00:23,440 --> 00:00:28,861|
|-|
|Whoo! Yeah! Somebody make some motherfucking noise in here!<br><br>Эй, чего вы все как неживые?|

|2<br>00:00:31,949 --> 00:00:33,616|
|-|
|Fuck these people.<br><br>Вот уроды.|

|3<br>00:00:37,705 --> 00:00:39,997|
|-|
|Man, this place is unbelievable.<br><br>Чумовое местечко.|

|4<br>00:00:40,499 --> 00:00:43,843|
|-|
|Fucking Goolybib, man. Those guys build a mediocre piece of software,<br><br>Чертов Гулибиб. Состряпали средненький софт,|

|5<br>00:00:43,919 --> 00:00:47,004|
|-|
|that might be worth something someday, and now they live here.<br><br>который когда-нибудь может выстрелит, и вот живут здесь.|

<br><br><br><br><br>
</td></tr> </table>

Дальнейшие планы:
- [ ] Разделение объединенных субтитров по предложениям
- [ ] Перевод субтитров, не вошедшие в объединение, на основе Yandex Translate API
- [ ] Создание веб-сервиса для онлайн доступа
