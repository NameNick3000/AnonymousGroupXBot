import kb
import os
import sys
import time
import config
import sqlite3
import datetime
from aiogram import Router, F
from payment import pay, check_buy
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
)
from Bot import (
    bot, execute, Register, coin_check, statistics, messages, messages2, number_of_complaints,
    date_check, delete_group, match_check, send, send2, send3, logger, number_of_messages,
    directory, directory2
)


sys.setrecursionlimit(2000)
router = Router()


@router.message(CommandStart())
async def start(msg: Message):
    res = coin_check(msg.chat.id, qty=1, money=False)
    if res == 2:
        first_name = msg.from_user.first_name
        last_name = msg.from_user.last_name
        username = msg.from_user.username
        user_id = msg.from_user.id
        chat_id = msg.chat.id
        date = str(datetime.datetime.now())
        execute(
            "INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
            VALUES=(first_name, last_name, username, user_id, chat_id, date, 0,)
        )
        for k, v in config.admins.items():
            if v in config.Notify:
                markup = InlineKeyboardMarkup(inline_keyboard=kb.button2)
                await bot.send_message(
                    v, f"У вас новый пользователь! Данные этого пользователя:\n"
                       f"ID: {user_id}, first name: {first_name}, username: @{username}",
                    reply_markup=markup, parse_mode=None
                )
        res = execute("SELECT user_id FROM friends2 WHERE username = ?", VALUES=(username,), one=True)
        res2 = execute("SELECT user_id FROM friends WHERE friend_id = ?", VALUES=(chat_id,), one=True)
        if res is not None or res2 is not None:
            try:
                ID = res[0]
                coins = float(
                    execute("SELECT coin FROM users WHERE user_id = %d" % (ID,), one=True)[0]
                ) + 30
                execute("UPDATE users SET coin = ? WHERE user_id = ?", (coins, ID,))
            except Exception:
                ID = res2[0]
                coins = float(
                    execute("SELECT coin FROM users WHERE user_id = %d" % (ID,), one=True)[0]
                ) + 30
                execute("UPDATE users SET coin = ? WHERE user_id = ?", (coins, ID,))
            execute("DELETE FROM friends WHERE friend_id=%d;" % (chat_id,))
            execute("DELETE FROM friends2 WHERE username = ?", VALUES=(username,))
            await bot.send_message(ID, "Вы успешно пригласили своего друга!")
        builder = InlineKeyboardBuilder()
        for i in range(len(kb.menu) - 1):
            builder.row(kb.menu[i])
        if msg.from_user.id in config.admins:
            builder.row(kb.menu[-1])
        await msg.answer(
            "Выберите действие в меню.\n\n"
            "В чате запрещены:\n"
            "1. Оскорбления в любом виде.\n"
            "2. Реклама.\n"
            "3. Просьбы поставить лайк, проголосовать или подписаться.\n"
            "4. Продажи любых товаров или услуг.\n"
            "5. Оружие, наркотики, психотропные вещества.\n"
            "6. Экстремистский контент и призывы к массовым беспорядкам.\n"
            "7. Сообщения, призывающие к суициду и иным действиям, "
            "способным нанести вред человеку или его имуществу.\n"
            "8. Распространение прочей информации, запрещенной законодательством.\n"
            "9. Порнография в любом виде.\n"
            "<b>Нарушение любых из этих правил ведёт к бану навсегда! "
            "Нажимая на любую из кнопок, вы соглашаетсь с тем, что не будете их нарушать!</b>",
            reply_markup=builder.as_markup()
        )
    else:
        builder = InlineKeyboardBuilder()
        for i in range(len(kb.menu) - 1):
            builder.row(kb.menu[i])
        if msg.from_user.id in config.admins:
            builder.row(kb.menu[-1])
        await msg.answer("Выберите действие в меню.", reply_markup=builder.as_markup())


@router.message(Command("balance"))
async def balance(msg: Message):
    conn = sqlite3.connect(config.database)
    cur = conn.cursor()
    ID = msg.from_user.id
    XCoin = cur.execute("SELECT coin FROM users WHERE user_id = ?", (ID,)).fetchone()
    cur.close()
    conn.close()
    if XCoin is not None:
        XCoin = XCoin[0]
        res = date_check(ID)
        if res is not None:
            await msg.answer(
                f"Ваш баланс XCoin: {XCoin}.\n"
                f"Срок вашей подписки - {res if res > 0 else 0} дней."
            )
        else:
            await msg.answer(f"Ваш баланс XCoin: {XCoin}")
    else:
        await msg.answer("Вы не зарегистрированы!")


@router.message(Command("updates"))
async def updates(msg: Message):
    await msg.answer("Обновление 1.12.2: добавлены иконки у некоторых кнопок.")


@router.message(Command("info"))
async def Help(msg: Message):
    await msg.answer(
        "1. Случайные группы - это группы случайно подобранных 10 людей.\n"
        "2. Чтобы отписаться от группы, нужно ввести '/stop точное название группы'.\n"
        "3. Чтобы удалить свою работу, вам нужно найти нужную работу по названию, а потом "
        "под ней нажать на кнопку 'Удалить эту работу'.\n\n"
        "В боте запрещены:\n"
        "1. Оскорбления в любом виде.\n"
        "2. Реклама.\n"
        "3. Просьбы поставить лайк, проголосовать или подписаться.\n"
        "4. Продажи любых товаров или услуг.\n"
        "5. Оружие, наркотики, психотропные вещества.\n"
        "6. Экстремистский контент и призывы к массовым беспорядкам.\n"
        "7. Сообщения, призывающие к суициду и иным действиям, "
        "способным нанести вред человеку или его имуществу.\n"
        "8. Распространение прочей информации, запрещенной законодательством.\n"
        "9. Порнография в любом виде."
    )


@router.message(Command("delete"))
async def delete(msg: Message, state: FSMContext):
    await msg.answer("Отправьте название группы, которую вы хотите удалить.")
    await state.set_state(Register.delete)


@router.message(Command("stop"))
async def stop(msg: Message, state: FSMContext):
    await state.clear()
    if execute(
            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    ) is None:
        execute(
            "INSERT INTO user_ratings VALUES(?, ?, ?, ?)", VALUES=(msg.chat.id, 0, 0, 0,)
        )
    messages2[str(msg.chat.id)] = list()
    if "/stop " == msg.text[:6]:
        Name = msg.text.replace("/stop ", "")
        execute(
            "DELETE FROM group_subscribers WHERE name = ? AND user_id = ?",
            VALUES=(Name, msg.chat.id)
        )
        await msg.answer("Вы успешно отписались от этой группы!")
        return
    Name = execute(
        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    )
    res = execute("SELECT id, name FROM people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    res2 = execute("SELECT id FROM random_people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    res3 = execute("SELECT * FROM random_person WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    res4 = execute("SELECT * FROM persons WHERE id_interlocutor = ?", VALUES=(msg.chat.id,), one=True)
    res5 = execute("SELECT * FROM persons WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    if res3 is not None:
        ID = res3[0]
        try:
            if ID % 2 == 0:
                chat_id = execute(
                    "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID - 1,), one=True
                )[0]
            else:
                chat_id = execute(
                    "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID + 1,), one=True
                )[0]
            Name = ID if Name is None else Name[0]
            try:
                await bot.send_message(
                    chat_id,
                    f"{f'Пользователь №{ID}' if Name == ID else Name} вышел(а) из чата."
                )
            except Exception:
                pass
            execute("INSERT INTO random_person3 VALUES(?, ?)", VALUES=(res3[0], res3[1],))
        except Exception:
            if ID % 2 == 0:
                chat_id = execute(
                    "SELECT user_id FROM random_person3 WHERE id = ?", VALUES=(ID - 1,), one=True
                )[0]
                execute(
                    "DELETE FROM random_person3 WHERE id = ?", VALUES=(ID - 1,)
                )
            else:
                chat_id = execute(
                    "SELECT user_id FROM random_person3 WHERE id = ?", VALUES=(ID + 1,), one=True
                )[0]
                execute(
                    "DELETE FROM random_person3 WHERE id = ?", VALUES=(ID + 1,)
                )
        Name2 = execute(
            "SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True
        )
        ID2 = ID - 1 if ID % 2 == 0 else ID + 1
        Name2 = f"{f'Пользователь №{ID2}' if Name2 is None else Name2[0]}"
        execute(
            "INSERT INTO chats VALUES(?, ?, ?)", VALUES=(msg.from_user.id, chat_id, Name2,)
        )
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="-2", callback_data=f"score:{chat_id}:-2"),
            InlineKeyboardButton(text="-1", callback_data=f"score:{chat_id}:-1"),
            InlineKeyboardButton(text="0", callback_data=f"score:{chat_id}:0"),
            InlineKeyboardButton(text="1", callback_data=f"score:{chat_id}:1"),
            InlineKeyboardButton(text="2", callback_data=f"score:{chat_id}:2")
        )
        builder.row(InlineKeyboardButton(text="Случайная группа", callback_data="random_group"))
        builder.row(InlineKeyboardButton(text="🌀 Анонимный чат", callback_data="anonymous_chat"))
        execute("DELETE FROM random_person WHERE user_id = ?", VALUES=(msg.chat.id,))
        await msg.answer(
            "Выберите балл для собеседника или то, что вас интересует.", reply_markup=builder.as_markup()
        )
        return
    elif res is not None:
        Name = res[1]
        res = execute(
            "SELECT user_id FROM group_subscribers WHERE name = ? AND user_id <> ?",
            VALUES=(Name, msg.chat.id)
        )
        for i in res:
            try:
                await bot.send_message(i[0], f"Пользователь №{msg.from_user.id} вышел(а) из чата.")
            except Exception:
                pass
        execute("DELETE FROM people WHERE user_id = ?", VALUES=(msg.chat.id,))
    elif res2 is not None:
        ID = res2[0]
        ID2 = ID
        while ID2 % 10 != 0:
            ID2 += 1
        Name = ID if Name is None else Name[0]
        for i in range(10):
            if ID2 != ID:
                try:
                    chat_id = execute(
                        "SELECT user_id FROM random_people WHERE id = ?", VALUES=(ID2,), one=True
                    )[0]
                    Name2 = execute(
                        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True
                    )
                    Name2 = f"{f'Пользователь №{ID2}' if Name2 is None else Name2[0]}"
                    execute(
                        "INSERT INTO chats VALUES(?, ?, ?)", VALUES=(msg.from_user.id, chat_id, Name2,)
                    )
                    execute(
                        "INSERT INTO chats VALUES(?, ?, ?)",
                        VALUES=(chat_id, msg.from_user.id, f"{f'Пользователь №{ID}' if Name == ID else Name}",)
                    )
                    await bot.send_message(
                        chat_id, f"{f'Пользователь №{ID}' if Name == ID else Name} вышел(а) из чата."
                    )
                except Exception:
                    pass
            ID2 -= 1
        execute("DELETE FROM random_people WHERE user_id = ?", VALUES=(msg.chat.id,))
    elif res4 is not None:
        try:
            chat_id = res4[0]
            Name = execute(
                "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                VALUES=(msg.chat.id, chat_id,), one=True
            )[0]
            await bot.send_message(
                chat_id,
                f"{Name} вышел(а) из чата."
            )
        except Exception:
            pass
        execute("DELETE FROM persons WHERE id_interlocutor = ?", VALUES=(msg.chat.id,))
    elif res5 is not None:
        try:
            chat_id = res5[1]
            Name = execute(
                "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                VALUES=(msg.chat.id, chat_id,), one=True
            )[0]
            await bot.send_message(
                chat_id,
                f"{Name} вышел(а) из чата."
            )
        except Exception:
            pass
        execute("DELETE FROM persons WHERE user_id = ?", VALUES=(msg.chat.id,))
    else:
        execute("DELETE FROM random_person2 WHERE user_id = ?", VALUES=(msg.chat.id,))
    markup = InlineKeyboardMarkup(inline_keyboard=kb.menu2)
    await msg.answer("Диалог остановлен! Что вас интересует?", reply_markup=markup)


@router.message(Command("ban"))
async def Ban(msg: Message):
    if "/ban " in msg.text:
        try:
            data = msg.text.lstrip("/ban ").split(":")
            Name = data[1]
            Res = execute(
                "SELECT * FROM groups WHERE user_id = ? AND name = ?",
                VALUES=(msg.chat.id, Name,), one=True
            )
            if Res is not None or msg.from_user.id in config.admins:
                user_id = int(data[0])
                date = str(datetime.datetime.now())
                days = -1
                execute(
                    "INSERT INTO banned_subscribers VALUES(?, ?, ?, ?)",
                    (Name, date, days, user_id,)
                )
                await bot.send_message(
                    user_id, f"Вы были забанены в группе '{Name}' создателем этой группы."
                )
                await msg.answer(f"Вы успешно забанили пользователя с ID {user_id}!")
            else:
                await msg.answer("Вы не являетесь создателем этой группы!")
        except Exception:
            await msg.answer("Этого пользователя не существует или неверные данные!")
    else:
        await msg.answer(
            "Чтобы забанить пользователя, вам нужно ввести эти данные:\n"
            "/ban <номер пользователя>:<название группы>\n\n"
            "Пример: /ban 123456789:group1", parse_mode=None
        )


@router.message(Command("unban"))
async def Unban(msg: Message):
    if "/unban " in msg.text:
        try:
            data = msg.text.lstrip("/unban ").split(":")
            Name = data[1]
            Res = execute(
                "SELECT * FROM groups WHERE user_id = ? AND name = ?",
                VALUES=(msg.chat.id, Name,), one=True
            )
            if Res is not None or msg.from_user.id in config.admins:
                user_id = int(data[0])
                execute(
                    "DELETE FROM banned_subscribers WHERE name = ? AND user_id = ?",
                    VALUES=(Name, user_id,)
                )
                await bot.send_message(
                    user_id, f"Вы были разбанены в группе '{Name}' создателем этой группы."
                )
                await msg.answer(f"Вы успешно разбанили пользователя с ID {user_id}!")
            else:
                await msg.answer("Вы не являетесь создателем этой группы!")
        except Exception:
            await msg.answer("Этого пользователя не существует или неверные данные!")
    else:
        await msg.answer(
            "Чтобы разбанить пользователя, вам нужно ввести эти данные:\n"
            "/unban <ID пользователя>:<название группы>\n\n"
            "Пример: /unban 123456789:group1", parse_mode=None
        )


@router.message(Command("profile"))
async def profile(msg: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.country_selection_menu)
    await msg.answer("Шаг 1/3: Выберите вашу страну.", reply_markup=markup)


@router.message(Command("search"))
async def search(msg: Message):
    if date_check(msg.from_user.id) is not None and date_check(msg.from_user.id) != -1:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.country_selection_menu2)
        await msg.answer("Шаг 1/3: Выберите страну собеседника.", reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
        await msg.answer(
            "У вас нет подписки! Подписка даёт:\n"
            "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
            "2. Функцию установки уникального ника в анонимном чате.\n"
            "3. Функцию удаления сообщений у собеседников.\n"
            "4. Функцию возврата собеседника.\n"
            "Подписку можно получить двумя способами:\n"
            "1. Попасть в топ-10 пользователей.\n"
            "2. Купить.",
            reply_markup=markup
        )


@router.message(Command(commands=["reset", "settings"]))
async def delete_settings(msg: Message):
    execute("DELETE FROM profiles2 WHERE user_id = ?", VALUES=(msg.from_user.id,))
    await msg.answer("Готово!")


@router.message(Command("setusername"))
async def set_username(msg: Message, state: FSMContext):
    if date_check(msg.from_user.id) is not None and date_check(msg.from_user.id) != -1:
        if match_check(msg.from_user.id):
            await msg.answer("Отправьте любой ник.")
            await state.set_state(Register.username)
        else:
            await msg.answer("Во время общения смена ника невозможна.")
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
        await msg.answer(
            "У вас нет подписки! Подписка даёт:\n"
            "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
            "2. Функцию установки уникального ника в анонимном чате.\n"
            "3. Функцию удаления сообщений у собеседников.\n"
            "4. Функцию возврата собеседника.\n"
            "Подписку можно получить двумя способами:\n"
            "1. Попасть в топ-10 пользователей.\n"
            "2. Купить.",
            reply_markup=markup
        )


@router.message(Command("resetusername"))
async def reset_username(msg: Message):
    if date_check(msg.from_user.id) is not None and date_check(msg.from_user.id) != -1:
        execute("DELETE FROM usernames WHERE user_id = ?", VALUES=(msg.from_user.id,))
        await msg.answer("Ваш ник сброшен!")
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
        await msg.answer(
            "У вас нет подписки! Подписка даёт:\n"
            "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
            "2. Функцию установки уникального ника в анонимном чате.\n"
            "3. Функцию удаления сообщений у собеседников.\n"
            "4. Функцию возврата собеседника.\n"
            "Подписку можно получить двумя способами:\n"
            "1. Попасть в топ-10 пользователей.\n"
            "2. Купить.",
            reply_markup=markup
        )


@router.message(Command("deletemessage"))
async def delete_message(msg: Message):
    if date_check(msg.chat.id) is not None and date_check(msg.chat.id) != -1:
        List = [] if str(msg.from_user.id) not in messages2 else \
            messages2[str(msg.from_user.id)]
        try:
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Да", callback_data=f"delete_message:{-1}"),
                InlineKeyboardButton(text="Нет", callback_data=f"other_message:{-1}")
            )
            List2 = List[-1]
            await send2(msg.chat.id, List2[0])
            await msg.answer("Вы хотите удалить это сообщение?", reply_markup=builder.as_markup())
        except Exception:
            await msg.answer(
                "Извините, не нашлось ваших сообщений. Это может быть связано с тем, что вы вышли из чата, "
                "или с отключением бота."
            )
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
        await msg.answer(
            "У вас нет подписки! Подписка даёт:\n"
            "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
            "2. Функцию установки уникального ника в анонимном чате.\n"
            "3. Функцию удаления сообщений у собеседников.\n"
            "4. Функцию возврата собеседника.\n"
            "Подписку можно получить двумя способами:\n"
            "1. Попасть в топ-10 пользователей.\n"
            "2. Купить.",
            reply_markup=markup
        )


