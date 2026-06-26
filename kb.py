from aiogram.types import InlineKeyboardButton


menu = [
    InlineKeyboardButton(text="Групповое общение", callback_data="join_group"),
    InlineKeyboardButton(text="🌀 Анонимный чат (1 на 1)", callback_data="anonymous_chat"),
    InlineKeyboardButton(text="➕ Добавить", callback_data="add_group"),
    InlineKeyboardButton(text="🔽 Другое", callback_data="other"),
    InlineKeyboardButton(text="Админ панель", callback_data="panel")
]

group_type_menu = [
    [InlineKeyboardButton(text="В случайную группу", callback_data="random_group")],
    [InlineKeyboardButton(text="В публичную группу", callback_data="public_group")],
    [InlineKeyboardButton(text="В приватную группу", callback_data="private_group")]
]

groups = [
    [InlineKeyboardButton(text="🖼️ Художников или Фотографов", callback_data="artist_works")],
    [InlineKeyboardButton(text="🎵 Музыкантов", callback_data="musicians")],
    [InlineKeyboardButton(text="🔍 Поиск по названию", callback_data="NameSearch")]
]

group_type_menu2 = [
    [InlineKeyboardButton(text="Публичную группу", callback_data="t:0")],
    [InlineKeyboardButton(text="Приватную группу", callback_data="t:1")]
]

search_menu = [
    [InlineKeyboardButton(text="🔍 Поиск по названию", callback_data="name_search")],
    [InlineKeyboardButton(text="🔍 Поиск по категориям", callback_data="category_search")]
]

other_menu = [
    [InlineKeyboardButton(text="💲 Пополнить баланс", callback_data="replenish")],
    [InlineKeyboardButton(text="💎 Подписка", callback_data="subscribe")],
    [InlineKeyboardButton(text="💡 Предложить идею для обновления", callback_data="update")],
    [InlineKeyboardButton(text="➕ Пригласить друга", callback_data="friend")]
]

panel = [
    [InlineKeyboardButton(text="Добавить суперпольз.", callback_data="add_a_superuser")],
    [InlineKeyboardButton(text="Удалить суперпольз.", callback_data="remove_superuser")],
    [InlineKeyboardButton(text="Отправить сообщение", callback_data="send_message")],
    [InlineKeyboardButton(text="Статистика", callback_data="statistics")],
    [InlineKeyboardButton(text="Включить уведомления", callback_data="enable")],
    [InlineKeyboardButton(text="Выключить уведомления", callback_data="turn_off")],
    [InlineKeyboardButton(text="Узнать идеи", callback_data="ideas")],
    [InlineKeyboardButton(text="Оправить монеты", callback_data="send_coins")],
    [InlineKeyboardButton(text="Забанить", callback_data="ban")],
    [InlineKeyboardButton(text="Разбанить", callback_data="unban")],
    [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
]

statistics_menu = [
    [InlineKeyboardButton(text="За этот день", callback_data="day")],
    [InlineKeyboardButton(text="За этот месяц", callback_data="month")]
]

sms_sending_buttons = [
    [InlineKeyboardButton(text="Всем", callback_data="everyone")],
    [InlineKeyboardButton(text="Одному человеку", callback_data="one_person")]
]

info_button = [
    [InlineKeyboardButton(text="Что даёт эта привилегия?", callback_data="INFO")]
]

button = [
    [InlineKeyboardButton(text="💲 Пополнить баланс", callback_data="replenish")]
]

button2 = [
    [InlineKeyboardButton(text="Выключить уведомления", callback_data="turn_off")]
]

button4 = [
    [InlineKeyboardButton(text="💎 Подписка", callback_data="subscribe")]
]

time_selection_menu = [
    [InlineKeyboardButton(text="1 месяц (50 XCoin)", callback_data="d:30")],
    [InlineKeyboardButton(text="3 месяца (120 XCoin)", callback_data="d:90")],
    [InlineKeyboardButton(text="12 месяцев (450 XCoin)", callback_data="d:365")]
]

confirmation_button = [
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data="Yes")]
]

confirmation_button2 = [
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data="Yes2")]
]

menu2 = [
    [InlineKeyboardButton(text="Случайная группа", callback_data="random_group")],
    [InlineKeyboardButton(text="Анонимный чат", callback_data="anonymous_chat")]
]

categories = [
    "Политика", "Экономика", "Бизнес", "Карьера", "Путешествия", "Лингвистика",
    "Психология", "Реклама", "Книги", "Образование",
    "Трейдинг", "Право", "Технологии", "Медицина",
    "Здоровье", "Спорт", "Мода", "Кулинария",
    "Искусство", "Дизайн", "Рукоделие", "Курсы и гайды",
    "Юмор и развлечения", "Познавательное", "Музыка", "Фильмы",
    "Недвижимость", "Скидки", "Строительство и ремонт", "Инвестирование",
    "Другое"
]

gender_selection_menu = [
    [InlineKeyboardButton(text="♂ Мужской", callback_data="gender:0"),
     InlineKeyboardButton(text="♀ Женский", callback_data="gender:1")]
]

gender_selection_menu2 = [
    [InlineKeyboardButton(text="♂ Мужской", callback_data="Gender:0"),
     InlineKeyboardButton(text="♀ Женский", callback_data="Gender:1")]
]

