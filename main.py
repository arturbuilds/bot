import telebot
import sqlite3
from telebot import types
from datetime import datetime, timedelta

token = '8740005988:AAEzFdnNgIujH4w4xJn46SVOj2Q3V-phB1c'
bot = telebot.TeleBot(token)
admin_id = 5996865953

admin_states = {}

def get_next_days(offset=0):
    days_ukr = {0: 'Пн', 1: 'Вв', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Нд'}
    months_ukr = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня', 
                  7: 'липня', 8: 'серпня', 9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}
    
    now = datetime.now()
    days_list = []

    for i in range(offset, offset + 4):
        target_date = now + timedelta(days=i)

        db_data_str = target_date.strftime('%Y-%m-%d')

        if i == 0:
            btn_text = 'Сьогодні'
        elif i == 1:
            btn_text = 'Завтра'
        else:
            day_name = days_ukr[target_date.weekday()]
            day_num = target_date.day
            months_name = months_ukr[target_date.month]
            btn_text = f'{day_name}, {day_num} {months_name}'

        days_list.append((btn_text, db_data_str))

    return days_list
    

def init_db():
    conn = sqlite3.connect('salon_booking.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_selections (
            user_id INTEGER PRIMARY KEY,
            selected_service_id INTEGER,
            selected_master_id INTEGER,
            selected_date TEXT,
            selected_time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone TEXT,
            service TEXT,
            master TEXT,
            date TEXT,
            time TEXT           
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            profession TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        services = [
            ('Стрижка жіноча', 350),
            ('Стрижка чоловіча', 250),
            ('Фарбування', 600),
            ('Макіяж денний', 300),
            ('Макіяж вечірній', 400),
            ('Ламінування вій', 500),
            ('Чистка обличчя', 450),
            ('Убіть сінінкіна', 1)
        ]
        cursor.executemany("INSERT INTO services (name, price) VALUES (?, ?)", services)
    
    cursor.execute("SELECT COUNT(*) FROM masters")
    if cursor.fetchone()[0] == 0:
        masters = [
            ('Ольга', 'стиліст, візажист'),
            ('Оксана', 'косметолог'),
            ('Марія', 'бровист, колорист'),
            ('Сінікін', 'сексолог')
        ]
        cursor.executemany("INSERT INTO masters (name, profession) VALUES (?, ?)", masters)
    
    conn.commit()
    conn.close()

def get_services():
    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price FROM services')
    data = cursor.fetchall()
    conn.close()
    return data

def get_masters():
    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, profession FROM masters')
    data = cursor.fetchall()
    conn.close()
    return data

@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    full_name = f'{first_name} {last_name}'.strip()

    username = message.from_user.username
    user_id = message.from_user.id

    text_admin = f'В бот зашел {full_name}\n username: {username}\n id: {user_id}'

    bot.send_message(admin_id, text_admin)

    text_welcome = f'Привіт, {full_name}! Ви в чат боті салону краси'
    bot.send_message(message.chat.id, text_welcome)

    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    button_record_inline = types.InlineKeyboardButton('Записатися ✍️', callback_data='record_apponiment')
    button_about_us_inline = types.InlineKeyboardButton('Про нас', callback_data='about_us')
    markup_inline.add(button_record_inline, button_about_us_inline)

    bot.send_message(message.chat.id, 'Оберіть наступний крок', reply_markup=markup_inline)

@bot.callback_query_handler(func=lambda call: call.data == 'about_us')
def about_us(call):
    bot.answer_callback_query(call.id)

    about_text = (
        "✨ *Ласкаво просимо до нашого простору краси!* ✨\n\n"
        "Ми створили місце, де ваш стиль та здоров'я шкіри — наш главный пріоритет. "
        "У роботі ми використовуємо лише світові преміум-бренди космецевтики (Medik8, Casmara, Davines) "
        "та сертифіковане європейське обладнання.\n\n"
        "🌸 *Наші ключові напрямки:*\n"
        "• *Стиль:* авторські стрижки, складні фарбування та догляд за волоссям.\n"
        "• *Естетика:* преміальна косметологія, апаратна корекція фігури, RF-ліфтинг.\n"
        "• *Погляд:* ламінування вій та професійне оформлення брів.\n\n"
        "📍 *Чекаємо на вас за адресою:* м. Львів, вул. Григоровича, 6\n\n"
        "🔗 *Наш Instagram:* [відвідати профіль](https://instagram.com)"
    )

    back_markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton('⬅️ На головну', callback_data='to_main_menu')
    back_markup.add(back_button)

    bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = about_text,
        parse_mode = 'Markdown',
        reply_markup = back_markup,
        disable_web_page_preview = True
    )