@router.message(Command("statistics"))
async def Statistics(msg: Message):
    if execute(
        "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    ) is None:
        execute(
            "INSERT INTO user_ratings VALUES(?, ?, ?, ?)", VALUES=(msg.chat.id, 0, 0, 0,)
        )
    res = execute(
        "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    )
    Text = f"Ваша статистика:\n" \
           f"Количество баллов:\n{res[1]}\n" \
           f"Количество начатых чатов:\n{res[3]}\n" \
           f"Количество отправленных сообщений:\n{res[2]}"
    Res = execute(
        "SELECT * FROM random_people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    )
    if Res is not None:
        ID = Res[0]
        ID2 = ID
        while ID2 % 10 != 0:
            ID2 += 1
        for i in range(10):
            if ID2 != ID:
                try:
                    chat_id = execute(
                        "SELECT user_id FROM random_people WHERE id = ?",
                        VALUES=(ID2,), one=True
                    )[0]
                    Name = execute(
                        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True
                    )
                    Res3 = execute(
                        "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(chat_id,), one=True
                    )
                    Text += f"\n\nСтатистика пользователя {f'№{ID2}' if Name is None else Name[0]}:\n" \
                            f"Количество баллов:\n{Res3[1]}\n" \
                            f"Количество начатых чатов:\n{Res3[3]}\n" \
                            f"Количество отправленных сообщений:\n{Res3[2]}"
                except Exception:
                    pass
            ID2 -= 1
        await msg.answer(Text)
    else:
        await msg.answer(Text)


@router.message(Command("top"))
async def top(msg: Message):
    res = execute("SELECT messages, user_id FROM user_ratings")
    List = sorted(res, key=lambda x: x[0], reverse=True)
    if len(List) >= 10 and List[0][0] >= 200:
        Top = ""
        value = 1
        for v in List:
            if value > 50:
                break
            try:
                res = execute(
                    "SELECT first_name FROM users WHERE user_id = ?", VALUES=(v[1],), one=True
                )
                s = f"{value}. {res[0]} — {v[0]} сообщений\n"
                Top += s
                value += 1
            except Exception:
                pass
        await msg.answer(Top)
        logger.info(f"{msg.from_user.id}: Top!")
    else:
        await msg.answer(
            "Извините, топ сейчас не доступен, так как нет ни одного пользователя, "
            "который отправил больше 200 сообщений."
        )


@router.message(Command("back"))
async def back(msg: Message):
    if date_check(msg.chat.id) is not None and date_check(msg.chat.id) != -1:
        List = execute(
            "SELECT id_interlocutor, user_nickname FROM chats WHERE user_id = ?",
            VALUES=(msg.chat.id,)
        )
        if List:
            List = List[-1]
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Да", callback_data=f"request:{List[0]}"),
                InlineKeyboardButton(text="Нет", callback_data=f"other_interlocutor:{-1}")
            )
            await msg.answer(
                f"Вы хотите продолжить разговор с {List[1]}?",
                reply_markup=builder.as_markup()
            )
        else:
            await msg.answer("Вы ещё не общались!")
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
        await msg.answer(
            "У вас нет подписки! Подписка даёт:\n"
            "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
            "2. Функцию установки уникального ника в анонимном чате.\n"
            "3. Функцию удаления сообщений у собеседников.\n"
            "4. Функцию возврата собеседника.\n"
            "Подписку можно получить двумя способами:\n"
            "1. Попасть в топ-10 пользователей.\n"
            "2. Купить.",
            reply_markup=markup
        )


@router.message(Command("add"))
async def add(msg: Message):
    res = execute("SELECT id FROM random_people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    res2 = execute("SELECT id FROM random_person WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    res3 = execute("SELECT * FROM persons WHERE id_interlocutor = ?", VALUES=(msg.chat.id,), one=True)
    res4 = execute("SELECT * FROM persons WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    if res is not None:
        ID = res[0]
        ID2 = ID
        while ID2 % 10 != 0:
            ID2 += 1
        builder = InlineKeyboardBuilder()
        value = False
        for i in range(10):
            try:
                chat_id = execute(
                    "SELECT user_id FROM random_people WHERE id = ?", VALUES=(ID2,), one=True
                )[0]
                if msg.chat.id != chat_id:
                    Res = execute(
                        "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
                        VALUES=(msg.chat.id, chat_id), one=True
                    )
                    Res2 = execute(
                        "SELECT * FROM friends4 WHERE user_id = ? AND friend_id = ?",
                        VALUES=(msg.chat.id, chat_id), one=True
                    )
                    if Res is None and Res2 is None:
                        Name = execute("SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True)
                        Name = f'Пользователь №{ID2}' if Name is None else Name[0]
                        builder.row(InlineKeyboardButton(text=str(Name), callback_data=f"add:{chat_id}"))
                        value = True
            except Exception:
                pass
            ID2 -= 1
        if value:
            await msg.answer(
                "Выберите того, кого вы хотите добавить в друзья.", reply_markup=builder.as_markup()
            )
        else:
            await msg.answer("Извините, в группе больше нет никого, кого вы можете добавить в друзья.")
    elif res2 is not None:
        ID = res2[0]
        try:
            if ID % 2 == 0:
                ID2 = ID - 1
                chat_id = execute(
                    "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID2,), one=True
                )[0]
            else:
                ID2 = ID + 1
                chat_id = execute(
                    "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID2,), one=True
                )[0]
            if execute(
                "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
                VALUES=(msg.chat.id, chat_id), one=True
            ) is None:
                Name = execute("SELECT name FROM usernames WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
                Name = f'пользователя №{ID}' if Name is None else Name[0]
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"Add:{msg.chat.id}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"cancel:{msg.chat.id}")
                )
                await bot.send_message(
                    chat_id, f"Вы хотите добавить в друзья {Name}?", reply_markup=builder.as_markup()
                )
                await msg.answer("Вы успешно отправили запрос!")
            else:
                await msg.answer("Вы уже добавили этого человека в друзья.")
        except Exception:
            await msg.answer("Извините, собеседник завершил диалог.")
    elif res3 is not None:
        chat_id = res3[0]
        if execute(
            "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
            VALUES=(msg.chat.id, chat_id), one=True
        ) is None:
            try:
                Name = execute(
                    "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                    VALUES=(msg.chat.id, chat_id,), one=True
                )[0]
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"Add:{msg.chat.id}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"cancel:{msg.chat.id}")
                )
                await bot.send_message(
                    chat_id, f"Вы хотите добавить в друзья {Name}?", reply_markup=builder.as_markup()
                )
                await msg.answer("Вы успешно отправили запрос!")
            except Exception:
                await msg.answer("Извините, собеседник завершил диалог.")
        else:
            await msg.answer("Вы уже добавили этого человека в друзья.")
    elif res4 is not None:
        chat_id = res4[1]
        if execute(
                "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
                VALUES=(msg.chat.id, chat_id), one=True
        ) is None:
            try:
                Name = execute(
                    "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                    VALUES=(msg.chat.id, chat_id,), one=True
                )[0]
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"Add:{msg.chat.id}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"cancel:{msg.chat.id}")
                )
                await bot.send_message(
                    chat_id, f"Вы хотите добавить в друзья {Name}?", reply_markup=builder.as_markup()
                )
                await msg.answer("Вы успешно отправили запрос!")
            except Exception:
                await msg.answer("Извините, собеседник завершил диалог.")
        else:
            await msg.answer("Вы уже добавили этого человека в друзья.")
    else:
        await msg.answer("Вы не в диалоге!")


@router.message(Command("friends"))
async def friends(msg: Message):
    if execute(
        "SELECT * FROM friends3 WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    ) is not None:
        Index = 0
        Friends = execute(
            "SELECT friend_id, friend_name FROM friends3 WHERE user_id = ?", VALUES=(msg.chat.id,)
        )
        if len(Friends) > 1:
            FriendId = Friends[0][0]
            FriendName = Friends[0][1]
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
            builder.row(InlineKeyboardButton(text="➡", callback_data=f"next:{Index}"))
        else:
            FriendId = Friends[0][0]
            FriendName = Friends[0][1]
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
        res = execute(
            "SELECT * FROM user_ratings WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        Profile = execute(
            "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        await msg.answer(
            f"Имя: {FriendName}\n\n"
            f"Рейтинг:\n{res[1]}\n"
            f"Количество начатых чатов:\n{res[3]}\n"
            f"Количество отправленных сообщений:\n{res[2]}\n"
            f"Пол: {kb.gender[Profile[0]]}\n"
            f"Страна: {Profile[1]}\n"
            f"Хобби: {kb.hobbies[Profile[2]]}", reply_markup=builder.as_markup()
        )
    else:
        await msg.answer("У вас пока нет друзей...")


@router.message(Register.friend_name)
async def friend_name(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        ID = int(data["ID"])
        Name = str(msg.text)
        if len(Name) <= 40:
            await state.clear()
            execute(
                "UPDATE friends3 SET friend_name = ? WHERE user_id = ? AND friend_id = ?",
                VALUES=(Name, msg.chat.id, ID,)
            )
            execute(
                "UPDATE chats SET user_nickname = ? WHERE id_interlocutor = ? AND user_id = ?",
                VALUES=(Name, ID, msg.chat.id,)
            )
            await msg.answer("Вы успешно изменили ник вашего друга!")
        else:
            await msg.answer("Длина имени больше 40 символов!")
    except Exception:
        await msg.answer("Извините, произошла ошибка.")


@router.message(Register.delete)
async def Delete(msg: Message, state: FSMContext):
    await state.clear()
    try:
        res = execute(
            "SELECT * FROM groups WHERE user_id = ? AND name = ?", VALUES=(msg.chat.id, msg.text), one=True
        )
        if res is not None:
            delete_group(msg.text)
            await msg.answer("Успешно!")
        elif msg.from_user.id in config.admins:
            delete_group(msg.text)
            await msg.answer("Успешно!")
        else:
            await msg.answer("У вас нет этой группы.")
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: Delete")
        await msg.answer("Произошла ошибка, повторите попытку.")
        await state.set_state(Register.delete)


@router.message(Register.username)
async def set_username(msg: Message, state: FSMContext):
    new_name = str(msg.text)
    res = execute("SELECT * FROM usernames WHERE name = ?", VALUES=(new_name,), one=True)
    if res is None:
        if len(new_name) <= 30 and new_name[:12] != "Пользователь":
            await state.clear()
            res2 = execute(
                "SELECT * FROM usernames WHERE user_id = ?", VALUES=(msg.from_user.id,), one=True
            )
            if res2 is None:
                execute(
                    "INSERT INTO usernames VALUES(?, ?)",
                    VALUES=(new_name, msg.from_user.id,)
                )
            else:
                execute(
                    "UPDATE usernames SET name = ? WHERE user_id = ?",
                    VALUES=(new_name, msg.from_user.id,)
                )
            await msg.answer("Вы успешно обновили ник!")
        else:
            await msg.answer("Слишком длинный или недопустимый ник!")
    else:
        await msg.answer("Извините, этот ник уже занят. Повторите попытку.")


@router.message(Register.superuser1)
async def add_a_superuser(message: Message, state: FSMContext):
    await state.clear()
    try:
        ID = int(message.text)
        result = execute("SELECT * FROM users WHERE user_id = ?", VALUES=(ID,), one=True)
        if result is not None:
            execute("INSERT INTO superusers VALUES(?, ?, ?, ?, ?, ?, ?)", VALUES=result)
            execute("DELETE FROM users WHERE user_id = ?", VALUES=(ID,))
            await message.answer("Готово!")
            markup = InlineKeyboardMarkup(inline_keyboard=kb.info_button)
            await bot.send_message(ID, "Админ этого бота выдал вам привилегию 'superuser'!", reply_markup=markup)
        else:
            await message.answer("Этого пользователя нет в бд! Повторите попытку.")
            await state.set_state(Register.superuser1)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: add_a_superuser")


@router.message(Register.superuser2)
async def remove_superuser(message: Message, state: FSMContext):
    await state.clear()
    try:
        ID = int(message.text)
        result = execute("SELECT * FROM superusers WHERE user_id = ?", VALUES=(ID,), one=True)
        if result is not None:
            execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)", VALUES=result)
            execute("DELETE FROM superusers WHERE user_id = ?", VALUES=(ID,))
            await bot.send_message(message.chat.id, "Готово!")
        else:
            await bot.send_message(message.chat.id, "Этого пользователя нет в бд! Повторите попытку.")
            await state.set_state(Register.superuser2)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: remove_superuser")


@router.message(Register.coin)
async def replenish(message: Message, state: FSMContext):
    await state.clear()
    try:
        count = int(message.text)
        if 10 <= count <= 50000:
            res = await pay(count)
            url, label = res[0], res[1]
            replenish_buttons = [
                [
                    InlineKeyboardButton(text="Оплатить", url=url),
                    InlineKeyboardButton(
                        text="Проверить оплату", callback_data=f"CheckBuy_{label}_{count}"
                    )
                ]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=replenish_buttons)
            await message.answer(
                "Нажмите на кнопку 'Оплатить', чтобы перейти на сайт оплаты, а потом на "
                "кнопку 'проверить оплату'.",
                reply_markup=markup
            )
        else:
            await bot.send_message(message.chat.id, "Неверное количество! Повторите попытку.")
            await state.set_state(Register.coin)
    except Exception as EX:
        await message.answer("Введите правильное значение количества монет!")
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: replenish")
        await state.set_state(Register.coin)


@router.message(Register.send_coins)
async def send_coins(msg: Message, state: FSMContext):
    await state.update_data(ID=msg.text)
    await msg.answer("Сколько монет вас интересует?")
    await state.set_state(Register.send_coins2)


@router.message(Register.send_coins2)
async def send_coins2(msg: Message, state: FSMContext):
    try:
        coins = float(msg.text)
        data = await state.get_data()
        ID = int(data["ID"])
        await state.clear()
        res = execute("SELECT coin FROM users WHERE user_id = %d" % (ID,), one=True)[0]
        Coins = coins + res
        execute("UPDATE users SET coin = %f WHERE user_id = %d" % (Coins, ID,))
        await msg.answer("Вы успешно пополнили баланс!")
        await bot.send_message(ID, f"Админ этого бота пополнил ваш баланс на {coins} XCoin.")
    except Exception as EX:
        await msg.answer("Что-то пошло не так. Повторите попытку.")
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: send_coins2")
        await state.set_state(Register.send_coins)


@router.message(Register.user_id)
async def get_user_id(msg: Message, state: FSMContext):
    await state.update_data(user_id=msg.text)
    await msg.answer("Введите текст сообщения.")
    await state.set_state(Register.sms)


@router.message(Register.sms)
async def send_sms(msg: Message, state: FSMContext):
    try:
        user_id = await state.get_data()
        await state.clear()
        user_id = int(user_id["user_id"])
        await bot.send_message(user_id, msg.text)
        await msg.answer("Отправлено!")
    except Exception as EX:
        await msg.answer("Что-то пошло не так.")
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: send_sms")


@router.message(Register.sms2)
async def send_sms2(msg: Message, state: FSMContext):
    await state.clear()
    conn = sqlite3.connect(config.database)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM users;")
    all_results = cur.fetchall()
    cur.execute("SELECT chat_id FROM superusers;")
    all_results2 = cur.fetchall()
    cur.close()
    conn.close()
    value = 0
    Text = msg.text
    for i in all_results:
        print(f"Отправка смс {i[0]} (user).")
        try:
            await bot.send_message(i[0], Text)
            print("Смс успешно отправлено!")
            value += 1
        except Exception:
            pass
    for i in all_results2:
        print(f"Отправка смс {i[0]} (superuser).")
        try:
            await bot.send_message(i[0], Text)
            print("Смс успешно отправлено!")
            value += 1
        except Exception:
            pass
    print("Готово!")
    await msg.answer(f"Отправлено сообщений: {value}.")


@router.message(Register.friend_id)
async def friend_id(msg: Message, state: FSMContext):
    await state.clear()
    try:
        ID = int(msg.text)
        execute("INSERT INTO friends VALUES(?, ?)", (msg.chat.id, ID,))
    except Exception:
        username = str(msg.text).replace("@", "")
        execute("INSERT INTO friends2 VALUES(?, ?)", (msg.chat.id, username,))
    await msg.answer("Вы можете пригласить друга! Ваш баланс будет пополнен на 30 монет!")


@router.message(Register.user_id3)
async def unban(msg: Message, state: FSMContext):
    try:
        ID = int(msg.text)
        execute("DELETE FROM banned_users WHERE user_id = ?", VALUES=(ID,))
        await msg.answer("Готово!")
        await bot.send_message(ID, "Вы были разбанены.")
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: unban")
        await msg.answer("Произошла ошибка, повторите попытку.")
        await state.set_state(Register.user_id3)


@router.message(Register.user_id2)
async def ban(msg: Message, state: FSMContext):
    try:
        await state.update_data(user_id2=int(msg.text))
        await msg.answer("По какой причине?")
        await state.set_state(Register.reason)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: ban")
        await msg.answer("Произошла ошибка, повторите попытку.")
        await state.set_state(Register.user_id2)


@router.message(Register.reason)
async def reason(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        date = str(datetime.datetime.now())
        days = -1
        ID = int(data["user_id2"])
        if execute("SELECT * FROM users WHERE user_id = %d" % (ID,), one=True) is not None:
            execute("INSERT INTO banned_users VALUES(?, ?, ?)", (date, days, ID,))
            try:
                await bot.send_message(ID, f"Вы были забанены по причине:\n{msg.text}")
            except Exception:
                pass
            await msg.answer("Готово!")
        else:
            await msg.answer("Этого пользователя нет в базе данных!")
            await state.set_state(Register.user_id2)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: reason")
        await msg.answer("Произошла ошибка, повторите попытку.")
        await state.set_state(Register.user_id2)


@router.message(Register.reason2)
async def reason2(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        res = execute("SELECT photo FROM groups2 WHERE name = ?", VALUES=(data["Name2"],), one=True)
        if res is not None:
            execute("DELETE FROM groups2 WHERE name = ?", VALUES=(data["Name2"],))
            os.remove(res[0])
            await msg.answer("Успешно!")
            await bot.send_message(data["ID"], f"Ваша группа не прошла проверку по причине:\n{msg.text}")
        else:
            await msg.answer("Этой группы нет в базе данных!")
    except Exception as EX:
        await msg.answer(str(EX))


@router.message(Register.name)
async def name(msg: Message, state: FSMContext):
    try:
        if 5 <= len(msg.text) <= 30:
            res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            if res is None:
                res = execute(
                    "SELECT * FROM groups WHERE name = ?", VALUES=(msg.text,), one=True
                )
                res2 = execute(
                    "SELECT * FROM groups2 WHERE name = ?", VALUES=(msg.text,), one=True
                )
                if res is None and res2 is None:
                    await state.update_data(
                        name=msg.text.replace(":", "").replace("<", "").replace(">", "")
                    )
                    await msg.answer("Отправьте описание к вашей группе.")
                    await state.set_state(Register.description)
                else:
                    await msg.answer("Это название уже есть в базе данных. Повторите попытку.")
                    await state.set_state(Register.name)
            else:
                await msg.answer("Вы были забанены.")
                await state.clear()
        else:
            await msg.answer(
                "Длина названия должна быть не больше 30 символов и не меньше 5! Повторите попытку."
            )
            await state.set_state(Register.name)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: name")
        await msg.answer("Произошла ошибка. Повторите попытку.")
        await state.set_state(Register.name)


@router.message(Register.description)
async def Description(msg: Message, state: FSMContext):
    if len(str(msg.text)) <= 2000:
        await state.update_data(
            description=msg.text.replace("<", "").replace(">", "")
        )
        await msg.answer("Отправьте аватарку вашей группы.")
        await state.set_state(Register.photo)
    else:
        await msg.answer("Длина описания больше 2000 символов! Повторите попытку.")
        await state.set_state(Register.description)


@router.message(Register.photo)
async def Photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        List1 = os.listdir(directory)
        List2 = []
        for i in List1:
            v = i.replace("Image", "").split(".")[0]
            List2.append(int(v))
        Index = max(List2) if List2 else 0
        file_name = f"Image{Index+1}.png"
        path = directory + file_name
        await bot.download(msg.photo[-1], destination=path)
        await state.update_data(photo=path)

        markup = InlineKeyboardMarkup(inline_keyboard=kb.confirmation_button)
        image = FSInputFile(path)
        await msg.answer_photo(
            image,
            caption=f"Категория: {data['category']}\n"
                    f"Название: {data['name']}\n"
                    f"Описание: {data['description']}\n"
                    f"Тип: {'Публичная' if data['type'] == 0 else 'Приватная'}",
            reply_markup=markup
        )
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: Photo")
        await msg.answer("Произошла ошибка. Повторите попытку.")
        await state.set_state(Register.photo)


@router.message(Register.name2)
async def search(msg: Message):
    try:
        Name = str(msg.text)
        subscribers = execute("SELECT * FROM group_subscribers WHERE name = ?", VALUES=(Name,))
        number = len(subscribers)
        res = execute("SELECT * FROM groups WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        description = res[4]
        photo = res[5]
        views = res[7]

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Вступить", callback_data=f"join:{Name}"))

        image = FSInputFile(photo)
        await msg.answer_photo(
            photo=image,
            caption=f"{Name}\n\n{description}\n\n"
                    f"Количество подписчиков: {number}\n"
                    f"Количество просмотров: {views}\n"
                    f"Дата создания: {date.split(' ')[0]}",
            reply_markup=builder.as_markup()
        )
        execute("UPDATE groups SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except Exception:
        await msg.answer("Извините, ничего не нашлось...")


@router.message(Register.name3)
async def search2(msg: Message):
    try:
        Name = str(msg.text)
        subscribers = execute("SELECT * FROM group_subscribers WHERE name = ?", VALUES=(Name,))
        number = len(subscribers)
        res = execute("SELECT * FROM groups WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        description = res[4]
        photo = res[5]
        views = res[7]

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Вступить", callback_data=f"Join:{Name}"))

        image = FSInputFile(photo)
        await msg.answer_photo(
            photo=image,
            caption=f"{Name}\n\n{description}\n\n"
                    f"Количество подписчиков: {number}\n"
                    f"Количество просмотров: {views}\n"
                    f"Дата создания: {date.split(' ')[0]}",
            reply_markup=builder.as_markup()
        )
        execute("UPDATE groups SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except Exception:
        await msg.answer("Извините, ничего не нашлось...")


@router.message(Register.work_name)
async def work_name(msg: Message, state: FSMContext):
    try:
        if len(msg.text) <= 30:
            res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            if res is None:
                res = execute(
                    "SELECT * FROM works WHERE name = ?", VALUES=(msg.text,), one=True
                )
                res2 = execute(
                    "SELECT * FROM works2 WHERE name = ?", VALUES=(msg.text,), one=True
                )
                if res is None and res2 is None:
                    await state.update_data(
                        name=msg.text.replace(":", "").replace("<", "").replace(">", "")
                    )
                    await msg.answer(
                        "Отправьте вашу работу. <b>Внимание!</b> Работа должна быть ввиде фото или аудио файла!"
                    )
                    await state.set_state(Register.work_file)
                else:
                    await msg.answer("Это название уже есть в базе данных. Повторите попытку.")
                    await state.set_state(Register.work_name)
            else:
                await msg.answer("Вы были забанены.")
                await state.clear()
        else:
            await msg.answer(
                "Длина названия должна быть не больше 30 символов! Повторите попытку."
            )
            await state.set_state(Register.work_name)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: work_name")
        await msg.answer("Произошла ошибка. Повторите попытку.")
        await state.set_state(Register.work_name)


@router.message(Register.work_file)
async def work_file(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.confirmation_button2)
        if msg.content_type == "photo":
            List1 = os.listdir(directory2)
            List2 = []
            for i in List1:
                v = i.replace("Work", "").split(".")[0]
                List2.append(int(v))
            Index = max(List2) if List2 else 0
            file_name = f"Work{Index+1}.png"
            path = directory2 + file_name
            await bot.download(msg.photo[-1], destination=path)
            await state.update_data(file=path)
            await state.update_data(type=0)
            image = FSInputFile(path)
            await msg.answer_photo(
                image,
                caption=f"Название: {data['name']}",
                reply_markup=markup
            )
        elif msg.content_type == "audio":
            List1 = os.listdir(directory2)
            List2 = []
            for i in List1:
                v = i.replace("Work", "").split(".")[0]
                List2.append(int(v))
            Index = max(List2) if List2 else 0
            file_name = f"Work{Index+1}.mp3"
            path = directory2 + file_name
            await bot.download(msg.audio.file_id, destination=path)
            await state.update_data(file=path)
            await state.update_data(type=1)
            audio = FSInputFile(path)
            await msg.answer_audio(
                audio=audio,
                caption=f"Название: {data['name']}",
                reply_markup=markup
            )
        else:
            await msg.answer("Неверное сообщение! Повторите попытку.")
            await state.set_state(Register.work_file)
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: work_file")
        await msg.answer("Произошла ошибка. Повторите попытку.")
        await state.set_state(Register.work_file)


@router.message(Register.work_name2)
async def work_name2(msg: Message):
    try:
        Name = str(msg.text)
        res = execute("SELECT * FROM works WHERE name = ?", VALUES=(Name,), one=True)
        ID = res[0]
        date = res[1]
        category = res[2]
        file = res[5]
        views = res[6]
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="1 ⭐", callback_data=f"1:star:{Name}"),
            InlineKeyboardButton(text="2 ⭐", callback_data=f"2:star:{Name}"),
            InlineKeyboardButton(text="3 ⭐", callback_data=f"3:star:{Name}"),
            InlineKeyboardButton(text="4 ⭐", callback_data=f"4:star:{Name}"),
            InlineKeyboardButton(text="5 ⭐", callback_data=f"5:star:{Name}")
        )
        if ID == msg.from_user.id:
            builder.row(InlineKeyboardButton(text="Удалить эту работу", callback_data=f"delete:{Name}"))
        res2 = execute("SELECT rating FROM stars WHERE name = ?", VALUES=(Name,))
        rating = 0
        for i in res2:
            rating += i[0]
        number_of_ratings = len(res2)
        file = FSInputFile(file)
        if category == 0:
            await msg.answer_photo(
                photo=file,
                caption=f"{Name}\n\n"
                        f"{f'Рейтинг: {rating/number_of_ratings} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                        f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
                reply_markup=builder.as_markup()
            )
        else:
            await msg.answer_audio(
                audio=file,
                caption=f"{Name}\n"
                        f"{f'Рейтинг: {rating/number_of_ratings} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                        f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
                reply_markup=builder.as_markup()
            )
        execute("UPDATE works SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: work_name2")
        await msg.answer("Извините, ничего не нашлось...")


@router.message(Register.mailing)
async def mailing(msg: Message, state: FSMContext):
    await state.clear()
    Text = "Реклама отключается при покупке подписки."
    conn = sqlite3.connect(config.database)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM users;")
    all_results = cur.fetchall()
    cur.close()
    conn.close()
    value = 0
    markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
    for i in all_results:
        print(f"Отправка смс {i[0]}.")
        try:
            if date_check(i[0]) is None or date_check(i[0]) == -1:
                res = await send3(i[0], msg, Text, markup)
                if not res:
                    break
                print("Смс успешно отправлено!")
                value += 1
        except Exception:
            pass
    print("Готово!")
    await msg.answer(f"Отправлено сообщений: {value}.")


@router.message(Register.idea)
async def idea(msg: Message, state: FSMContext):
    try:
        await state.clear()
        execute("INSERT INTO ideas VALUES(?, ?, ?)", (datetime.datetime.now(), msg.chat.id, msg.text,))
        await msg.answer("Готово!")
    except Exception as EX:
        await msg.answer("Произошла ошибка, возможно, неверное сообщение, повторите попытку.")
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: idea")
        await state.set_state(Register.idea)


@router.message()
async def TEXT(msg: Message):
    if execute(
            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    ) is None:
        execute(
            "INSERT INTO user_ratings VALUES(?, ?, ?, ?)", VALUES=(msg.chat.id, 0, 0, 0,)
        )
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
    Name = execute(
        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
    )
    if res is None:
        if len(str(msg.text)) <= 3000 and len(str(msg.caption)) <= 500:
            messages2[str(msg.from_user.id)] = [] if str(msg.from_user.id) not in messages2 else \
                messages2[str(msg.from_user.id)]
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Пожаловаться", callback_data=f"report:{msg.chat.id}:{msg.from_user.username}"
                )
            )
            res = execute("SELECT id, name FROM people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            res2 = execute("SELECT id FROM random_people WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            res3 = execute("SELECT id FROM random_person WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            res4 = execute("SELECT * FROM persons WHERE id_interlocutor = ?", VALUES=(msg.chat.id,), one=True)
            res5 = execute("SELECT * FROM persons WHERE user_id = ?", VALUES=(msg.chat.id,), one=True)
            if res3 is not None:
                Res = execute(
                    "SELECT messages FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
                )[0]
                Res += 1
                execute("UPDATE user_ratings SET messages = ? WHERE user_id = ?", VALUES=(Res, msg.chat.id,))
            if res is not None:
                Name = res[1]
                res2 = execute(
                    "SELECT * FROM banned_subscribers WHERE user_id = ? AND name = ?",
                    VALUES=(msg.chat.id, Name,), one=True
                )
                if res2 is None:
                    builder.row(InlineKeyboardButton(text="Ответить", callback_data=f"join:{Name}"))
                    res = execute(
                        "SELECT user_id FROM group_subscribers WHERE name = ? AND user_id <> ?",
                        VALUES=(Name, msg.chat.id,)
                    )
                    for i in res:
                        try:
                            res2 = await send(
                                i[0],
                                msg, f"<i>Пользователь №{msg.chat.id}</i>\nГруппа: {Name}", markup=builder.as_markup()
                            )
                            if not res2:
                                break
                        except Exception:
                            pass
                else:
                    await msg.answer("Вы были забанены.")
            elif res2 is not None:
                number_of_messages[msg.chat.id] = 1 if msg.chat.id not in number_of_messages else \
                    number_of_messages[msg.chat.id] + 1
                ID = res2[0]
                ID2 = ID
                while ID2 % 10 != 0:
                    ID2 += 1
                Name = ID if Name is None else Name[0]
                res = execute("SELECT id FROM random_people WHERE id >= ?", VALUES=(ID,))
                ID3 = res[-1][0] if res else 1
                if ID3 > 10:
                    while ID3 % 10 != 0:
                        ID3 -= 1
                if ID3 - ID >= 0 and ID3 >= 10:
                    Res = execute(
                        "SELECT messages FROM user_ratings WHERE user_id = ?", VALUES=(msg.chat.id,), one=True
                    )[0]
                    Res += 1
                    execute("UPDATE user_ratings SET messages = ? WHERE user_id = ?", VALUES=(Res, msg.chat.id,))
                    List = []
                    for i in range(10):
                        if ID2 != ID:
                            try:
                                chat_id = execute(
                                    "SELECT user_id FROM random_people WHERE id = ?",
                                    VALUES=(ID2,), one=True
                                )[0]
                                res = await send(
                                    chat_id, msg, f"<i>{f'Пользователь №{ID}' if Name == ID else Name}</i>",
                                    markup=builder.as_markup()
                                )
                                if not res:
                                    break
                                List.append(res)
                            except Exception:
                                pass
                        ID2 -= 1
                    if List:
                        messages2[str(msg.from_user.id)].append(List)
                else:
                    await msg.answer("Пожалуйста, подождите, пока найдутся все собеседники.")
            elif res3 is not None:
                ID = res3[0]
                try:
                    if ID % 2 == 0:
                        Name = ID if Name is None else Name[0]
                        chat_id = execute(
                            "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID - 1,), one=True
                        )[0]
                        res = await send(
                            chat_id, msg, f"<i>{f'Пользователь №{ID}' if Name == ID else Name}</i>",
                            markup=builder.as_markup()
                        )
                    else:
                        Name = ID if Name is None else Name[0]
                        chat_id = execute(
                            "SELECT user_id FROM random_person WHERE id = ?", VALUES=(ID + 1,), one=True
                        )[0]
                        res = await send(
                            chat_id, msg, f"<i>{f'Пользователь №{ID}' if Name == ID else Name}</i>",
                            markup=builder.as_markup()
                        )
                    if res:
                        List = [res]
                        messages2[str(msg.from_user.id)].append(List)
                except Exception:
                    pass
            elif res4 is not None:
                try:
                    chat_id = res4[0]
                    Name = execute(
                        "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                        VALUES=(msg.chat.id, chat_id,), one=True
                    )
                    Name2 = execute(
                        "SELECT friend_name FROM friends3 WHERE friend_id = ? AND user_id = ?",
                        VALUES=(msg.chat.id, chat_id,), one=True
                    )
                    Name = Name2[0] if Name2 is not None else Name[0]
                    res = await send(
                        chat_id, msg, f"<i>{Name}</i>",
                        markup=builder.as_markup()
                    )
                    if res:
                        List = [res]
                        messages2[str(msg.from_user.id)].append(List)
                except Exception:
                    pass
            elif res5 is not None:
                try:
                    chat_id = res5[1]
                    Name = execute(
                        "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                        VALUES=(msg.chat.id, chat_id,), one=True
                    )
                    Name2 = execute(
                        "SELECT friend_name FROM friends3 WHERE friend_id = ? AND user_id = ?",
                        VALUES=(msg.chat.id, chat_id,), one=True
                    )
                    Name = Name2[0] if Name2 is not None else Name[0]
                    res = await send(
                        chat_id, msg, f"<i>{Name}</i>",
                        markup=builder.as_markup()
                    )
                    if res:
                        List = [res]
                        messages2[str(msg.from_user.id)].append(List)
                except Exception:
                    pass
            else:
                await msg.answer("Неверное сообщение!")
        else:
            await msg.answer("Сообщение слишком длинное!")
    else:
        await msg.answer("Вы были забанены.")


@router.callback_query(F.data == "join_group")
async def callback(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.group_type_menu)
    await call.message.answer(
        "Куда вы хотите попасть? Случайные группы - "
        "это группы случайно подобранных 10 людей.",
        reply_markup=markup
    )


@router.callback_query(F.data == "random_group")
async def callback2(call: CallbackQuery):
    if execute(
            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
    ) is None:
        execute(
            "INSERT INTO user_ratings VALUES(?, ?, ?, ?)", VALUES=(call.message.chat.id, 0, 0, 0,)
        )
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True)
    if res is None:
        if match_check(call.message.chat.id):
            res = execute("SELECT id, user_id FROM random_people")
            ID = res[-1][0] + 1 if res else 1
            execute(
                "INSERT INTO random_people VALUES(?, ?)", VALUES=(ID, call.message.chat.id)
            )
            Name = execute(
                "SELECT name FROM usernames WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
            )
            Name = ID if Name is None else Name[0]
            if ID % 10 == 0:
                Res = execute(
                    "SELECT chats FROM user_ratings WHERE user_id = ?",
                    VALUES=(call.message.chat.id,), one=True
                )[0]
                Res += 1
                execute(
                    "UPDATE user_ratings SET chats = ? WHERE user_id = ?",
                    VALUES=(Res, call.message.chat.id,)
                )
                for i in res[-9:]:
                    try:
                        Res = execute(
                            "SELECT chats FROM user_ratings WHERE user_id = ?",
                            VALUES=(i[0],), one=True
                        )[0]
                        Res += 1
                        execute(
                            "UPDATE user_ratings SET chats = ? WHERE user_id = ?",
                            VALUES=(Res, i[0],)
                        )
                    except Exception:
                        pass
                    try:
                        await bot.send_message(
                            i[1],
                            "Собеседники найдены! Вы можете начинать общение!"
                        )
                    except Exception:
                        pass
                await call.message.answer(
                    f"Собеседники найдены! Вы можете отправить текст собеседникам! Для выхода введите /stop. "
                    f"Ваш ник:\n{f'Пользователь №{ID}' if Name == ID else Name}"
                )
            else:
                await call.message.answer(
                    f"Пожалуйста, подождите, пока найдутся все собеседники. "
                    f"Ваш ник:\n{f'Пользователь №{ID}' if Name == ID else Name}\n\n"
                    f"Если вы захотите удалить своё сообщение у собеседников, то вы можете это сделать при "
                    f"помощи команды /deletemessage."
                )
        else:
            await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")
    else:
        await call.message.answer("Вы были забанены.")


@router.callback_query(F.data == "public_group")
async def callback3(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.search_menu)
    await call.message.answer("Как вы хотите найти группу?", reply_markup=markup)


@router.callback_query(F.data == "name_search")
async def callback4(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте точное название.")
    await state.set_state(Register.name2)


@router.callback_query(F.data == "category_search")
async def callback5(call: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for i in range(0, len(kb.categories) - 1, 2):
        data = kb.categories[i]
        data2 = kb.categories[i+1]
        builder.row(
            InlineKeyboardButton(text=data, callback_data=data+"_"),
            InlineKeyboardButton(text=data2, callback_data=data2+"_")
        )
    builder.row(InlineKeyboardButton(text="Другая категория", callback_data="Другое_"))
    await call.message.answer("Какая категория вас интересует?", reply_markup=builder.as_markup())


@router.callback_query(F.data == "private_group")
async def callback6(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте точное название этой группы.")
    await state.set_state(Register.name3)


@router.callback_query(F.data == "add_group")
async def callback7(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.group_type_menu2)
    await call.message.answer(
        "Что вы хотите добавить? "
        "Приватные группы может добавлять только ограниченный круг лиц.",
        reply_markup=markup
    )


@router.callback_query(F.data.split(":")[0] == "t")
async def callback8(call: CallbackQuery, state: FSMContext):
    Type = int(call.data.split(":")[1])
    res = True
    if Type == 1 and call.message.chat.id not in config.admins:
        res = False
    if res:
        await state.update_data(type=Type)
        builder = InlineKeyboardBuilder()
        for i in range(0, len(kb.categories) - 1, 2):
            data = kb.categories[i]
            data2 = kb.categories[i + 1]
            builder.row(
                InlineKeyboardButton(text=data, callback_data=f"{data}"),
                InlineKeyboardButton(text=data2, callback_data=f"{data}")
            )
        builder.row(InlineKeyboardButton(text="Другая категория", callback_data="Другое"))
        await call.message.answer("Какая должна быть категория у вашей группы?", reply_markup=builder.as_markup())
    else:
        await call.message.answer("Вы не можете добавить группу этого типа.")


@router.callback_query(F.data == "anonymous_chat")
async def callback9(call: CallbackQuery):
    if execute(
            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
    ) is None:
        execute(
            "INSERT INTO user_ratings VALUES(?, ?, ?, ?)", VALUES=(call.message.chat.id, 0, 0, 0,)
        )
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True)
    if res is None:
        if match_check(call.message.chat.id):
            profile1 = execute(
                "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
                VALUES=(call.message.chat.id,), one=True
            )
            if profile1 is not None:
                profile2 = execute(
                    "SELECT gender, country_code, hobby FROM profiles2 WHERE user_id = ?",
                    VALUES=(call.message.chat.id,)
                )
                if profile2 and date_check(call.message.chat.id) == -1:
                    profile2 = None
                    execute("DELETE FROM profiles2 WHERE user_id = ?", VALUES=(call.message.chat.id,))
                    markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
                    await call.message.answer(
                        "Так как у вас закончилась подписка, произошёл сброс настроек поиска.",
                        reply_markup=markup
                    )
                if profile2:
                    ID = None
                    res = execute("SELECT user_id FROM random_person2")
                    Profile = None
                    for i in res:
                        Profile = execute(
                            "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
                            VALUES=(i[0],), one=True
                        )
                        Profile2 = execute(
                            "SELECT gender, country_code, hobby FROM profiles2 WHERE user_id = ?",
                            VALUES=(i[0],)
                        )
                        if Profile in profile2 and \
                                (profile1 in Profile2 or not Profile2):
                            ID = i[0]
                            break
                    if ID is not None:
                        res = execute(
                            "SELECT chats FROM user_ratings WHERE user_id = ?", VALUES=(ID,), one=True
                        )[0]
                        res += 1
                        execute("UPDATE user_ratings SET chats = ? WHERE user_id = ?", VALUES=(res, ID,))

                        execute("DELETE FROM random_person2 WHERE user_id = ?", VALUES=(ID,))
                        res = execute("SELECT id, user_id FROM random_person")
                        ID2 = res[-1][0] + 1 if res else 1
                        if ID2 % 2 == 0:
                            ID2 += 1
                        execute(
                            "INSERT INTO random_person VALUES(?, ?)", VALUES=(ID2, ID,)
                        )

                        res = execute(
                            "SELECT chats FROM user_ratings WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )[0]
                        res += 1
                        execute(
                            "UPDATE user_ratings SET chats = ? WHERE user_id = ?",
                            VALUES=(res, call.message.chat.id,)
                        )

                        res = execute("SELECT id, user_id FROM random_person")
                        ID2 = res[-1][0] + 1
                        execute(
                            "INSERT INTO random_person VALUES(?, ?)", VALUES=(ID2, call.message.chat.id,)
                        )

                        Name = execute(
                            "SELECT name FROM usernames WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )
                        res = execute(
                            "SELECT * FROM user_ratings WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )
                        try:
                            await bot.send_message(
                                ID,
                                f"Собеседник найден! Вы можете отправить текст собеседнику! Для выхода введите /stop.\n\n"
                                f"Данные собеседника:\n"
                                f"Рейтинг:\n{res[1]}\n"
                                f"Количество начатых чатов:\n{res[3]}\n"
                                f"Количество отправленных сообщений:\n{res[2]}\n"
                                f"Пол: {kb.gender[profile1[0]]}\n"
                                f"Страна: {profile1[1]}\n"
                                f"Хобби: {kb.hobbies[profile1[2]]}\n\n"
                                f"Если вы захотите удалить своё сообщение у собеседника, то вы можете это сделать при "
                                f"помощи команды /deletemessage."
                            )
                        except Exception:
                            pass
                        res = execute(
                            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(ID,), one=True
                        )
                        await call.message.answer(
                            f"Собеседник найден! Вы можете отправить текст собеседнику! Для выхода введите /stop. "
                            f"Ваш ник:\n{f'Пользователь №{ID2}' if Name is None else Name[0]}\n\n"
                            f"Данные собеседника:\n"
                            f"Рейтинг:\n{res[1]}\n"
                            f"Количество начатых чатов:\n{res[3]}\n"
                            f"Количество отправленных сообщений:\n{res[2]}\n"
                            f"Пол: {kb.gender[Profile[0]]}\n"
                            f"Страна: {Profile[1]}\n"
                            f"Хобби: {kb.hobbies[Profile[2]]}\n\n"
                            f"Если вы захотите удалить своё сообщение у собеседника, то вы можете это сделать при "
                            f"помощи команды /deletemessage."
                        )
                    else:
                        execute("INSERT INTO random_person2 VALUES(?)", VALUES=(call.message.chat.id,))
                        await call.message.answer("Пожалуйста, подождите, пока найдётся собеседник.")
                else:
                    ID = None
                    res = execute("SELECT user_id FROM random_person2")
                    Profile = None
                    for i in res:
                        Profile = execute(
                            "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
                            VALUES=(i[0],), one=True
                        )
                        Profile2 = execute(
                            "SELECT gender, country_code, hobby FROM profiles2 WHERE user_id = ?",
                            VALUES=(i[0],)
                        )
                        if profile1 in Profile2 or not Profile2:
                            ID = i[0]
                            break
                    if ID is not None:
                        res = execute(
                            "SELECT chats FROM user_ratings WHERE user_id = ?", VALUES=(ID,), one=True
                        )[0]
                        res += 1
                        execute("UPDATE user_ratings SET chats = ? WHERE user_id = ?", VALUES=(res, ID,))

                        execute("DELETE FROM random_person2 WHERE user_id = ?", VALUES=(ID,))
                        res = execute("SELECT id, user_id FROM random_person")
                        ID2 = res[-1][0] + 1 if res else 1
                        if ID2 % 2 == 0:
                            ID2 += 1
                        execute(
                            "INSERT INTO random_person VALUES(?, ?)", VALUES=(ID2, ID,)
                        )

                        res = execute("SELECT id, user_id FROM random_person")
                        ID2 = res[-1][0] + 1
                        execute(
                            "INSERT INTO random_person VALUES(?, ?)",
                            VALUES=(ID2, call.message.chat.id,)
                        )

                        res = execute(
                            "SELECT chats FROM user_ratings WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )[0]
                        res += 1
                        execute(
                            "UPDATE user_ratings SET chats = ? WHERE user_id = ?",
                            VALUES=(res, call.message.chat.id,)
                        )

                        Name = execute(
                            "SELECT name FROM usernames WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )
                        res = execute(
                            "SELECT * FROM user_ratings WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )
                        try:
                            await bot.send_message(
                                ID,
                                f"Собеседник найден! Вы можете отправить текст собеседнику! Для выхода введите /stop.\n\n"
                                f"Данные собеседника:\n"
                                f"Рейтинг:\n{res[1]}\n"
                                f"Количество начатых чатов:\n{res[3]}\n"
                                f"Количество отправленных сообщений:\n{res[2]}\n"
                                f"Пол: {kb.gender[profile1[0]]}\n"
                                f"Страна: {profile1[1]}\n"
                                f"Хобби: {kb.hobbies[profile1[2]]}\n\n"
                                f"Если вы захотите удалить своё сообщение у собеседника, то вы можете это сделать при "
                                f"помощи команды /deletemessage."
                            )
                        except Exception:
                            pass
                        res = execute(
                            "SELECT * FROM user_ratings WHERE user_id = ?", VALUES=(ID,), one=True
                        )
                        await call.message.answer(
                            f"Собеседник найден! Вы можете отправить текст собеседнику! Для выхода введите /stop. "
                            f"Ваш ник:\n{f'Пользователь №{ID2}' if Name is None else Name[0]}\n\n"
                            f"Данные собеседника:\n"
                            f"Рейтинг:\n{res[1]}\n"
                            f"Количество начатых чатов:\n{res[3]}\n"
                            f"Количество отправленных сообщений:\n{res[2]}\n"
                            f"Пол: {kb.gender[Profile[0]]}\n"
                            f"Страна: {Profile[1]}\n"
                            f"Хобби: {kb.hobbies[Profile[2]]}\n\n"
                            f"Если вы захотите удалить своё сообщение у собеседника, то вы можете это сделать при "
                            f"помощи команды /deletemessage."
                        )
                    else:
                        execute("INSERT INTO random_person2 VALUES(?)", VALUES=(call.message.chat.id,))
                        await call.message.answer("Подождите, пока найдётся собеседник.")
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=kb.country_selection_menu)
                await call.message.answer("Шаг 1/3: Выберите вашу страну.", reply_markup=markup)
        else:
            await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")
    else:
        await call.message.answer("Вы были забанены.")


@router.callback_query(F.data == "other")
async def callback10(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.other_menu)
    await call.message.answer(
        "Что вас интересует? Подписка даёт доступ к различным функциям, а также к "
        "настройкам поиска собеседников.",
        reply_markup=markup
    )


@router.callback_query(F.data == "replenish")
async def callback11(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Какое количество (10-50000) XCoin вас интересует?")
    await state.set_state(Register.coin)


@router.callback_query(F.data == "subscribe")
async def callback12(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.time_selection_menu)
    await call.message.answer("На сколько?", reply_markup=markup)


@router.callback_query(F.data == "update")
async def callback13(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте описание идеи.")
    await state.set_state(Register.idea)


@router.callback_query(F.data == "friend")
async def callback14(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте ID или username вашего друга. Username должен начинаться с @!")
    await state.set_state(Register.friend_id)


@router.callback_query(F.data == "panel")
async def callback15(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.panel)
    await call.message.answer("Что вас интересует?", reply_markup=markup)


@router.callback_query(F.data == "add_a_superuser")
async def callback16(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите id пользователя, которого вы хотите добавить.")
    await state.set_state(Register.superuser1)


@router.callback_query(F.data == "remove_superuser")
async def callback17(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите id пользователя, которого вы хотите удалить.")
    await state.set_state(Register.superuser2)


@router.callback_query(F.data == "enable")
async def callback18(call: CallbackQuery):
    config.Notify.append(call.message.chat.id)
    await call.message.answer("Вы успешно включили уведомления!")


@router.callback_query(F.data == "turn_off")
async def callback19(call: CallbackQuery):
    ID = call.message.chat.id
    config.Notify = [i for i in config.Notify if i != ID]
    await call.message.answer("Вы успешно выключили уведомления!")


@router.callback_query(F.data == "send_message")
async def callback20(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.sms_sending_buttons)
    await call.message.answer("Кому вы хотите оправить смс?", reply_markup=markup)


@router.callback_query(F.data == "everyone")
async def callback21(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите текст смс.")
    await state.set_state(Register.sms2)


@router.callback_query(F.data == "one_person")
async def callback22(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите id того, кому вы хотите отправить смс.")
    await state.set_state(Register.user_id)


@router.callback_query(F.data == "statistics")
async def callback23(call: CallbackQuery):
    res = len(execute("SELECT * FROM users"))
    markup = InlineKeyboardMarkup(inline_keyboard=kb.statistics_menu)
    await call.message.answer(
        f"Какой промежуток вас интересует?\n"
        f"Всего было зарегистрировано пользователей: {res}\n"
        f"Всего было отправлено сообщений: {messages}",
        reply_markup=markup
    )


@router.callback_query(F.data == "day")
async def callback24(call: CallbackQuery):
    result = statistics()
    await call.message.answer(f"За последний день зарегистрировалось пользователей: {result}.")


@router.callback_query(F.data == "month")
async def callback25(call: CallbackQuery):
    result = statistics(Day=False)
    await call.message.answer(f"За последний месяц зарегистрировалось пользователей: {result}.")


@router.callback_query(F.data == "ideas")
async def callback26(call: CallbackQuery):
    try:
        result = execute("SELECT * FROM ideas")[-1]
        ideas_menu = [
            [InlineKeyboardButton(text="Ещё", callback_data="more:-1")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=ideas_menu)
        await call.message.answer(f"{result[2]}\n\nДата: {result[0]}\nID: {result[1]}", reply_markup=markup)
    except IndexError:
        await call.message.answer("Извините, ничего не нашлось...")


@router.callback_query(F.data.split(":")[0] == "more")
async def callback27(call: CallbackQuery):
    Index = int(call.data.replace("more:", "")) - 1
    try:
        result = execute("SELECT * FROM ideas")[Index]
        ideas_menu = [
            [InlineKeyboardButton(text="Ещё", callback_data=f"more:{Index}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=ideas_menu)
        await call.message.answer(f"{result[2]}\n\nДата: {result[0]}\nID: {result[1]}", reply_markup=markup)
    except IndexError:
        await call.message.answer("Извините, больше ничего не нашлось...")


@router.callback_query(F.data == "send_coins")
async def callback28(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Кому вы хотите отправить монеты?")
    await state.set_state(Register.send_coins)


@router.callback_query(F.data == "ban")
async def callback29(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте ID человека, которого вы хотите забанить.")
    await state.set_state(Register.user_id2)


@router.callback_query(F.data == "unban")
async def callback30(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте ID человека, которого вы хотите разбанить.")
    await state.set_state(Register.user_id3)


@router.callback_query(F.data == "INFO")
async def callback31(call: CallbackQuery):
    await call.message.answer("Вы можете пользоваться всеми функциями полностью бесплатно.")


@router.callback_query(F.data.split(":")[0] == "d")
async def callback32(call: CallbackQuery):
    days = int(call.data.split(":")[1])
    if days == 2:
        count = 30
    elif days == 30:
        count = 50
    elif days == 90:
        count = 120
    else:
        count = 450
    Res = execute("SELECT messages, user_id FROM user_ratings")
    List = sorted(Res, key=lambda x: x[0], reverse=True)
    Res = False
    value = 1
    if List[0][0] >= 200:
        List = List[:10]
        for i, v in enumerate(List):
            if v[1] == call.message.chat.id:
                Res = True
                value = i + 1
                break
    Res2 = date_check(call.message.chat.id)
    if Res and (Res2 is None or Res2 == -1):
        date = str(datetime.datetime.now().date())
        days = 90 if value <= 5 else 30
        if Res2 is not None:
            execute(
                "UPDATE subscribers SET date = ?, days = ? WHERE user_id = ?",
                VALUES=(date, days, call.message.chat.id)
            )
        else:
            execute(
                "INSERT INTO subscribers VALUES(?, ?, ?)", VALUES=(call.message.chat.id, date, days)
            )
        if days == 90:
            await call.message.answer(
                "Вы попали в топ-5 пользователей! Вам было начислено 90 дней подписки!"
            )
        else:
            await call.message.answer(
                "Вы попали в топ-10 пользователей! Вам было начислено 30 дней подписки!"
            )
    elif coin_check(call.message.chat.id, qty=count) == 0:
        date = str(datetime.datetime.now().date())
        res = date_check(call.message.chat.id)
        if res is not None:
            days = days + res if res > 0 else days
            execute(
                "UPDATE subscribers SET date = ?, days = ? WHERE user_id = ?",
                VALUES=(date, days, call.message.chat.id)
            )
        else:
            execute(
                "INSERT INTO subscribers VALUES(?, ?, ?)", VALUES=(call.message.chat.id, date, days)
            )
        await call.message.answer("Готово!")
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=kb.button)
        await call.message.answer(
            "Пополните баланс для продления подписки на соответствующую сумму. "
            "Если вы попали в топ-10 пользователей, то вам нужно подождать, пока "
            "истечёт срок вашей подписки.",
            reply_markup=markup
        )


@router.callback_query(F.data.split(":")[0] == "Yes")
async def callback33(call: CallbackQuery, state: FSMContext):
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True)
    if res is None:
        try:
            data = await state.get_data()
            await state.clear()
            ID = call.message.chat.id
            date = str(datetime.datetime.now().date())
            Name = data["name"]
            description = data["description"]
            photo = data["photo"]
            category = data["category"]
            Type = int(data["type"])
            execute(
                "INSERT INTO groups2 VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                VALUES=(ID, date, Type, Name, description, photo, category, 0,)
            )

            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Принять", callback_data=f"accept:{Name}:{ID}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"reject:{Name}:{ID}")
            )
            image = FSInputFile(photo)
            for k, v in config.admins.items():
                await bot.send_photo(
                    v, image,
                    caption=f"Здравствуйте! Пользователь с ID {ID} решил добавить группу с этими данными:\n"
                            f"Название: {Name}\n"
                            f"Описание: {description}\n"
                            f"Категория: {category}\n"
                            f"Тип: {'Публичная' if Type == 0 else 'Приватная'}",
                    reply_markup=builder.as_markup()
                )
            await call.message.answer(
                "Вы успешно указали все данные! "
                "Подождите, пока модератор проверит эти данные."
            )
        except KeyError:
            await call.message.answer("Эта кнопка больше не работает!")
    else:
        await call.message.answer("Вы были забанены.")


@router.callback_query(F.data.split(":")[0] == "accept")
async def callback34(call: CallbackQuery):
    data = call.data.split(":")
    res = execute("SELECT * FROM groups2 WHERE name = ?", VALUES=(data[1],), one=True)
    if res is not None:
        execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?, ?, ?)", res)
        execute("DELETE FROM groups2 WHERE name = ?", VALUES=(data[1],))
        await call.message.answer(f"Вы успешно добавили группу с названием '{data[1]}'!")
        await bot.send_message(int(data[2]), f"Вы успешно добавили группу!")
    else:
        await call.message.answer("Этой группы нет в базе данных!")


@router.callback_query(F.data.split(":")[0] == "reject")
async def callback35(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")
    await state.update_data(Name2=data[1])
    await state.update_data(ID=int(data[2]))
    await call.message.answer("По какой причине?")
    await state.set_state(Register.reason2)


@router.callback_query(F.data.split(":")[0] == "report")
async def callback36(call: CallbackQuery):
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True)
    if res is None:
        number = 0 if call.message.chat.id not in number_of_complaints else \
            number_of_complaints[call.message.chat.id]
        if time.time() - number >= 300:
            ID = call.data.split(":")[1]
            username = call.data.replace(f"report:{ID}:", "")
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Забанить", callback_data=f"Ban:{ID}"))
            try:
                for k, v in config.admins.items():
                    await bot.send_message(
                        v,
                        f"Пользователь с ID <code>{call.message.chat.id}</code> оставил "
                        f"жалобу на пользователя с ID <code>{ID}</code> и username @{username}.\n"
                        f"Ему пришло это сообщение:"
                    )
                    await send2(v, call.message, markup=builder.as_markup())
            except Exception:
                for k, v in config.admins.items():
                    await bot.send_message(
                        v,
                        f"Пользователь с ID {call.message.chat.id} оставил "
                        f"жалобу на пользователя с ID {ID} и username @{username}.\n"
                        f"Ему пришло это сообщение:", parse_mode=None
                    )
                    await send2(v, call.message, markup=builder.as_markup())
            await call.answer("Спасибо!")
            await call.message.edit_reply_markup()
            number_of_complaints[call.message.chat.id] = time.time()
        else:
            await call.message.answer(
                "Пожалуйста, подождите, пока пройдёт 5 минут с момента последней вашей жалобы."
            )
    else:
        await call.message.answer("Вы были забанены.")


@router.callback_query(F.data.split(":")[0] == "more_groups")
async def callback37(call: CallbackQuery):
    try:
        Index = int(call.data.split(":")[1]) + 1
        category = call.data.split(":")[2]
        List = []
        Res = execute(
            "SELECT name FROM groups WHERE category = ? AND type = 0", VALUES=(category,)
        )
        for Name in Res:
            Res2 = execute("SELECT * FROM group_subscribers WHERE name = ?", VALUES=(Name[0],))
            List.append({"name": Name[0], "number": len(Res2)})
        sorted_list = sorted(List, reverse=True, key=lambda x: x["number"])
        subscribers = sorted_list[Index]["number"]
        Name = sorted_list[Index]["name"]
        res = execute("SELECT * FROM groups WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        description = res[4]
        photo = res[5]
        views = res[7]

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Вступить", callback_data=f"join:{Name}"))
        builder.row(InlineKeyboardButton(text="Ещё", callback_data=f"more_groups:{Index}:{category}"))

        image = FSInputFile(photo)
        await call.message.answer_photo(
            photo=image,
            caption=f"{Name}\n\n{description}\n\n"
                    f"Количество подписчиков: {subscribers}\n"
                    f"Количество просмотров: {views}\n"
                    f"Дата создания: {date.split(' ')[0]}",
            reply_markup=builder.as_markup()
        )
        execute("UPDATE groups SET views = ? WHERE Name = ?", VALUES=(views + 1, Name,))
    except IndexError:
        await call.message.answer("Извините, ничего не нашлось...")


@router.callback_query(F.data.split(":")[0] == "join")
async def callback38(call: CallbackQuery):
    Name = call.data.split(":")[1]
    res = execute("SELECT type FROM groups WHERE name = ?", VALUES=(Name,), one=True)
    if res is not None:
        if date_check(call.message.chat.id) is not None and date_check(call.message.chat.id) != -1 \
                or res[0] == 1:
            if match_check(call.message.chat.id):
                UserID = call.message.chat.id
                if execute(
                    "SELECT * FROM group_subscribers WHERE name = ? AND user_id = ?",
                    VALUES=(Name, UserID,), one=True
                ) is None:
                    execute(
                        "INSERT INTO group_subscribers VALUES(?, ?)", VALUES=(Name, UserID,)
                    )
                if execute(
                    "SELECT * FROM people WHERE name = ? AND user_id = ?",
                    VALUES=(Name, UserID,), one=True
                ) is None:
                    res = execute("SELECT id FROM people WHERE name = ?", VALUES=(Name,))
                    ID = res[-1][0] + 1 if res else 1
                    execute(
                        "INSERT INTO people VALUES(?, ?, ?)", VALUES=(Name, ID, UserID,)
                    )
                await call.message.answer(
                    "Вы успешно вступили в группу! Вы можете начинать общение! Для выхода введите /stop."
                )
            else:
                await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
            await call.message.answer(
                "У вас нет подписки! Подписка даёт:\n"
                "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
                "2. Функцию установки уникального ника в анонимном чате.\n"
                "3. Функцию удаления сообщений у собеседников.\n"
                "4. Функцию возврата собеседника.\n"
                "Подписку можно получить двумя способами:\n"
                "1. Попасть в топ-10 пользователей.\n"
                "2. Купить.",
                reply_markup=markup
            )
    else:
        await call.message.answer("Извините, этой группы уже не существует...")


@router.callback_query(F.data.split(":")[0] == "Join")
async def callback39(call: CallbackQuery):
    Name = call.data.split(":")[1]
    res = execute("SELECT user_id FROM groups WHERE name = ?", VALUES=(Name,), one=True)
    if res is not None:
        UserID = call.message.chat.id
        builder = InlineKeyboardBuilder()
        Res = execute(
            "SELECT * FROM group_subscribers WHERE name = ? AND user_id = ?",
            VALUES=(Name, UserID,), one=True
        )
        if Res is not None:
            if match_check(call.message.chat.id):
                Res = execute(
                    "SELECT * FROM people WHERE name = ? AND user_id = ?",
                    VALUES=(Name, UserID,), one=True
                )
                if Res is None:
                    res = execute("SELECT id FROM people WHERE name = ?", VALUES=(Name,))
                    ID = res[-1][0] + 1 if res else 1
                    execute(
                        "INSERT INTO people VALUES(?, ?, ?)", VALUES=(Name, ID, UserID,)
                    )
                await call.message.answer(
                    "Вы успешно вступили в группу! Вы можете начинать общение! Для выхода введите /stop."
                )
            else:
                await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")
        else:
            builder.row(
                InlineKeyboardButton(text="Принять", callback_data=f"Accept:{Name}:{UserID}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"Reject:{Name}:{UserID}")
            )
            await bot.send_message(
                res[0], f"Пользователь с ID {UserID} подал заявку на вступление в вашу группу '{Name}'.",
                reply_markup=builder.as_markup()
            )
            await call.message.answer("Заявка на вступление подана!")
    else:
        await call.message.answer("Извините, этой группы уже не существует...")


@router.callback_query(F.data.split(":")[0] == "Accept")
async def callback40(call: CallbackQuery):
    Name = call.data.split(":")[1]
    UserID = int(call.data.split(":")[2])
    if execute(
        "SELECT * FROM group_subscribers WHERE name = ? AND user_id = ?",
        VALUES=(Name, UserID,), one=True
    ) is None:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Начать общение", callback_data=f"join:{Name}"))
        await bot.send_message(
            UserID, "Вы успешно вступили в группу! Вы можете начинать общение!", reply_markup=builder.as_markup()
        )
    await call.message.answer("Успешно!")


@router.callback_query(F.data.split(":")[0] == "Reject")
async def callback41(call: CallbackQuery):
    Name = call.data.split(":")[1]
    UserID = int(call.data.split(":")[2])
    if execute(
        "SELECT * FROM group_subscribers WHERE name = ? AND user_id = ?",
        VALUES=(Name, UserID,), one=True
    ) is None:
        await bot.send_message(UserID, "Ваша заявка была отклонена.")
    await call.message.answer("Успешно!")


@router.callback_query(F.data.split(":")[0] == "code")
async def callback43(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[1]
    await state.update_data(code=code)
    markup = InlineKeyboardMarkup(inline_keyboard=kb.hobby_selection_menu)
    await call.message.answer(
        "Шаг 2/3: Выберите ваше увлечение или ваш род деятельности.", reply_markup=markup
    )


@router.callback_query(F.data.split(":")[0] == "hobby")
async def callback44(call: CallbackQuery, state: FSMContext):
    hobby = int(call.data.split(":")[1])
    await state.update_data(hobby=hobby)
    markup = InlineKeyboardMarkup(inline_keyboard=kb.gender_selection_menu)
    await call.message.answer("Шаг 3/3: Выберите ваш пол.", reply_markup=markup)


@router.callback_query(F.data.split(":")[0] == "gender")
async def callback45(call: CallbackQuery, state: FSMContext):
    try:
        gender = int(call.data.split(":")[1])
        data = await state.get_data()
        await state.clear()
        ID = call.message.chat.id
        if execute("SELECT * FROM profiles WHERE user_id = ?", VALUES=(ID,), one=True) is None:
            execute(
                "INSERT INTO profiles VALUES(?, ?, ?, ?)",
                VALUES=(ID, gender, data["code"], data["hobby"],)
            )
            await call.message.answer(
                "Профиль создан!\nВы указали эти данные:\n"
                f"Пол: {kb.gender[gender]}\n"
                f"Страна: {data['code']}\n"
                f"Хобби: {kb.hobbies[data['hobby']]}"
            )
        else:
            execute(
                "UPDATE profiles SET gender = ?, country_code = ?, hobby = ? WHERE user_id = ?",
                VALUES=(gender, data["code"], data["hobby"], ID,)
            )
            await call.message.answer(
                "Профиль обновлён!\nВы указали эти данные:\n"
                f"Пол: {kb.gender[gender]}\n"
                f"Страна: {data['code']}\n"
                f"Хобби: {kb.hobbies[data['hobby']]}"
            )
    except KeyError:
        await call.message.answer("Пожалуйста, укажите все данные.")


@router.callback_query(F.data.split(":")[0] == "Code")
async def callback46(call: CallbackQuery, state: FSMContext):
    code = call.data.split(":")[1]
    await state.update_data(code=code)
    markup = InlineKeyboardMarkup(inline_keyboard=kb.hobby_selection_menu2)
    await call.message.answer("Шаг 2/3: Выберите увлечение собеседника.", reply_markup=markup)


@router.callback_query(F.data.split(":")[0] == "Hobby")
async def callback47(call: CallbackQuery, state: FSMContext):
    hobby = int(call.data.split(":")[1])
    await state.update_data(hobby=hobby)
    markup = InlineKeyboardMarkup(inline_keyboard=kb.gender_selection_menu2)
    await call.message.answer("Шаг 3/3: Выберите пол собеседника.", reply_markup=markup)


@router.callback_query(F.data.split(":")[0] == "Gender")
async def callback48(call: CallbackQuery, state: FSMContext):
    try:
        gender = int(call.data.split(":")[1])
        data = await state.get_data()
        await state.clear()
        ID = call.message.chat.id
        if execute("SELECT * FROM profiles2 WHERE user_id = ?", VALUES=(ID,), one=True) is None:
            if data["hobby"] == -1:
                for i in range(len(kb.hobbies) - 1):
                    execute(
                        "INSERT INTO profiles2 VALUES(?, ?, ?, ?)",
                        VALUES=(ID, gender, data["code"], i,)
                    )
            else:
                execute(
                    "INSERT INTO profiles2 VALUES(?, ?, ?, ?)",
                    VALUES=(ID, gender, data["code"], data["hobby"],)
                )
            await call.message.answer(
                f"Вы успешно указали все данные!\nВы указали эти данные:\n"
                f"Пол: {kb.gender[gender]}\n"
                f"Страна: {data['code']}\n"
                f"Хобби: {kb.hobbies[data['hobby']]}\n\n"
                f"Функция настройки поиска себеседников пока работает только в чате 1 на 1."
            )
        else:
            execute("DELETE FROM profiles2 WHERE user_id = ?", VALUES=(ID,))
            if data["hobby"] == -1:
                for i in range(len(kb.hobbies) - 1):
                    execute(
                        "INSERT INTO profiles2 VALUES(?, ?, ?, ?)",
                        VALUES=(ID, gender, data["code"], i,)
                    )
            else:
                execute(
                    "INSERT INTO profiles2 VALUES(?, ?, ?, ?)",
                    VALUES=(ID, gender, data["code"], data["hobby"],)
                )
            await call.message.answer(
                "Вы успешно обновили все данные!\nВы указали эти данные:\n"
                f"Пол: {kb.gender[gender]}\n"
                f"Страна: {data['code']}\n"
                f"Хобби: {kb.hobbies[data['hobby']]}"
            )
    except KeyError:
        await call.message.answer("Пожалуйста, укажите все данные.")


@router.callback_query(F.data.split(":")[0] == "Ban")
async def callback49(call: CallbackQuery):
    ID = int(call.data.split(":")[1])
    if execute("SELECT * FROM users WHERE user_id = %d" % (ID,), one=True) is not None:
        date = str(datetime.datetime.now())
        days = -1
        execute("INSERT INTO banned_users VALUES(?, ?, ?)", (date, days, ID,))
        try:
            await bot.send_message(ID, "Вы были забанены из-за ваших сообщений в чате.")
        except Exception:
            pass
        await call.answer("Готово!")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Разбанить", callback_data=f"Unban:{ID}"))
        await call.message.edit_reply_markup(reply_markup=builder.as_markup())
    else:
        await call.answer("Этого пользователя нет в базе данных!")


@router.callback_query(F.data == "add_work")
async def callback50(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте название вашей работы.")
    await state.set_state(Register.work_name)


@router.callback_query(F.data == "voting_group")
async def callback51(call: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=kb.groups)
    await call.message.answer(
        "Выберите в чьём каталоге вы хотите проголосовать или найдите работу по названию.",
        reply_markup=markup
    )


@router.callback_query(F.data == "artist_works")
async def callback52(call: CallbackQuery):
    try:
        List = []
        Res = execute("SELECT name FROM works WHERE type = 0")
        for Name in Res:
            Res2 = execute("SELECT rating FROM stars WHERE name = ?", VALUES=(Name[0],))
            rating = 0
            for i in Res2:
                rating += i[0]
            rating = rating / len(Res2) if rating > 0 else 0
            List.append({"name": Name[0], "rating": rating})
        List2 = list(reversed(List))
        Name = List2[0]["name"]
        res = execute("SELECT * FROM works WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        file = res[5]
        views = res[6]
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="1 ⭐", callback_data=f"1:star:{Name}"),
            InlineKeyboardButton(text="2 ⭐", callback_data=f"2:star:{Name}"),
            InlineKeyboardButton(text="3 ⭐", callback_data=f"3:star:{Name}"),
            InlineKeyboardButton(text="4 ⭐", callback_data=f"4:star:{Name}"),
            InlineKeyboardButton(text="5 ⭐", callback_data=f"5:star:{Name}")
        )
        builder.row(InlineKeyboardButton(text="Ещё", callback_data=f"more_works:0:0"))
        rating = List2[0]["rating"]
        image = FSInputFile(file)
        await call.message.answer_photo(
            photo=image,
            caption=f"{Name}\n\n"
                    f"{f'Рейтинг: {rating} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                    f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
            reply_markup=builder.as_markup()
        )
        execute("UPDATE works SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except IndexError:
        await call.message.answer("Извините, ничего не нашлось...")


@router.callback_query(F.data == "musicians")
async def callback54(call: CallbackQuery):
    try:
        List = []
        Res = execute("SELECT name FROM works WHERE type = 1")
        for Name in Res:
            Res2 = execute("SELECT rating FROM stars WHERE name = ?", VALUES=(Name[0],))
            rating = 0
            for i in Res2:
                rating += i[0]
            rating = rating / len(Res2) if rating > 0 else 0
            List.append({"name": Name[0], "rating": rating})
        List2 = list(reversed(List))
        Name = List2[0]["name"]
        res = execute("SELECT * FROM works WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        file = res[5]
        views = res[6]
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="1 ⭐", callback_data=f"1:star:{Name}"),
            InlineKeyboardButton(text="2 ⭐", callback_data=f"2:star:{Name}"),
            InlineKeyboardButton(text="3 ⭐", callback_data=f"3:star:{Name}"),
            InlineKeyboardButton(text="4 ⭐", callback_data=f"4:star:{Name}"),
            InlineKeyboardButton(text="5 ⭐", callback_data=f"5:star:{Name}")
        )
        builder.row(InlineKeyboardButton(text="Ещё", callback_data=f"more_works:0:1"))
        rating = List2[0]["rating"]
        audio = FSInputFile(file)
        await call.message.answer_audio(
            audio=audio,
            caption=f"{Name}\n\n"
                    f"{f'Рейтинг: {rating} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                    f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
            reply_markup=builder.as_markup()
        )
        execute("UPDATE works SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except IndexError:
        await call.message.answer("Извините, ничего не нашлось...")


@router.callback_query(F.data.split(":")[0] == "more_works")
async def callback53(call: CallbackQuery):
    try:
        Index = int(call.data.split(":")[1]) + 1
        category = int(call.data.split(":")[2])
        List = []
        Res = execute("SELECT name FROM works WHERE type = ?", VALUES=(category,))
        for Name in Res:
            Res2 = execute("SELECT rating FROM stars WHERE name = ?", VALUES=(Name[0],))
            rating = 0
            for i in Res2:
                rating += i[0]
            rating = rating / len(Res2) if rating > 0 else 0
            List.append({"name": Name[0], "rating": rating})
        List2 = list(reversed(List))
        Name = List2[Index]["name"]
        res = execute("SELECT * FROM works WHERE name = ?", VALUES=(Name,), one=True)
        date = res[1]
        file = res[5]
        views = res[6]
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="1 ⭐", callback_data=f"1:star:{Name}"),
            InlineKeyboardButton(text="2 ⭐", callback_data=f"2:star:{Name}"),
            InlineKeyboardButton(text="3 ⭐", callback_data=f"3:star:{Name}"),
            InlineKeyboardButton(text="4 ⭐", callback_data=f"4:star:{Name}"),
            InlineKeyboardButton(text="5 ⭐", callback_data=f"5:star:{Name}")
        )
        builder.row(InlineKeyboardButton(text="Ещё", callback_data=f"more_works:{Index}:{category}"))
        rating = List2[Index]["rating"]
        file = FSInputFile(file)
        if category == 0:
            await call.message.answer_photo(
                photo=file,
                caption=f"{Name}\n\n"
                        f"{f'Рейтинг: {rating} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                        f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
                reply_markup=builder.as_markup()
            )
        else:
            await call.message.answer_audio(
                audio=file,
                caption=f"{Name}\n\n"
                        f"{f'Рейтинг: {rating} ⭐' if rating > 0 else 'Оценок пока не было'}\n"
                        f"Кол-во просмотров: {views}\nДата публикации: {date.split(' ')[0]}",
                reply_markup=builder.as_markup()
            )
        execute("UPDATE works SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
    except IndexError:
        await call.message.answer("Извините, ничего не нашлось...")


@router.callback_query(F.data.split(":")[1] == "star")
async def callback55(call: CallbackQuery):
    data = call.data.split(":")
    stars = int(data[0])
    ID = call.message.chat.id
    Name = data[2]
    res = execute("SELECT user_id FROM works WHERE name = ?", VALUES=(Name,), one=True)[0]
    if res != ID or ID in config.admins:
        if execute("SELECT * FROM stars WHERE user_id = ? AND name = ?", VALUES=(ID, Name), one=True) is None:
            execute("INSERT INTO stars VALUES(?, ?, ?)", VALUES=(Name, ID, stars))
        else:
            execute("UPDATE stars SET rating = ? WHERE user_id = ? AND name = ?", VALUES=(stars, ID, Name))
        await call.answer("Оценка оставлена!")
    else:
        await call.answer("Вы не можете оставить оценку!")


@router.callback_query(F.data == "NameSearch")
async def callback56(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте точное название работы.")
    await state.set_state(Register.work_name2)


@router.callback_query(F.data == "Yes2")
async def callback57(call: CallbackQuery, state: FSMContext):
    res = execute("SELECT * FROM banned_users WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True)
    if res is None:
        try:
            data = await state.get_data()
            await state.clear()
            ID = call.message.chat.id
            date = str(datetime.datetime.now().date())
            Name = data["name"]
            description = None
            file = data["file"]
            Type = int(data["type"])
            execute(
                "INSERT INTO works2 VALUES(?, ?, ?, ?, ?, ?, ?)",
                VALUES=(ID, date, Type, Name, description, file, 0,)
            )
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Принять", callback_data=f"a:{Name}:{ID}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"r:{Name}:{ID}")
            )
            file = FSInputFile(file)
            if Type == 0:
                for k, v in config.admins.items():
                    await bot.send_photo(
                        v, file,
                        caption=f"Здравствуйте! Пользователь с ID {ID} решил добавить работу с этими данными:\n"
                                f"Название: {Name}",
                        reply_markup=builder.as_markup()
                    )
            else:
                for k, v in config.admins.items():
                    await bot.send_audio(
                        v, file,
                        caption=f"Здравствуйте! Пользователь с ID {ID} решил добавить работу с этими данными:\n"
                                f"Название: {Name}",
                        reply_markup=builder.as_markup()
                    )
            await call.message.answer(
                "Вы успешно указали все данные! "
                "Подождите, пока модератор проверит эти данные."
            )
        except KeyError:
            await call.message.answer("Эта кнопка больше не работает!")
    else:
        await call.message.answer("Вы были забанены.")


@router.callback_query(F.data.split(":")[0] == "a")
async def callback58(call: CallbackQuery):
    data = call.data.split(":")
    res = execute("SELECT * FROM works2 WHERE name = ?", VALUES=(data[1],), one=True)
    if res is not None:
        execute("INSERT INTO works VALUES(?, ?, ?, ?, ?, ?, ?)", res)
        execute("DELETE FROM works2 WHERE name = ?", VALUES=(data[1],))
        await call.message.answer(f"Вы успешно добавили работу с названием '{data[1]}'!")
        await bot.send_message(int(data[2]), "Вы успешно добавили свою работу!")
    else:
        await call.message.answer("Этой работы нет в базе данных!")


@router.callback_query(F.data.split(":")[0] == "r")
async def callback59(call: CallbackQuery):
    data = call.data.split(":")
    try:
        res = execute("SELECT file FROM works2 WHERE name = ?", VALUES=(data[1],), one=True)
        if res is not None:
            execute("DELETE FROM works2 WHERE name = ?", VALUES=(data[1],))
            os.remove(res[0])
            await call.message.answer("Успешно!")
            await bot.send_message(int(data[2]), f"Ваша работа не прошла проверку.")
        else:
            await call.message.answer("Этой работы нет в базе данных!")
    except Exception as EX:
        await call.message.answer(str(EX))


@router.callback_query(F.data.split(":")[0] == "delete")
async def callback60(call: CallbackQuery):
    Name = call.data.split(":")[1]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Подтверждаю", callback_data=f"delete2:{Name}"))
    await call.message.answer(
        "Вы подтверждаете удаление своей работы? Если нет, то никуда не нажимайте.",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.split(":")[0] == "delete2")
async def callback61(call: CallbackQuery):
    Name = call.data.split(":")[1]
    res = execute("SELECT file FROM works WHERE name = ?", VALUES=(Name,), one=True)
    execute("DELETE FROM works WHERE name = ?", VALUES=(Name,))
    os.remove(res[0])
    await call.message.answer("Вы успешно удалили свою работу!")


@router.callback_query(F.data == "mailing")
async def callback62(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте рекламный пост.")
    await state.set_state(Register.mailing)


@router.callback_query(F.data.split(":")[0] == "delete_message")
async def callback63(call: CallbackQuery):
    data = call.data.split(":")
    try:
        index = int(data[1])
        List = messages2[str(call.message.chat.id)][index]
        messages2[str(call.message.chat.id)].pop(index)
        for m in List:
            try:
                await bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
            except Exception:
                pass
        await call.message.edit_text("Вы успешно удалили это сообщение у собеседников!")
    except Exception:
        await call.message.edit_reply_markup()
        await call.message.edit_text("Извините, произошла ошибка.")


@router.callback_query(F.data.split(":")[0] == "other_message")
async def callback64(call: CallbackQuery):
    data = call.data.split(":")
    index = int(data[1]) - 1
    try:
        if date_check(call.message.chat.id) is not None \
                and date_check(call.message.chat.id) != -1:
            List = [] if str(call.message.chat.id) not in messages2 else \
                messages2[str(call.message.chat.id)]
            if List:
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"delete_message:{index}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"other_message:{index}")
                )
                List2 = List[index]
                await send2(call.message.chat.id, List2[0])
                await call.message.answer("Вы хотите удалить это сообщение?", reply_markup=builder.as_markup())
            else:
                await call.message.answer("Вы не отправили нужное количество сообщений!")
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
            await call.message.answer(
                "У вас нет подписки! Подписка даёт:\n"
                "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
                "2. Функцию установки уникального ника в анонимном чате.\n"
                "3. Функцию удаления сообщений у собеседников.\n"
                "Подписку можно получить двумя способами:\n"
                "4. Функцию возврата собеседника.\n"
                "1. Попасть в топ-10 пользователей.\n"
                "2. Купить.",
                reply_markup=markup
            )
    except Exception:
        await call.message.answer("Извините, больше не нашлось ваших сообщений.")


@router.callback_query(F.data.split(":")[0] == "score")
async def callback65(call: CallbackQuery):
    try:
        data = call.data.split(":")
        chat_id = int(data[1])
        res = execute("SELECT score FROM user_ratings WHERE user_id = ?", VALUES=(chat_id,), one=True)[0]
        score = int(data[2]) + res
        execute("UPDATE user_ratings SET score = ? WHERE user_id = ?", VALUES=(score, chat_id,))
    except Exception:
        pass
    markup = InlineKeyboardMarkup(inline_keyboard=kb.menu2)
    await call.message.edit_text(
        "Вы успешно оценили собеседника! Что вас интересует?", reply_markup=markup
    )


@router.callback_query(F.data.split(":")[0] == "request")
async def callback66(call: CallbackQuery):
    if match_check(call.message.chat.id):
        data = call.data.split(":")
        ID = int(data[1])
        if match_check(ID):
            Name = execute(
                "SELECT user_nickname FROM chats WHERE user_id = ? AND id_interlocutor = ?",
                VALUES=(ID, call.message.chat.id,), one=True
            )
            try:
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"Request:{call.message.chat.id}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"cancel:{call.message.chat.id}")
                )
                builder.row(
                    InlineKeyboardButton(
                        text="Нет, заблокировать", callback_data=f"block:{call.message.chat.id}"
                    )
                )
                await bot.send_message(
                    ID, f"Вы хотите продолжить диалог с {Name[0]}? Если вы нажмёте на кнопку "
                        f"'Нет, заблокировать', то {Name[0]} больше не сможет вам отправлять запросы.",
                    reply_markup=builder.as_markup()
                )
                await call.message.edit_text("Вы успешно отправили запрос!")
            except Exception:
                await call.message.edit_text("Произошла ошибка, возможно, собеседник удалил чат с ботом.")
        else:
            await call.message.answer("Извините, этот пользователь занят.")
    else:
        await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")


@router.callback_query(F.data.split(":")[0] == "other_interlocutor")
async def callback67(call: CallbackQuery):
    try:
        Index = int(call.data.split(":")[1]) - 1
        if date_check(call.message.chat.id) is None or date_check(call.message.chat.id) == -1:
            res = False
        else:
            res = True
        if res:
            List = execute(
                "SELECT id_interlocutor, user_nickname FROM chats WHERE user_id = ?",
                VALUES=(call.message.chat.id,)
            )
            List = List[Index]
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Да", callback_data=f"request:{List[0]}"),
                InlineKeyboardButton(text="Нет", callback_data=f"other_interlocutor:{Index}")
            )
            await call.message.answer(
                f"Вы хотите продолжить разговор с {List[1]}?",
                reply_markup=builder.as_markup()
            )
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
            await call.message.answer(
                "У вас нет подписки! Подписка даёт:\n"
                "1. Функцию настройки поиска собеседников по трём критериям (пол, страна и увлечения).\n"
                "2. Функцию установки уникального ника в анонимном чате.\n"
                "3. Функцию удаления сообщений у собеседников.\n"
                "4. Функцию возврата собеседника.\n"
                "Подписку можно получить двумя способами:\n"
                "1. Попасть в топ-10 пользователей.\n"
                "2. Купить.",
                reply_markup=markup
            )
    except IndexError:
        await call.message.answer("Извините, больше не нашлось ваших чатов.")


@router.callback_query(F.data.split(":")[0] == "Request")
async def callback68(call: CallbackQuery):
    if match_check(call.message.chat.id):
        data = call.data.split(":")
        ID = int(data[1])
        if match_check(ID):
            execute("INSERT INTO persons VALUES(?, ?)", VALUES=(ID, call.message.chat.id,))
            try:
                await bot.send_message(
                    ID,
                    "Собеседник одобрил ваш запрос! Вы можете начать общение!"
                )
                await call.message.edit_reply_markup()
                await call.message.edit_text("Вы можете начать общение!")
            except Exception:
                await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")
        else:
            await call.message.answer("Извините, этот пользователь уже занят.")
    else:
        await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")


@router.callback_query(F.data.split(":")[0] == "cancel")
async def callback69(call: CallbackQuery):
    data = call.data.split(":")
    ID = int(data[1])
    try:
        await bot.send_message(
            ID,
            "Собеседник отклонил ваш запрос."
        )
        await call.message.edit_text("Вы успешно отклонили запрос!")
    except Exception:
        await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")


@router.callback_query(F.data.split(":")[0] == "block")
async def callback70(call: CallbackQuery):
    data = call.data.split(":")
    ID = int(data[1])
    ID2 = call.message.chat.id
    execute("DELETE FROM chats WHERE user_id = ? AND id_interlocutor = ?", VALUES=(ID, ID2))
    execute("DELETE FROM chats WHERE user_id = ? AND id_interlocutor = ?", VALUES=(ID2, ID))
    try:
        await bot.send_message(
            ID, "Собеседник вас заблокировал, вы больше не сможете отправлять ему запросы."
        )
        await call.message.edit_reply_markup()
        await call.message.edit_text(
            "Вы успешно заблокировали собеседника, он больше не сможет отправлять вам запросы."
        )
    except Exception:
        await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")


@router.callback_query(F.data.split(":")[0] == "add")
async def callback71(call: CallbackQuery):
    try:
        chat_id = int(call.data.split(":")[1])
        res = execute(
            "SELECT id FROM random_people WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
        )
        res2 = execute(
            "SELECT id FROM random_person WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
        )
        ID = res[0] if res is not None else res2[0]
        Name = execute(
            "SELECT name FROM usernames WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
        )
        Name = f'пользователя №{ID}' if Name is None else Name[0]
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Да", callback_data=f"Add:{call.message.chat.id}"),
            InlineKeyboardButton(text="Нет", callback_data=f"cancel:{call.message.chat.id}")
        )
        await bot.send_message(
            chat_id, f"Вы хотите добавить в друзья {Name}?", reply_markup=builder.as_markup()
        )
        execute("INSERT INTO friends4 VALUES(?, ?)", VALUES=(call.message.chat.id, chat_id,))
        await call.message.edit_text("Вы успешно отправили запрос!")
    except Exception:
        await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")


@router.callback_query(F.data.split(":")[0] == "Add")
async def callback72(call: CallbackQuery):
    try:
        chat_id = int(call.data.split(":")[1])
        result = execute(
            "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
            VALUES=(call.message.chat.id, chat_id), one=True
        )
        result2 = execute(
            "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
            VALUES=(chat_id, call.message.chat.id), one=True
        )
        if result is None and result2 is None:
            execute(
                "DELETE FROM friends4 WHERE user_id = ? AND friend_id = ?",
                VALUES=(chat_id, call.message.chat.id,)
            )
            res = execute(
                "SELECT id FROM random_person WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
            )
            res2 = execute(
                "SELECT id FROM random_people WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
            )
            res3 = execute(
                "SELECT * FROM persons WHERE id_interlocutor = ?", VALUES=(chat_id,), one=True
            )
            res4 = execute(
                "SELECT * FROM persons WHERE user_id = ?", VALUES=(chat_id,), one=True
            )
            Res = False
            if res is not None:
                ID = res[0]
                Id = ID + 1 if ID % 2 != 0 else ID - 1
                ID2 = execute("SELECT user_id FROM random_person WHERE id = ?", VALUES=(Id,), one=True)
                if ID2 is not None:
                    if ID2[0] == chat_id:
                        Name = execute(
                            "SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True
                        )
                        Name2 = f'Пользователь №{Id}' if Name is None else Name[0]
                        execute(
                            "INSERT INTO friends3 VALUES(?, ?, ?)",
                            VALUES=(call.message.chat.id, chat_id, Name2,)
                        )
                        Name3 = f'пользователя №{Id}' if Name is None else Name[0]
                        Res = True
                        await call.message.edit_text(f"Вы успешно добавили в друзья {Name3}!")
                        Name = execute(
                            "SELECT name FROM usernames WHERE user_id = ?",
                            VALUES=(call.message.chat.id,), one=True
                        )
                        Name2 = f'Пользователь №{ID}' if Name is None else Name[0]
                        execute(
                            "INSERT INTO friends3 VALUES(?, ?, ?)",
                            VALUES=(chat_id, call.message.chat.id, Name2,)
                        )
                        Name3 = f'пользователя №{ID}' if Name is None else Name[0]
                        await bot.send_message(chat_id, f"Вы успешно добавили в друзья {Name3}!")
            if res2 is not None:
                ID = res2[0]
                ID2 = ID
                while ID2 % 10 != 0:
                    ID2 += 1
                value = False
                Id = None
                for _ in range(10):
                    if ID2 != ID:
                        try:
                            ID3 = execute(
                                "SELECT user_id FROM random_people WHERE id = ?",
                                VALUES=(ID2,), one=True
                            )[0]
                            if ID3 == chat_id:
                                Id = ID2
                                value = True
                        except Exception:
                            pass
                    ID2 -= 1
                if value:
                    Name = execute(
                        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(chat_id,), one=True
                    )
                    Name2 = f'Пользователь №{Id}' if Name is None else Name[0]
                    execute(
                        "INSERT INTO friends3 VALUES(?, ?, ?)", VALUES=(call.message.chat.id, chat_id, Name2,)
                    )
                    Name3 = f'пользователя №{Id}' if Name is None else Name[0]
                    Res = True
                    await call.message.edit_text(f"Вы успешно добавили в друзья {Name3}!")
                    Name = execute(
                        "SELECT name FROM usernames WHERE user_id = ?", VALUES=(call.message.chat.id,), one=True
                    )
                    Name2 = f'Пользователь №{ID}' if Name is None else Name[0]
                    execute(
                        "INSERT INTO friends3 VALUES(?, ?, ?)", VALUES=(chat_id, call.message.chat.id, Name2,)
                    )
                    Name3 = f'пользователя №{ID}' if Name is None else Name[0]
                    await bot.send_message(chat_id, f"Вы успешно добавили в друзья {Name3}!")
            if res3 is not None or res4 is not None:
                ID = res3[1] if res3 is not None else res4[0]
                Name = execute(
                    "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                    VALUES=(ID, call.message.chat.id,), one=True
                )[0]
                execute(
                    "INSERT INTO friends3 VALUES(?, ?, ?)", VALUES=(call.message.chat.id, chat_id, Name,)
                )
                Res = True
                await call.message.edit_text(f"Вы успешно добавили в друзья {Name}!")
                Name = execute(
                    "SELECT user_nickname FROM chats WHERE id_interlocutor = ? AND user_id = ?",
                    VALUES=(call.message.chat.id, ID,), one=True
                )[0]
                execute(
                    "INSERT INTO friends3 VALUES(?, ?, ?)", VALUES=(chat_id, call.message.chat.id, Name,)
                )
                await bot.send_message(chat_id, f"Вы успешно добавили в друзья {Name}!")
            if not Res:
                await call.message.edit_text("Вы не можете добавить этого человека в друзья.")
        else:
            await call.message.edit_text("Вы уже добавили этого человека в друзья.")
    except Exception:
        await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")


@router.callback_query(F.data.split(":")[0] == "rename")
async def callback73(call: CallbackQuery, state: FSMContext):
    ID = int(call.data.split(":")[1])
    await state.update_data(ID=ID)
    await state.set_state(Register.friend_name)
    await call.message.answer("Отправьте новый ник.")


@router.callback_query(F.data.split(":")[0] == "delete_friend")
async def callback74(call: CallbackQuery):
    ID = int(call.data.split(":")[1])
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Да", callback_data=f"delete_friend2:{ID}"))
    await call.message.answer(
        "Вы подтверждаете удаление вашего друга?",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.split(":")[0] == "delete_friend2")
async def callback75(call: CallbackQuery):
    try:
        ID = int(call.data.split(":")[1])
        Res = execute(
            "SELECT * FROM friends3 WHERE user_id = ? AND friend_id = ?",
            VALUES=(call.message.chat.id, ID), one=True
        )
        if Res is not None:
            execute(
                "DELETE FROM friends3 WHERE user_id = ? AND friend_id = ?",
                VALUES=(call.message.chat.id, ID,)
            )
            execute(
                "DELETE FROM friends3 WHERE friend_id = ? AND user_id = ?",
                VALUES=(call.message.chat.id, ID,)
            )
            await bot.send_message(ID, "Ваш друг удалил вас из друзей.")
            await call.message.edit_text("Вы успешно удалили своего друга.")
        else:
            await call.message.edit_text("Вы уже удалили этого друга.")
    except Exception:
        await call.message.answer("Произошла ошибка, возможно, собеседник удалил чат с ботом.")


@router.callback_query(F.data.split(":")[0] == "next")
async def callback76(call: CallbackQuery):
    try:
        Index = int(call.data.split(":")[1]) + 1
        Friends = execute(
            "SELECT friend_id, friend_name FROM friends3 WHERE user_id = ?",
            VALUES=(call.message.chat.id,)
        )
        friend = Friends[Index]
        FriendId = friend[0]
        FriendName = friend[1]
        if Index + 1 < len(Friends):
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
            builder.row(
                InlineKeyboardButton(text="⬅", callback_data=f"back:{Index}"),
                InlineKeyboardButton(text="➡", callback_data=f"next:{Index}")
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
            builder.row(
                InlineKeyboardButton(text="⬅", callback_data=f"back:{Index}")
            )
        res = execute(
            "SELECT * FROM user_ratings WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        Profile = execute(
            "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        await call.message.edit_text(
            f"Имя: {FriendName}\n\n"
            f"Рейтинг:\n{res[1]}\n"
            f"Количество начатых чатов:\n{res[3]}\n"
            f"Количество отправленных сообщений:\n{res[2]}\n"
            f"Пол: {kb.gender[Profile[0]]}\n"
            f"Страна: {Profile[1]}\n"
            f"Хобби: {kb.hobbies[Profile[2]]}", reply_markup=builder.as_markup()
        )
    except Exception:
        await call.message.edit_reply_markup()


@router.callback_query(F.data.split(":")[0] == "back")
async def callback77(call: CallbackQuery):
    try:
        Index = int(call.data.split(":")[1]) - 1
        Friends = execute(
            "SELECT friend_id, friend_name FROM friends3 WHERE user_id = ?",
            VALUES=(call.message.chat.id,)
        )
        friend = Friends[Index]
        FriendId = friend[0]
        FriendName = friend[1]
        if Index > 0:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
            builder.row(
                InlineKeyboardButton(text="⬅", callback_data=f"back:{Index}"),
                InlineKeyboardButton(text="➡", callback_data=f"next:{Index}")
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="💬 Продолжить общение", callback_data=f"request2:{FriendId}")),
            builder.row(InlineKeyboardButton(text="🗑 Удалить из списка", callback_data=f"delete_friend:{FriendId}"))
            builder.row(InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename:{FriendId}"))
            builder.row(
                InlineKeyboardButton(text="➡", callback_data=f"next:{Index}")
            )
        res = execute(
            "SELECT * FROM user_ratings WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        Profile = execute(
            "SELECT gender, country_code, hobby FROM profiles WHERE user_id = ?",
            VALUES=(FriendId,), one=True
        )
        await call.message.edit_text(
            f"Имя: {FriendName}\n\n"
            f"Рейтинг:\n{res[1]}\n"
            f"Количество начатых чатов:\n{res[3]}\n"
            f"Количество отправленных сообщений:\n{res[2]}\n"
            f"Пол: {kb.gender[Profile[0]]}\n"
            f"Страна: {Profile[1]}\n"
            f"Хобби: {kb.hobbies[Profile[2]]}", reply_markup=builder.as_markup()
        )
    except Exception:
        await call.message.edit_reply_markup()


@router.callback_query(F.data.split(":")[0] == "request2")
async def callback78(call: CallbackQuery):
    if match_check(call.message.chat.id):
        data = call.data.split(":")
        ID = int(data[1])
        if match_check(ID):
            Name = execute(
                "SELECT friend_name FROM friends3 WHERE user_id = ? AND friend_id = ?",
                VALUES=(ID, call.message.chat.id,), one=True
            )
            try:
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(text="Да", callback_data=f"Request:{call.message.chat.id}"),
                    InlineKeyboardButton(text="Нет", callback_data=f"cancel:{call.message.chat.id}")
                )
                await bot.send_message(
                    ID, f"Вы хотите продолжить диалог с {Name[0]}?", reply_markup=builder.as_markup()
                )
                await call.message.edit_text("Вы успешно отправили запрос!")
            except Exception:
                await call.message.edit_text("Произошла ошибка, возможно, собеседник удалил чат с ботом.")
        else:
            await call.message.answer("Извините, этот пользователь занят.")
    else:
        await call.message.answer("Если вы хотите начать новый диалог, то введите /stop.")


@router.callback_query(F.data.split(":")[0] == "Unban")
async def callback79(call: CallbackQuery):
    try:
        ID = int(call.data.split(":")[1])
        execute("DELETE FROM banned_users WHERE user_id = ?", VALUES=(ID,))
        await call.answer("Готово!")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Забанить", callback_data=f"Ban:{ID}"))
        await call.message.edit_reply_markup(reply_markup=builder.as_markup())
        await bot.send_message(ID, "Вы были разбанены.")
    except Exception as EX:
        logger.error(f"{datetime.datetime.now()} EX: {EX}, function: unban")
        await call.answer("Произошла ошибка.")


@router.callback_query()
async def CallBack(call: CallbackQuery, state: FSMContext):
    if call.data[:-1] in kb.categories:
        try:
            List = []
            Res = execute(
                "SELECT name FROM groups WHERE category = ? AND type = 0", VALUES=(call.data[:-1],)
            )
            for Name in Res:
                Res2 = execute("SELECT * FROM group_subscribers WHERE name = ?", VALUES=(Name[0],))
                List.append({"name": Name[0], "number": len(Res2)})
            sorted_list = sorted(List, reverse=True, key=lambda x: x["number"])
            subscribers = sorted_list[0]["number"]
            Name = sorted_list[0]["name"]
            res = execute("SELECT * FROM groups WHERE name = ?", VALUES=(Name,), one=True)
            date = res[1]
            description = res[4]
            photo = res[5]
            views = res[7]
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Вступить", callback_data=f"join:{Name}"))
            builder.row(InlineKeyboardButton(text="Ещё", callback_data=f"more_groups:0:{call.data[:-1]}"))
            image = FSInputFile(photo)
            await call.message.answer_photo(
                photo=image,
                caption=f"{Name}\n\n{description}\n\n"
                        f"Количество подписчиков: {subscribers}\n"
                        f"Количество просмотров: {views}\n"
                        f"Дата создания: {date.split(' ')[0]}",
                reply_markup=builder.as_markup()
            )
            execute("UPDATE groups SET views = ? WHERE name = ?", VALUES=(views + 1, Name,))
        except IndexError:
            await call.message.answer("Извините, ничего не нашлось...")
    elif call.data in kb.categories:
        await state.update_data(category=call.data)
        await state.set_state(Register.name)
        await call.message.answer("Отправьте название вашей группы.")
    elif "CheckBuy_" in call.data:
        Data = call.data.replace("CheckBuy_", "").split("_")
        label = Data[0]
        coins = int(Data[1])
        res = await check_buy(label)
        if res:
            try:
                result = float(
                    execute("SELECT coin FROM users WHERE user_id = %d" % (call.message.chat.id,), one=True)[0]
                )
                result += coins
                execute("UPDATE users SET coin = ? WHERE user_id = ?", (result, call.message.chat.id,))
                markup = InlineKeyboardMarkup(inline_keyboard=kb.button4)
                await call.message.edit_text("Вы успешно пополнили баланс!", reply_markup=markup)
                for k, v in config.admins.items():
                    await bot.send_message(
                        v,
                        f"Здравствуйте! Пользователь с ID <code>{call.message.chat.id}</code> "
                        f"пополнил баланс на сумму {coins}₽!"
                    )
            except Exception as EX:
                logger.error(f"{datetime.datetime.now()} EX: {EX}, function: CallBack")
                await call.message.answer("Произошла ошибка, повторите попытку.")
        else:
            await call.message.answer("Оплата ещё не прошла, повторите попытку.")
    else:
        await call.message.answer("Неправильное нажатие!")