country_selection_menu = [
    [InlineKeyboardButton(text="Россия", callback_data="code:RU"),
     InlineKeyboardButton(text="Украина", callback_data="code:UA")],
    [InlineKeyboardButton(text="Беларусь", callback_data="code:BY"),
     InlineKeyboardButton(text="Казахстан", callback_data="code:KZ")],
    [InlineKeyboardButton(text="Армения", callback_data="code:AM"),
     InlineKeyboardButton(text="Азербайджан", callback_data="code:AZ")],
    [InlineKeyboardButton(text="Узбекистан", callback_data="code:UZ"),
     InlineKeyboardButton(text="Таджикистан", callback_data="code:TJ")],
    [InlineKeyboardButton(text="Туркменистан", callback_data="code:TM"),
     InlineKeyboardButton(text="Молдова", callback_data="code:MD")],
    [InlineKeyboardButton(text="Киргизия", callback_data="code:KG"),
     InlineKeyboardButton(text="Китай", callback_data="code:CN")],
    [InlineKeyboardButton(text="Страны ЕС", callback_data="code:EU"),
     InlineKeyboardButton(text="США", callback_data="code:US")],
    [InlineKeyboardButton(text="Другая", callback_data="code:other")]
]

country_selection_menu2 = [
    [InlineKeyboardButton(text="Россия", callback_data="Code:RU"),
     InlineKeyboardButton(text="Украина", callback_data="Code:UA")],
    [InlineKeyboardButton(text="Беларусь", callback_data="Code:BY"),
     InlineKeyboardButton(text="Казахстан", callback_data="Code:KZ")],
    [InlineKeyboardButton(text="Армения", callback_data="Code:AM"),
     InlineKeyboardButton(text="Азербайджан", callback_data="Code:AZ")],
    [InlineKeyboardButton(text="Узбекистан", callback_data="Code:UZ"),
     InlineKeyboardButton(text="Таджикистан", callback_data="Code:TJ")],
    [InlineKeyboardButton(text="Туркменистан", callback_data="Code:TM"),
     InlineKeyboardButton(text="Молдова", callback_data="Code:MD")],
    [InlineKeyboardButton(text="Киргизия", callback_data="Code:KG"),
     InlineKeyboardButton(text="Китай", callback_data="Code:CN")],
    [InlineKeyboardButton(text="Страны ЕС", callback_data="Code:EU"),
     InlineKeyboardButton(text="США", callback_data="Code:US")],
    [InlineKeyboardButton(text="Другая", callback_data="Code:other")]
]

hobby_selection_menu = [
    [InlineKeyboardButton(text="Йога", callback_data="hobby:1"),
     InlineKeyboardButton(text="Автомобили", callback_data="hobby:2")],
    [InlineKeyboardButton(text="Книги", callback_data="hobby:3"),
     InlineKeyboardButton(text="Путешествия", callback_data="hobby:4")],
    [InlineKeyboardButton(text="Программирование", callback_data="hobby:5")],
    [InlineKeyboardButton(text="Коллекционирование", callback_data="hobby:6")],
    [InlineKeyboardButton(text="Куллинария", callback_data="hobby:7"),
     InlineKeyboardButton(text="Рукоделие", callback_data="hobby:8")],
    [InlineKeyboardButton(text="Соц. Сети", callback_data="hobby:9"),
     InlineKeyboardButton(text="Рисование", callback_data="hobby:10")],
    [InlineKeyboardButton(text="Аниме", callback_data="hobby:11"),
     InlineKeyboardButton(text="Музыка", callback_data="hobby:12")],
    [InlineKeyboardButton(text="Спорт", callback_data="hobby:13"),
     InlineKeyboardButton(text="Дизайн", callback_data="hobby:14")],
    [InlineKeyboardButton(text="Фотоискусство", callback_data="hobby:15"),
     InlineKeyboardButton(text="Астрономия", callback_data="hobby:16")],
    [InlineKeyboardButton(text="3D-моделирование", callback_data="hobby:17")],
    [InlineKeyboardButton(text="Другое", callback_data="hobby:0")]
]

hobby_selection_menu2 = [
    [InlineKeyboardButton(text="Йога", callback_data="Hobby:1"),
     InlineKeyboardButton(text="Автомобили", callback_data="Hobby:2")],
    [InlineKeyboardButton(text="Книги", callback_data="Hobby:3"),
     InlineKeyboardButton(text="Путешествия", callback_data="Hobby:4")],
    [InlineKeyboardButton(text="Программирование", callback_data="Hobby:5")],
    [InlineKeyboardButton(text="Коллекционирование", callback_data="Hobby:6")],
    [InlineKeyboardButton(text="Куллинария", callback_data="Hobby:7"),
     InlineKeyboardButton(text="Рукоделие", callback_data="Hobby:8")],
    [InlineKeyboardButton(text="Соц. Сети", callback_data="Hobby:9"),
     InlineKeyboardButton(text="Рисование", callback_data="Hobby:10")],
    [InlineKeyboardButton(text="Аниме", callback_data="Hobby:11"),
     InlineKeyboardButton(text="Музыка", callback_data="Hobby:12")],
    [InlineKeyboardButton(text="Спорт", callback_data="Hobby:13"),
     InlineKeyboardButton(text="Дизайн", callback_data="Hobby:14")],
    [InlineKeyboardButton(text="Фотоискусство", callback_data="Hobby:15"),
     InlineKeyboardButton(text="Астрономия", callback_data="Hobby:16")],
    [InlineKeyboardButton(text="3D-моделирование", callback_data="Hobby:17")],
    [InlineKeyboardButton(text="Другое", callback_data="Hobby:0"),
     InlineKeyboardButton(text="Любое", callback_data="Hobby:-1")]
]

hobbies = [
    "Другое",
    "Йога", "Автомобили",
    "Книги", "Путешествия",
    "Программирование", "Коллекционирование",
    "Куллинария", "Рукоделие",
    "Соц. Сети", "Рисование",
    "Аниме", "Музыка", "Спорт",
    "Дизайн", "Фотоискусство",
    "Астрономия", "3D-моделирование",
    "Любое"
]

gender = [
    "♂ Мужской", "♀ Женский"
]