@bot.callback_query_handler(func=lambda call: call.data == 'to_main_menu')
def go_to_main_menu(call):
    bot.answer_callback_query(call.id)

    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    button_record_inline = types.InlineKeyboardButton('Записатися ✍️', callback_data='record_apponiment')
    button_about_us_inline = types.InlineKeyboardButton('Про нас', callback_data='about_us')
    markup_inline.add(button_record_inline, button_about_us_inline)

    bot.edit_message_text(
        chat_id = call.message.chat.id, 
        message_id = call.message.message_id, 
        text = 'Оберіть наступний крок', 
        reply_markup = markup_inline
    )

@bot.callback_query_handler(func=lambda call: call.data == 'record_apponiment')
def record_apponiment(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    conn = sqlite3.connect('salon_booking.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('SELECT selected_service_id, selected_master_id, selected_date, selected_time FROM user_selections WHERE user_id = ?', (user_id,))

    result = cursor.fetchone()

    service_text = 'Обрати послуги'
    date_text = 'Обрати дату та час'
    master_text = 'Обрати співробітника'

    all_selected = False

    if result:
        service_id, master_id, date, time = result

        if service_id:
            cursor = sqlite3.connect('salon_booking.db').cursor()
            cursor.execute('SELECT name FROM services WHERE id = ?', (service_id,))
            service_name = cursor.fetchone()
            if service_name:
                service_text = f'Послуга ✅ ({service_name[0]})'

        if master_id:
            cursor = sqlite3.connect('salon_booking.db').cursor()
            cursor.execute('SELECT name FROM masters WHERE id = ?', (master_id,))
            master_name = cursor.fetchone()
            if master_name:
                master_text = f'Майстер ✅ ({master_name[0]})'

        if date and time:
            date_text = f'Дата та час ✅ ({date}, {time})'
        
        all_selected = bool(service_id and master_id and date and time)

    conn.close()

    text = 'Обрати деталі запису'

    record_markup = types.InlineKeyboardMarkup(row_width=1)
    record_poslyga = types.InlineKeyboardButton(service_text, callback_data='poslyga')
    record_time = types.InlineKeyboardButton(date_text, callback_data='time')
    record_work = types.InlineKeyboardButton(master_text, callback_data='choose_masters')
    record_go_to_home = types.InlineKeyboardButton('⬅️ На головну', callback_data='to_main_menu')
    record_markup.add(record_poslyga, record_time, record_work, record_go_to_home)

    if all_selected:
        record_markup.add(types.InlineKeyboardButton('Підтвердити запис ➡️', callback_data='confirm_booking'))

    bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = text,
        parse_mode = 'Markdown',
        reply_markup = record_markup,
    )

@bot.callback_query_handler(func=lambda call: call.data == 'poslyga')
def poslyga(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT selected_service_id FROM user_selections WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    current_service_id = result[0] if result else None
    conn.close()

    poslyga_markup = types.InlineKeyboardMarkup(row_width=1)
    
    for sid, name, price in get_services():
        if sid == current_service_id:
            btn_text = f'✅ {name} - {price}₴'
        else:
            btn_text = f'{name} - {price}₴'
        poslyga_markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'service_{sid}'))

    record_go_to_home = types.InlineKeyboardButton('⬅️ На головну', callback_data='to_main_menu')
    continue_btn = types.InlineKeyboardButton('Продовжити ➡️', callback_data='continue_from_services')
    poslyga_markup.row(record_go_to_home, continue_btn)

    bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Обрати деталі запису',
        reply_markup = poslyga_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def selected_service(call):
    bot.answer_callback_query(call.id)
    service_id = int(call.data.split('_')[1])
    user_id = call.from_user.id

    conn = sqlite3.connect("salon_booking.db")
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO user_selections (user_id) VALUES (?)', (user_id,))
    cursor.execute('UPDATE user_selections SET selected_service_id = ? WHERE user_id = ?', (service_id, user_id))

    conn.commit()
    conn.close()

    poslyga(call)

