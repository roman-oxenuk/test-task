### Как запустить

1. Приложение запуститься локально на 5000 порту.
Будет доступно по `http://localhost:5000`
Для этого подимаем докер-контейнеры:
`docker-compose up`

1. Для создания индексов в Mongo:
`docker-compose exec web flask create_indexes`

1. Можно сразу проверить работу приложения запустив тесты:
`docker-compose exec web python -m pytest`

1. Чтобы создать тестовых пользователей нужно выполнить:
`docker-compose exec web flask generate_users 3`
Где 3 -- это кол-во создаваемых пользователей.
Команда вернёт созданные объекты в json-е.


1. Чтобы добавить пользователю транзакции нужно выполнить команду:
`docker-compose exec web flask generate_transaction_for_user anthony.riley@yahoo.com 23`
Где
anthony.riley@yahoo.com -- email пользователя, существующего в базе. Можно его взять из вывода предыдущей команды.
23 -- кол-во созданных для выбранного пользователя транзакций

### Комментарии
* Решил попробовать swagger через connexion. Благодаря нему по адресу `/api/ui` доступна автоматическая документация по API.
* Для работы с Mongo решил использовать PyMongo, т.к. это более низкоуровневая библиотека, и мне хотелось получить более "нативный" опыт с Mongo. Для реального проекта думаю что выбрал бы MongoEngine (но не факт).

### Как проверить
Доступные урлы:
`/login` -- форма, запрашивающая email пользователя, под которым нужно залогиниться. Она перекидывает на след. форму, где нужно ввести код для входа. **Код для входа выводится в консоль приложения**.
`/api/transactions` -- список транзакций пользователя
`/api/user` -- данные пользователя
`/logout` -- урл для разлогина

### Что не сделал или сделал не в соответствие с требованиями
1. Не стал делать отправку кода для логина на емейл. Сейчас код выводиться просто в консоль.
Чтобы исключить вероятность возникновения проблем с отправкой писем с той машины, на которой будет запускаться приложение, хотел использовать стороний сервис Mailgun. Но для того, чтобы отправлять там письма на произвольный адрес, нужно подтвердить права владение доменом, с которого будут отправляться письма. В общем, не стал с этим заморачиваться.
Тут же не стал выделять отправку в отложенную асинхронную задачу. Но большой сложности в этом не вижу, т.к. опыт работы с Flask+Celery у меня был.

1. Не выполнил пункт IV.2 в части "генератор (...), использующий III.4."
Вместо того, чтобы использовать API для вставки тестовых данных, эти данные добавляются напрямую в базу, а не через API. Мне показалось, что так как-то проще и понятнее, и результат от этого не меняется. Но если это какой-то принципиальный момент, то не будет никакой сложности, чтобы переделать на добавление именно через API.

1. В пункте III.4 авторизацию для внешней системы не сделал.

### Что можно сделать лучше
1. Дизайн страничек авторизации. Хотя бы добавить bootstrap и уже вид будет лучше. Но решил, что это не первоочередная задача.
1. Возможно стоит выбрать MongoEngine для работы с Mongo, если она удобнее.
1. Сейчас запрограммированы далеко не все ошибки валидации даных, приходящих в API для создания транзакций. Нет единого справочника аэропортов и пр.
1. Расширить набор тестов.