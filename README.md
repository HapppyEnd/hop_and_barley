# Hop & Barley - Online Brewing Store

Полнофункциональный интернет-магазин, построенный на Django и Django REST Framework.

## 🛠 Технологический стек

- **Backend**: Django 5.2.5, Django REST Framework 3.16.1
- **База данных**: PostgreSQL 15
- **Аутентификация**: JWT (SimpleJWT), Session Auth
- **Документация**: drf-spectacular
- **Контейнеризация**: Docker, Docker Compose
- **Тестирование**: pytest, pytest-django

## 📦 Установка и запуск

### Предварительные требования

- **Docker** 20.10+
- **Docker Compose** 2.0+

### Быстрый старт

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/HapppyEnd/hop_and_barley
cd hop_and_barley
```

2. **Создайте файл окружения `.env` в корне проекта:**
```env
# Django settings
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DATABASE_URL=postgresql://postgres:postgres@db:5432/hop_and_barley
POSTGRES_DB=hop_and_barley
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Docker
DOCKER_CONTAINER=true

```

3. **Запустите проект:**
```bash
docker-compose up --build
```

**Примечание:** При первом запуске Docker автоматически выполнит:
- **Ожидание готовности базы данных** (PostgreSQL)
- **Создание и применение миграций** базы данных
- **Создание суперпользователя** (логин: admin@hopandbarley.com, пароль: admin123)
- **Загрузку тестовых данных** о продуктах из `products_data.json`
- **Сбор статических файлов** для Nginx
- **Копирование демо-изображений** товаров

Все эти процессы выполняются в `docker-entrypoint.sh` и не требуют ручного вмешательства.

**Управление Docker контейнерами:**
```bash
# Остановка контейнеров
docker-compose down

# Перезапуск с пересборкой
docker-compose up --build

```

4. **Откройте в браузере:**
- **Веб-интерфейс**: http://localhost
- **Админ-панель**: http://localhost/admin (логин: admin@hopandbarley.com, пароль: admin123)
- **API документация**: http://localhost/api/docs/

### 🔧 Переменные окружения

**Важно:**
- `DOCKER_CONTAINER=true` - использует PostgreSQL в Docker (рекомендуется)
- `DOCKER_CONTAINER=false` - использует SQLite для локальной разработки
- Секретный ключ уже настроен для разработки
- Email настройки уже настроены в `settings.py`
- В dev режиме email сохраняются в папку `sent_emails/` как файлы

### 🐳 Docker Services

Проект использует 3 контейнера:

- **`web`** - Django приложение (Python 3.12) с автоматической настройкой
- **`db`** - PostgreSQL 15 база данных
- **`nginx`** - Веб-сервер для статических файлов и проксирование запросов


## 🏗 Архитектура проекта

```
hop_and_barley/
├── config/                 # Настройки Django
├── products/               # Каталог товаров и отзывы
├── orders/                 # Заказы и корзина (session-based)
├── users/                  # Пользователи с email-аутентификацией
├── api/                    # REST API с JWT авторизацией
├── tests/                  # Тесты
├── static/                 # Статические файлы
├── media/                  # Медиа файлы
├── templates/              # HTML шаблоны
├── sent_emails/            # Сохранение email уведомлений (dev)
├── docker-compose.yml      # Docker конфигурация
├── docker-entrypoint.sh    # Скрипт инициализации контейнера
├── nginx.conf              # Конфигурация Nginx
└── requirements.txt        # Python зависимости
```

## 🔧 Основные функции

### Каталог товаров
- Список товаров с пагинацией
- Фильтрация по категориям и цене
- Поиск по названию и описанию
- Сортировка по цене, дате, популярности

### Система заказов
- Корзина на основе сессий
- Оформление заказа с валидацией
- Email уведомления (сохраняются в папке `sent_emails/` в dev режиме)
- Отслеживание статуса заказа

### Пользовательские аккаунты
- Регистрация и авторизация по email
- Личный кабинет с профилем
- История заказов
- Управление профилем (телефон, адрес, фото)

### Админ-панель
- Управление товарами и заказами
- Управление пользователями
- Статистика по категориям

## 🔌 API Endpoints

### Аутентификация
- `POST /api/auth/token/` - Получение JWT токенов
- `POST /api/auth/token/refresh/` - Обновление токена
- `POST /api/users/register/` - Регистрация пользователя

### Товары
- `GET /api/products/` - Список товаров
- `GET /api/products/{id}/` - Детали товара
- `POST /api/products/` - Создание товара (admin)

### Заказы
- `GET /api/orders/` - Список заказов пользователя
- `POST /api/orders/` - Создание заказа
- `POST /api/orders/{id}/cancel/` - Отмена заказа

### Корзина
- `GET /api/cart/` - Содержимое корзины
- `POST /api/cart/` - Добавление товара в корзину
- `PUT /api/cart/{id}/` - Обновление количества товара
- `DELETE /api/cart/{id}/` - Удаление товара из корзины

### Отзывы
- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создание отзыва
- `PUT /api/reviews/{id}/` - Обновление отзыва

## 🧪 Тестирование

### Запуск тестов (локально)
```bash
# Все тесты
py -m pytest

# С покрытием
py -m pytest --cov=.

# Конкретный модуль
py -m pytest tests/products/

# Конкретный тест
py -m pytest tests/products/test_models.py::TestProductModel::test_product_creation
```

### 🚀 Локальная разработка

Для работы с проектом локально (без Docker):

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
# Создайте .env файл с DOCKER_CONTAINER=false

# Применение миграций
py manage.py migrate

# Создание суперпользователя
py manage.py createsuperuser

# Загрузка тестовых данных
py manage.py load_products

# Запуск сервера разработки
py manage.py runserver
```

## 📊 Модели данных

### Product
- Название, описание, цена
- Категория, изображение
- Остаток на складе
- Статус активности

### Order
- Пользователь, статус
- Адрес доставки
- Общая стоимость
- Временные метки

### Review
- Товар, пользователь
- Рейтинг (1-5), комментарий
- Валидация покупки

## 🔐 Безопасность

- JWT токены с ротацией
- CSRF защита
- Валидация данных
- Проверка прав доступа
- Безопасные пароли

## 📈 Производительность

- Оптимизированные запросы с `select_related`
- Пагинация результатов
- Кэширование сессий
- Статические файлы через Nginx

## 🚀 Развертывание

### Production настройки
1. Установите `DEBUG=False`
2. Настройте `ALLOWED_HOSTS`
3. Используйте production базу данных
4. Настройте SMTP для email
5. Включите HTTPS


## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📝 Лицензия

Этот проект создан в учебных целях.

## 📞 Поддержка

При возникновении вопросов создайте issue в репозитории.

---

**Hop & Barley** - Ваш надежный партнер в мире домашнего пивоварения! 🍺