@bot.callback_query_handler(func=lambda call: call.data == 'continue_from_services')
def continue_from_services(call):
    bot.answer_callback_query(call.id)
    record_apponiment(call)

@bot.callback_query_handler(func=lambda call: call.data == 'choose_masters')
def choose_masters(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT selected_master_id FROM user_selections WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    current_master_id = result[0] if result else None
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for master_id, name, profession in get_masters():
        if master_id == current_master_id:
            btn_text = f'✅ {name} - {profession}'
        else:
            btn_text = f'{name} - {profession}'
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'master_{master_id}'))
    
    back_button = types.InlineKeyboardButton('◀️ Назад', callback_data='record_apponiment')
    continue_btn = types.InlineKeyboardButton('Продовжити ➡️', callback_data='continue_from_masters')
    markup.row(back_button, continue_btn)
    
    bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Оберіть деталі запису',
        reply_markup = markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('master_'))
def selected_master(call):
    bot.answer_callback_query(call.id)
    master_id = int(call.data.split('_')[1])
    user_id = call.from_user.id

    conn = sqlite3.connect("salon_booking.db")
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO user_selections (user_id) VALUES (?)', (user_id,))
    cursor.execute('UPDATE user_selections SET selected_master_id = ? WHERE user_id = ?', (master_id, user_id))

    conn.commit()
    conn.close()
    
    choose_masters(call)

@bot.callback_query_handler(func=lambda call: call.data == 'continue_from_masters')
def continue_from_masters(call):
    bot.answer_callback_query(call.id)
    record_apponiment(call)

@bot.callback_query_handler(func=lambda call: call.data == 'time')
def time(call):
    bot.answer_callback_query(call.id)

    days = get_next_days(0)

    date_markup = types.InlineKeyboardMarkup(row_width=1)

    for btn_text, db_date_str in days:
        btn = types.InlineKeyboardButton(
            btn_text,
            callback_data=f'select_date:{db_date_str}'
        )

        date_markup.add(btn)

    return_btn = types.InlineKeyboardButton('<<', callback_data='page:0')
    forth_btn = types.InlineKeyboardButton('>>', callback_data='page:4')

    date_markup.row(return_btn, forth_btn)

    back_btn = types.InlineKeyboardButton('⬅️ Назад', callback_data='record_apponiment')
    date_markup.add(back_btn)

    bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Оберіть дату для запису:',
        reply_markup = date_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('page:'))
