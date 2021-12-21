# Учебный проект Yatube - Социальная сеть блогеров. 
Разработан в рамках обучения в Яндекс.Практикум.

В проекте реализованы следующие функции:

 - Создание сообщества для публикаций.

 - Публикация поста в ленте, (возможность выбора группы, в которой появится этот пост);

 - Добавление новых записей авторизованными пользователями;

 - Добавление фотографий;

 - Добавление и редактирование комментариев;

 - Редактирование постов только его автором;

 - Подписка/отписка на авторов;

 - Создание отдельной ленты с постами авторов на которых подписан пользователь;

 - Реализовано кэширование, работает на главной странице;

 - Работает пагинация;

Так же реализовано тестирование(Unittest) основных функций:

После регистрации пользователя создается его персональная страница (profile);

Только авторизованный пользователь может опубликовать пост (new);

После публикации поста новая запись появляется на главной странице сайта (index), на персональной странице пользователя (profile), и на отдельной странице поста (post);

Только авторизированный пользователь может комментировать посты.

## Запуск приложения. 

 - Клонируйте репозиторий себе на компьютер:
```
git clone https://github.com/arsban/yatubeproject_hw05_final.git
```

 - Перейдите в папку с проектом:
```
cd yatubeproject_hw05_final
```

 - Установите зависимости
```
pip install -r requirements.txt:
```

-  Перейдите в папку с проектом файлами проекта:
```
cd yatube
```

 - Выполните все необходимые миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

## Для доступа к панели администратора создайте администратора:
```
python manage.py createsuperuser
```

## Запустите приложение:
```
python manage.py runserver
```
