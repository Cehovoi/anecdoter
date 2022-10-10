# Приложение состоит из трёх частей:
### 1. телеграмм бот который рассказывает анекдоты по предложенному слову или словосочетанию. После того как пользователь получил анекдот ему предлагается его оценить. @anecdot_searcher_bot

### 2. сайт на котором находятся оцененные пользователем анекдоты. Это Flask приложение с очень простым интерфейсом (только анекдоты, навигация по страницам с рейтингом и кнопка для админки). Есть пять страничек, соответствующих рейтингу 1-5, на каждой по 9 анекдотов. Можно зайти и посмотреть введя ссылку в браузере, но этот способ не позволит попасть в админку т.к не содержит chat id из телеграмм. Чтобы он появился нужно оценить анекдот в телеграмме и перейти по предложенной ссылке. Ссылка для примера (рабочая, но без возможности регистрации) первое число это рэйтинг анекдотов, второе chat id пользователя из телеграмма. https://anecdoter.su/rating/5/1

### 3. стандартная Flask админка поддерживающаю CRUD операции для пользователя с правами админа. Может зайти любой пользователь достаточно придумать и ввести логин и пароль. Не админу доступен только просмотр содержимого моделей базы данных. Чтобы попасть нажать на звёздочки на любой странице.

# Основные технологии:

### Python

### Docker

### PostgrSQL

### Flask

### SQLAlchemy

### pyTelegramBotAPI

### pytransitions - стейт машина для общения с пользователями телеграмма

### BeautifulSoup - для парсинга анекдотов с www.anekdot.ru

Бот упакован в докер. Реализовано кеширование данных, текст анекдота выдаваемый телеграммом хранится в кеше, в базе хранятся только индексы - порядковый номер анекдота на странице и номер страницы с www.anekdot.ru. Сайт (веб приложение) работает с моделью в которой всегда 45 анекдотов - это анекдоты оценённые пользователем, каждая новая оценка вытесняет один анекдот с соответствующим рейтингом.