def change_page(call):
    bot.answer_callback_query(call.id)

    offset = int(call.data.split(':')[1])

    days = get_next_days(offset)

    date_markup = types.InlineKeyboardMarkup(row_width=1)

    for btn_text, db_date_str in days:
        btn = types.InlineKeyboardButton(
            btn_text,
            callback_data=f'select_date:{db_date_str}'
        )
        date_markup.add(btn)

    prev_offset = max(0, offset - 4)
    next_offset = offset + 4

    return_btn = types.InlineKeyboardButton(
        '<<',
        callback_data=f'page:{prev_offset}'
    )

    forth_btn = types.InlineKeyboardButton(
        '>>',
        callback_data=f'page:{next_offset}'
    )

    date_markup.row(return_btn, forth_btn)

    back_btn = types.InlineKeyboardButton(
        '⬅️ Назад',
        callback_data='record_apponiment'
    )

    date_markup.add(back_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Оберіть дату для запису:',
        reply_markup=date_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_date:'))
def select_date(call):
    bot.answer_callback_query(call.id)

    selected_data = call.data.split(':')[1]
    user_id = call.from_user.id

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT time FROM bookings WHERE date = ?', (selected_data,))
    busy_times = [row[0] for row in cursor.fetchall()]

    cursor.execute('INSERT OR IGNORE INTO user_selections (user_id) VALUES (?)', (user_id,))
    cursor.execute('UPDATE user_selections SET selected_date = ? WHERE user_id = ?', (selected_data, user_id))

    conn.commit()

    cursor.execute('SELECT selected_time FROM user_selections WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    db_time = result[0] if result else None

    conn.close()

    text_14_00 = '14:00'
    text_14_15 = '14:15'
    text_14_30 = '14:30'
    text_14_45 = '14:45'
    text_15_00 = '15:00'
    text_15_15 = '15:15'
    text_15_30 = '15:30'
    text_15_45 = '15:45'
    text_16_00 = '16:00'

    if '14:00' in busy_times: text_14_00 += ' ❌'
    if '14:15' in busy_times: text_14_15 += ' ❌'
    if '14:30' in busy_times: text_14_30 += ' ❌'
    if '14:45' in busy_times: text_14_45 += ' ❌'
    if '15:00' in busy_times: text_15_00 += ' ❌'
    if '15:15' in busy_times: text_15_15 += ' ❌'
    if '15:30' in busy_times: text_15_30 += ' ❌'
    if '15:45' in busy_times: text_15_45 += ' ❌'
    if '16:00' in busy_times: text_16_00 += ' ❌'

    if db_time == '14:00': text_14_00 += ' ✅'
    if db_time == '14:15': text_14_15 += ' ✅'
    if db_time == '14:30': text_14_30 += ' ✅'
    if db_time == '14:45': text_14_45 += ' ✅'
    if db_time == '15:00': text_15_00 += ' ✅'
    if db_time == '15:15': text_15_15 += ' ✅'
    if db_time == '15:30': text_15_30 += ' ✅'
    if db_time == '15:45': text_15_45 += ' ✅'
    if db_time == '16:00': text_16_00 += ' ✅'

    def create_time_button(text, time_value):
        if time_value in busy_times:
            return types.InlineKeyboardButton(
                text,
                callback_data='busy_time'
            )
        else:
            return types.InlineKeyboardButton(
                text,
                callback_data=f'time_{time_value.replace(":", "_")}'
            )

    btn_14_00 = create_time_button(text_14_00, '14:00')
    btn_14_15 = create_time_button(text_14_15, '14:15')
    btn_14_30 = create_time_button(text_14_30, '14:30')
    btn_14_45 = create_time_button(text_14_45, '14:45')

    btn_15_00 = create_time_button(text_15_00, '15:00')
    btn_15_15 = create_time_button(text_15_15, '15:15')
    btn_15_30 = create_time_button(text_15_30, '15:30')
    btn_15_45 = create_time_button(text_15_45, '15:45')

    btn_16_00 = create_time_button(text_16_00, '16:00')

    markup_time = types.InlineKeyboardMarkup(row_width=1)

    markup_time.row(
        btn_14_00,
        btn_14_15,
        btn_14_30
    )

    markup_time.row(
        btn_14_45,
        btn_15_00,
        btn_15_15
    )

    markup_time.row(
        btn_15_30,
        btn_15_45,
        btn_16_00
    )

    markup_time.row(
        types.InlineKeyboardButton('⬅️ Назад', callback_data='time'),
        types.InlineKeyboardButton('Продовжити ➡️', callback_data='record_apponiment')
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Дата: {selected_data}\nОберіть час:',
        reply_markup=markup_time
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def select_time(call):
    bot.answer_callback_query(call.id)

    selected_time = call.data.replace('time_', '').replace('_', ':')
    user_id = call.from_user.id

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO user_selections (user_id) VALUES (?)', (user_id,))
    cursor.execute('UPDATE user_selections SET selected_time = ? WHERE user_id = ?', (selected_time, user_id))
    cursor.execute('SELECT selected_date FROM user_selections WHERE user_id = ?', (user_id,))

    result = cursor.fetchone()
    result = result[0] if result else None

    conn.commit()
    conn.close()

    fake_call = call
    fake_call.data = f"select_date:{result}"

    select_date(fake_call)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_booking')
def confirm_booking(call):
    bot.answer_callback_query(call.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton(text = '📱 Поділитися контактом', request_contact=True)
    markup.add(contact_btn)

    bot.send_message(call.message.chat.id, 'Щоб підтвердити запис, натисніть на кнопку "Поділитися контактом"',reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def get_contact(message):
    phone = message.contact.phone_number
    user_id = message.from_user.id

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT selected_service_id, selected_master_id, selected_date, selected_time
        FROM user_selections
        WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    
    if result:
        service_id, master_id, selected_date, selected_time = result
        
        cursor.execute('SELECT name FROM services WHERE id = ?', (service_id,))
        service_name = cursor.fetchone()
        service = service_name[0] if service_name else 'Невідомо'
        
        cursor.execute('SELECT name, profession FROM masters WHERE id = ?', (master_id,))
        master_data = cursor.fetchone()
        master = f'{master_data[0]} ({master_data[1]})' if master_data else 'Невідомо'
        
        cursor.execute('''
            INSERT INTO bookings (user_id, phone, service, master, date, time) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, phone, service, master, selected_date, selected_time))
        
        conn.commit()
        
        cursor.execute('DELETE FROM user_selections WHERE user_id = ?', (user_id,))
        conn.commit()

        bot.send_message(
            message.chat.id, f'''
                ✨ Дякуємо за запис!

                Ви успішно забронювали візит.

                📅 {selected_date}
                🕒 {selected_time}

                💄 {service}
                👩 {master}

                Якщо плани зміняться - зв'яжіться з нами заздалегідь.

                До зустрічі 🌷
                '''
            )

        admin_text = f'''
            🔔 Новий запис

            👤 Клієнт: {message.from_user.first_name}
            📞 Телефон: {phone}

            💄 Послуга: {service}
            👩 Майстер: {master}

            📅 Дата: {selected_date}
            🕒 Час: {selected_time}

            🆔 User ID: {user_id}
        '''

        bot.send_message(admin_id, admin_text)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, '⛔ Немає доступу')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    admin_bookings = types.InlineKeyboardButton('📋 Записи', callback_data='admin_bookings')
    admin_services = types.InlineKeyboardButton('💄 Послуги', callback_data='admin_services')
    admin_masters = types.InlineKeyboardButton('👩 Майстри', callback_data='admin_masters')
    
    markup.add(admin_bookings, admin_services, admin_masters)

    bot.send_message(
        message.chat.id,
        '⚙️ Адмін панель',
        reply_markup = markup
    )

def is_admin(call):
    return call.from_user.id == admin_id

@bot.callback_query_handler(func=lambda call: call.data == 'admin_bookings')
def admin_bookings(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton('📅 Сьогодні', callback_data='bookings_today'),
        types.InlineKeyboardButton('📅 Завтра', callback_data='bookings_tomorrow'),
        types.InlineKeyboardButton('📋 Всі записи', callback_data='bookings_all'),
        types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_menu')
    )

    bot.edit_message_text(
        '📋 Записи',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'bookings_today')
def bookings_today(call):
    bot.answer_callback_query(call.id)

    today = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT service, master, date, time, phone, user_id
        FROM bookings
        WHERE date = ?
        ORDER BY time
    ''', (today,))

    data = cursor.fetchall()
    conn.close()

    if not data:
        bot.send_message(call.message.chat.id, "📭 Сьогодні записів немає")
        return

    text = "📅 СЬОГОДНІ ЗАПИСИ:\n\n"

    for i, b in enumerate(data, 1):
        text += f"""
            {i}. 💄 {b[0]}
            👩 {b[1]}
            📞 {b[4]}
            🕒 {b[3]}
            🆔 {b[5]}

        """

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == 'bookings_tomorrow')
def bookings_tomorrow(call):
    bot.answer_callback_query(call.id)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT service, master, date, time, phone, user_id
        FROM bookings
        WHERE date = ?
        ORDER BY time
    ''', (tomorrow,))

    data = cursor.fetchall()
    conn.close()

    if not data:
        bot.send_message(call.message.chat.id, "📭 Завтра записів немає")
        return

    text = "📅 ЗАВТРА ЗАПИСИ:\n\n"

    for i, b in enumerate(data, 1):
        text += f"""
            {i}. 💄 {b[0]}
            👩 {b[1]}
            📞 {b[4]}
            🕒 {b[3]}
            🆔 {b[5]}

        """

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == 'bookings_all')
def bookings_all(call):
    bot.answer_callback_query(call.id)

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT service, master, date, time, phone, user_id
        FROM bookings
        ORDER BY date DESC, time DESC
    ''')

    data = cursor.fetchall()
    conn.close()

    if not data:
        bot.send_message(call.message.chat.id, "📭 Записів немає")
        return

    text = "📋 Всі записи:\n\n"

    for i, b in enumerate(data, 1):
        text += f"""
            {i}. 📅 {b[2]} {b[3]}
            💄 {b[0]}
            👩 {b[1]}
            📞 {b[4]}
            🆔 {b[5]}

        """

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == 'admin_services')
def admin_services(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton('➕ Додати послугу', callback_data='add_service'),
        types.InlineKeyboardButton('❌ Видалити послугу', callback_data='delete_service'),
        types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_menu')
    )

    bot.edit_message_text(
        '💄 Керування послугами',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'admin_menu')
def admin_menu(call):
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton('📋 Записи', callback_data='admin_bookings'),
        types.InlineKeyboardButton('💄 Послуги', callback_data='admin_services'),
        types.InlineKeyboardButton('👩 Майстри', callback_data='admin_masters')
    )

    bot.edit_message_text(
        '⚙️ Адмін панель',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'add_service')
def add_service(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)

    admin_states[call.from_user.id] = 'add_service'

    bot.send_message(
        call.message.chat.id,
        'Введіть послугу у форматі:\n\nМанікюр;500'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'delete_service')
def delete_service(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price FROM services')
    services = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)

    for sid, name, price in services:
        markup.add(
            types.InlineKeyboardButton(
                f'❌ {name} - {price} грн',
                callback_data=f'del_service_{sid}'
            )
        )

    markup.add(
        types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_services')
    )

    bot.send_message(
        call.message.chat.id,
        'Оберіть послугу для видалення:',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_service_'))
def confirm_delete_service(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id)

    service_id = int(call.data.replace('del_service_', ''))

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()

    bot.edit_message_text(
        '✅ Послугу видалено',
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(func=lambda message: message.from_user.id in admin_states)
def admin_actions(message):
    state = admin_states[message.from_user.id]

    if state == 'add_service':
        name, price = message.text.split(';')

        conn = sqlite3.connect('salon_booking.db')
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO services (name, price) VALUES (?, ?)',
            (name.strip(), int(price))
        )

        conn.commit()
        conn.close()

        del admin_states[message.from_user.id]

        bot.send_message(message.chat.id, f'✅ Послугу "{name}" додано')

    elif state == 'add_master':
        name, profession = message.text.split(';')

        conn = sqlite3.connect('salon_booking.db')
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO masters (name, profession) VALUES (?, ?)',
            (name.strip(), profession.strip())
        )

        conn.commit()
        conn.close()

        del admin_states[message.from_user.id]

        bot.send_message(message.chat.id, f'✅ Майстра "{name}" додано')

@bot.callback_query_handler(func=lambda call: call.data == 'admin_masters')
def admin_masters(call):
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)

    add_master = types.InlineKeyboardButton(
        '➕ Додати майстра',
        callback_data='add_master'
    )

    list_masters = types.InlineKeyboardButton(
        '📋 Список майстрів',
        callback_data='list_masters'
    )

    delete_master = types.InlineKeyboardButton(
        '❌ Видалити майстра',
        callback_data='delete_master'
    )

    back = types.InlineKeyboardButton(
        '⬅️ Назад',
        callback_data='admin_menu'
    )

    markup.add(add_master, list_masters, delete_master, back)

    bot.edit_message_text(
        '👩 Керування майстрами',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'add_master')
def add_master(call):
    bot.answer_callback_query(call.id)

    admin_states[call.from_user.id] = 'add_master'

    bot.send_message(
        call.message.chat.id,
        'Введіть майстра у форматі:\n\nІмʼя;Професія'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'list_masters')
def list_masters(call):
    bot.answer_callback_query(call.id)

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, profession FROM masters')
    masters = cursor.fetchall()

    conn.close()

    text = "📋 Список майстрів:\n\n"

    for mid, name, prof in masters:
        text += f"👩 {name} — {prof}\n"

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == 'delete_master')
def delete_master(call):
    bot.answer_callback_query(call.id)

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name FROM masters')
    masters = cursor.fetchall()

    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)

    for mid, name in masters:
        markup.add(
            types.InlineKeyboardButton(
                f'❌ {name}',
                callback_data=f'del_master_{mid}'
            )
        )

    bot.send_message(
        call.message.chat.id,
        'Оберіть майстра для видалення:',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_master_'))
def confirm_delete_master(call):
    bot.answer_callback_query(call.id)

    master_id = int(call.data.replace('del_master_', ''))

    conn = sqlite3.connect('salon_booking.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM masters WHERE id = ?', (master_id,))

    conn.commit()
    conn.close()

    bot.edit_message_text(
        '✅ Майстра видалено',
        call.message.chat.id,
        call.message.message_id
    )

init_db()   
print('Бот запущен...')
bot.infinity_polling()
