import json
import time

import pygsheets
import telebot
from dotenv import dotenv_values

import messages
from service import db
from service import spredsheet

env = dotenv_values('.env')

TOKEN = env.get('TELEGRAM_STAFF_TOKEN')
CHAT = env.get('TELEGRAM_CHAT_ID')
CLIENT_SECRET_FILE = env.get('CLIENT_SECRET_FILE')

# TODO: stop using json config (#6)
with open('config.json', 'r') as file:
    CONFIG = json.loads(file.read())

bot = telebot.TeleBot(TOKEN)
manager = pygsheets.authorize(service_account_file=CLIENT_SECRET_FILE)
connect, cursor = db.connect_database(env)


# Markups

main_menu_markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
main_menu_markup.add(
    telebot.types.InlineKeyboardButton('мои показатели \U0001f3af'),
    telebot.types.InlineKeyboardButton('мой план \U0001f4b5'),
    telebot.types.InlineKeyboardButton('день \U0001f4c6'),
    telebot.types.InlineKeyboardButton('неделя \U0001f5d3'),
    telebot.types.InlineKeyboardButton('иски \U0001f5ff'),
    telebot.types.InlineKeyboardButton('выручка \U0001f4b0'),
    telebot.types.InlineKeyboardButton('красавчики \U0001F3C6'),
    telebot.types.InlineKeyboardButton('объявление \U0001f4ef'),
)

statistic_day_markup = telebot.types.InlineKeyboardMarkup()
statistic_day_markup.add(
    telebot.types.InlineKeyboardButton('продажи', callback_data='день продажи'),
    telebot.types.InlineKeyboardButton('делопроизводство', callback_data='день делопроизводство'),
    telebot.types.InlineKeyboardButton('руководство', callback_data='день руководство'),
)

statistic_week_markup = telebot.types.InlineKeyboardMarkup()
statistic_week_markup.add(
    telebot.types.InlineKeyboardButton('продажи', callback_data='неделя продажи'),
    telebot.types.InlineKeyboardButton('делопроизводство', callback_data='неделя делопроизводство'),
    telebot.types.InlineKeyboardButton('руководство', callback_data='неделя руководство'),
)

leader_markup = telebot.types.InlineKeyboardMarkup()
leader_markup.add(
    telebot.types.InlineKeyboardButton('делопроизводство', callback_data='красавчик делопроизводство'),
)

plan_markup = telebot.types.InlineKeyboardMarkup()
plan_markup.add(
    telebot.types.InlineKeyboardButton('на день', callback_data='план день'),
    telebot.types.InlineKeyboardButton('на неделю', callback_data='план неделя'),
)


# Permissions

def user_has_permission(func):
    """
    Permission decorator.
    Checks if the telegram user is in DB and has access to the bot.
    Otherwise, sends an error message.
    """

    def inner(message):
        if db.user_exists(cursor, message.from_user.id):
            func(message)
        else:
            bot.send_message(message.from_user.id, messages.DENY_ANONIMUS_MESSAGE)
    return inner


def user_is_admin(func):
    """
    Permission decorator.
    Checks if the telegram user is admin (DB: "is_admin" field).
    Otherwise, sends an error message.
    """

    def inner(message):
        if db.user_is_admin(cursor, message.from_user.id):
            func(message)
        else:
            bot.send_message(message.from_user.id, messages.DENY_MESSAGE)
    return inner


# Commands actions

@bot.message_handler(commands=['start'])
@user_has_permission
def send_welcome(message):
    """
    /start command handler:
    sends a 'welcome message' and displays a main markup to user
    """

    user_id = message.from_user.id
    name = message.from_user.first_name
    bot.send_message(user_id, messages.START_MESSAGE.format(name), reply_markup=main_menu_markup)


@bot.message_handler(commands=['help'])
@user_has_permission
def send_help_text(message):
    """
    /help command handler:
    sends a 'help message' to user
    """

    bot.send_message(
        message.from_user.id,
        messages.HELP_MESSAGE.format(
            # TODO: stop using json config (#6)
            CONFIG['google']['tables']['KPI']['table'],
            CONFIG['google']['tables']['план']['table'],
        ),
    )


@bot.message_handler(commands=['users'])
@user_has_permission
def send_list_users(message):
    """
    /users command handler:
    sends a list of users, who was added in the DB via /adduser command
    """

    users = db.list_users(cursor)
    bot.send_message(message.from_user.id, users)


@bot.message_handler(commands=['adduser'])
@user_has_permission
@user_is_admin
def add_user_command_handler(message):
    """
    /adduser command handler (admin permission required):
    Adds user to the DB.
    Admin user must send a message with contains information about the new user.

    The format is:
        <telegram_id> <telegram_username> <firstname> <lastname> <department> <position> <is_admin>

    Example:
        111111111 demon_slayer_2000 Иван Иванов продажи лиды
    """

    def add_user(handler_message):
        data = handler_message.text.split()

        if len(data) != 7:
            bot.send_message(handler_message.from_user.id, 'Неверный формат.')
        elif data[4] not in messages.MESSAGES_CONFIG.keys():
            bot.send_message(handler_message.from_user.id, 'Указанный отдел не представлен в списке.')
        elif data[5] not in messages.MESSAGES_CONFIG[data[4]].keys():
            bot.send_message(handler_message.from_user.id, 'Указанный функционал отсутствует в списке.')
        else:
            try:
                user_id, username, firstname, lastname, department, position = data[0:6]
                is_admin = True if data[6] == 'да' else False
                args = cursor, connect, int(user_id), username, firstname, lastname, department, position, is_admin
            except (ValueError, KeyError):
                bot.send_message(handler_message.from_user.id, 'Неверный формат.')
            else:
                user_added = db.add_user(*args)
                if user_added:
                    bot.send_message(handler_message.from_user.id, 'Пользователь добавлен.')
                else:
                    bot.send_message(handler_message.from_user.id, f'Пользователь уже добавлен в базу (ID: {user_id}).')

    message = bot.send_message(message.from_user.id, messages.USER_ADD_MESSAGE)
    bot.register_next_step_handler(message, add_user)


@bot.message_handler(commands=['deluser'])
@user_has_permission
@user_is_admin
def delete_user_command_handler(message):
    """
    /deluser command handler (admin permission required):
    removes some user from the DB by its ID.
    Admin user must send a message with telegram ID of the user who supposed to be deleted from the bot

    The format is:
        <telegram_id>

    Example:
        111111111
    """

    def delete_user(handler_message):
        user_id = handler_message.text

        if user_id.isnumeric():
            db.delete_user(cursor, connect, user_id)
            bot.send_message(handler_message.from_user.id, f'Пользователь с ID "{user_id}" удален.')
        else:
            bot.send_message(handler_message.from_user.id, 'Неверный формат пользовательского ID.')

    message = bot.send_message(message.from_user.id, messages.USER_DELETE_MESSAGE)
    bot.register_next_step_handler(message, delete_user)


# Buttons actions

# Not used, probably can be removed
@bot.message_handler(regexp=r'мой план\S*')
def set_plan_message_handler(message):
    """
    Plan handler:
    allows user to set a day/week plan.
    Shows a markup with the specified choices, which triggers set_plan callback.
    """

    bot.send_message(message.from_user.id, 'На какой срок нужно выставить план?', reply_markup=plan_markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('план'))
def set_plan_callback(call):
    """
    Plan handler's callback:
    ask user to provide his day/week plan values and writes them into the plan google sheet.
    """

    def set_plan(handler_message, **kwargs):
        values = handler_message.text.split()

        if len(values) < kwargs['valamount']:
            bot.send_message(handler_message.from_user.id, 'Указаны не все показатели \u261d\U0001f3fb')
        elif len(values) > kwargs['valamount']:
            bot.send_message(handler_message.from_user.id, 'Указаны лишние показатели \u261d\U0001f3fb')
        elif not all(value.isnumeric() for value in values):
            bot.send_message(handler_message.from_user.id,
                             'Ответ должен быть количетсвенным и состоять из чисел \u261d\U0001f3fb')
        else:
            # TODO: stop using json config (#6)
            # TODO: refactor spreadsheet module (#12)
            status = spredsheet.write_plan_to_google_sheet(
                manager=manager,
                sheet_key=CONFIG['google']['tables']['план']['table'],
                page_id=CONFIG['google']['tables']['план']['sheets'][kwargs['department']],
                user_id=handler_message.from_user.id,
                department=kwargs['department'],
                position=kwargs['position'],
                period=kwargs['period'],
                values=values,
            )
            if status:
                table_url = 'https://docs.google.com/spreadsheets/d/{}/edit#gid={}/'.format(
                    CONFIG['google']['tables']['план']['table'],
                    CONFIG['google']['tables']['план']['sheets'][kwargs['department']],
                )
                bot.send_message(
                    handler_message.from_user.id,
                    f'Цель установлена \u2705\n\nМожно отследить свои показатели в таблице:\n{table_url}\n\n',
                )
            else:
                # TODO: logging (#10)
                bot.send_message(handler_message.from_user.id, 'Вас нет в таблице. Администратор оповещен.')

    kwargs = db.get_employee_department_and_position(cursor, call.from_user.id)
    department = kwargs['department']
    position = kwargs['position']

    kwargs['period'] = call.data.split()[-1]

    try:
        # TODO: stop using json config (#6)
        employee = CONFIG['подразделения'][department][position]['сотрудники'][str(call.from_user.id)]
    except KeyError:
        # TODO: logging (#10)
        bot.send_message(call.from_user.id, 'Я вас не узнаю. Администратор оповещен.')
    else:
        if employee['планирование']:
            if employee['планирование'][kwargs['period']]:
                bot.send_message(call.from_user.id, messages.PLAN_MESSAGE)
                kwargs['valamount'] = len(employee['планирование'][kwargs['period']]['текущая']['план'].keys())
                message = bot.send_message(
                    call.from_user.id,
                    '\n'.join(employee['планирование'][kwargs['period']]['текущая']['план'].keys()),
                )
                bot.register_next_step_handler(message, set_plan, **kwargs)
            else:
                bot.send_message(call.from_user.id, 'Ваши планы на указанный срок не отслеживаются \U0001f44c\U0001f3fb')
        else:
            bot.send_message(call.from_user.id, 'Ваши планы не отслеживаются ботом \U0001f44c\U0001f3fb')


@bot.message_handler(regexp=r'мои показатели\S*')
@user_has_permission
def kpi_check_message_handler(message):
    """
    KPI handler:
    allows user to send his day results (KPI values).
    The provided values are written on the KPI google sheet.
    """

    def kpi_check(handler_message, **kwargs):
        values = handler_message.text.split()

        if len(values) < kwargs['response_len']:
            bot.send_message(handler_message.from_user.id, 'Указаны не все показатели \u261d\U0001f3fb')
        elif len(values) > kwargs['response_len']:
            bot.send_message(handler_message.from_user.id, 'Указаны лишние показатели \u261d\U0001f3fb')
        elif not all(value.isnumeric() for value in values):
            bot.send_message(
                handler_message.from_user.id,
                'Ответ должен быть количетсвенным и состоять из чисел \u261d\U0001f3fb',
            )
        else:
            # TODO: stop using json config (#6)
            # TODO: refactor spreadsheet module (#12)
            status = spredsheet.write_kpi_to_google_sheet(
                manager=manager,
                sheet_key=CONFIG['google']['tables']['KPI']['table'],
                page_id=CONFIG['google']['tables']['KPI']['sheets'][kwargs['department']],
                user_id=handler_message.from_user.id,
                department=kwargs['department'],
                position=kwargs['position'],
                values=values,
            )
            if status:
                bot.send_message(message.from_user.id, 'Данные внесены \u2705\nХорошего вечера! \U0001f942')
            else:
                bot.send_message(handler_message.from_user.id, 'Вас не добавили в таблицу. Администратор оповещен.')

    kwargs = db.get_employee_department_and_position(cursor, message.from_user.id)
    try:
        # TODO: messages refactoring (#11)
        if messages.MESSAGES_CONFIG[kwargs['department']][kwargs['position']]:
            kwargs.update(
                response_len=messages.MESSAGES_CONFIG[kwargs['department']][kwargs['position']]['values_amount'],
            )
            message = bot.send_message(
                message.from_user.id, messages.MESSAGES_CONFIG[kwargs['department']][kwargs['position']]['message'],
            )
            bot.register_next_step_handler(message, kpi_check, **kwargs)
        else:
            bot.send_message(
                message.from_user.id,
                'На данный период ваш KPI не отслеживается ботом \U0001f44c\U0001f3fb',
            )
    except (ValueError, KeyError):
        # TODO: logging (#10)
        bot.send_message(message.from_user.id, 'Что-то пошло не так. Администратор оповещен.')


@bot.message_handler(regexp=r'день\S*')
@user_has_permission
def day_statistic_message_handler(message):
    """
    Day statistic handler:
    allows user to get statistics (KPI, leader, and other values) of the chosen department for today.
    Shows a markup with the departments list, which triggers day_statistic callback.
    """

    bot.send_message(message.chat.id, text='Выберите отдел', reply_markup=statistic_day_markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('день'))
def day_statistic_callback(call):
    """
    Day statistic handler's callback:
    sends user day statistics of the specified department.
    """

    bot.answer_callback_query(
        callback_query_id=call.id,
        text='Минуту, собираю данные.\nОбычно это занимает не больше 5 секунд \U0001f552',
    )

    department = call.data.split()[-1]

    # TODO: stop using json config (#6)
    # TODO: refactor spreadsheet module (#12)
    kpi_daily = spredsheet.get_daily_statistic(
        manager=manager,
        sheet_key=CONFIG['google']['tables']['KPI']['table'],
        page_id=CONFIG['google']['tables']['KPI']['sheets'][department],
        department=department,
    )

    bot.send_message(call.message.chat.id, 'Статистика за день \U0001f4c6')
    result_day = [f'{k}: {v}' for k, v in kpi_daily.items()]
    bot.send_message(call.message.chat.id, '\n'.join(result_day))

    bot.send_message(call.message.chat.id, 'Статистика по сотрудникам \U0001F465')

    # TODO: stop using json config (#6)
    # TODO: refactor spreadsheet module (#12)
    kpi_daily_detail = spredsheet.get_daily_detail_statistic(
        manager=manager,
        sheet_key=CONFIG['google']['tables']['KPI']['table'],
        page_id=CONFIG['google']['tables']['KPI']['sheets'][department],
        department=department
    )
    result_week = []
    for position, employees in kpi_daily_detail.items():
        employees_result = []
        if employees:
            for employee, values in employees.items():
                employees_result.append(f'\n\U0001F464 {employee}:\n')
                employees_result.append('\n'.join([f'{k}: {v}' for k, v in values.items()]))
            result_week.append(f'\n\n\U0001F53D {position.upper()}')
            result_week.append('\n'.join(employees_result))
    bot.send_message(call.message.chat.id, '\n'.join(result_week))


@bot.message_handler(regexp=r'неделя\S*')
@user_has_permission
def week_statistic_message_handler(message):
    """
    Week statistic handler:
    allows user to get statistics (KPI, leader, and other values) of the chosen department for the current week.
    Shows a markup with the departments list, which triggers week_statistic callback.
    """

    bot.send_message(message.chat.id, text='Выберите отдел', reply_markup=statistic_week_markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('неделя'))
def week_statistic_callback(call):
    """
    Week statistic handler's callback:
    sends user week statistics of the specified department.
    """

    bot.answer_callback_query(
        callback_query_id=call.id,
        text=('Собираю данные.\nОбычно это занимает не больше 5 секунд \U0001f552'),
    )

    department = call.data.split()[-1]

    # TODO: stop using json config (#6)
    # TODO: refactor spreadsheet module (#12)
    kpi_daily = spredsheet.get_weekly_statistic(
        manager=manager,
        sheet_key=CONFIG['google']['tables']['KPI']['table'],
        page_id=CONFIG['google']['tables']['KPI']['sheets'][department],
        department=department,
    )
    bot.send_message(call.message.chat.id, 'Статистика за неделю \U0001f5d3')
    result = [f'{k}: {v}' for k, v in kpi_daily.items()]
    bot.send_message(call.message.chat.id, '\n'.join(result))


@bot.message_handler(regexp=r'выручка\S*')
@user_has_permission
@user_is_admin
def day_revenue_message_handler(message):
    """
    Day revenue handler (admin permission required):
    allows user to send a revenue for today.
    The provided values are written on the KPI google sheet.
    """

    def get_day_revenue(handler_message):
        if not handler_message.text.isnumeric():
            bot.send_message(
                handler_message.from_user.id,
                'Прости, я не понял. Попробуй снова и пришли пожалуйста данные в числовом формате \u261d\U0001f3fb',
            )
        else:
            # TODO: stop using json config (#6)
            # TODO: refactor spreadsheet module (#12)
            status = spredsheet.write_income_to_google_sheet(
                manager=manager,
                sheet_key=CONFIG['google']['tables']['KPI']['table'],
                page_id=CONFIG['google']['tables']['KPI']['sheets']['руководство'],
                value=handler_message.text,
            )
            if status:
                bot.send_message(handler_message.from_user.id, 'Спасибо! Данные внесены \u2705')
            else:
                bot.send_message(handler_message.from_user.id, 'Что-то пошло не так. Администратор оповещен.')

    bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}!\nКакая сумма выручки на сегодня?')
    bot.register_next_step_handler(message, get_day_revenue)


@bot.message_handler(regexp=r'иски\S*')
@user_has_permission
@user_is_admin
def week_lawsuits_message_handler(message):
    """
    Week lawsuits handler (admin permission required):
    allows user to send a number of written lawsuits for today.
    The provided values are written on the KPI google sheet.
    """

    def send_week_lawsuits(handler_message):
        if not handler_message.text.isnumeric():
            bot.send_message(
                handler_message.from_user.id,
                'Прости, я не понял. Попробуй снова и пришли пожалуйста данные в числовом формате \u261d\U0001f3fb',
            )
        else:
            # TODO: stop using json config (#6)
            # TODO: refactor spreadsheet module (#12)
            status = spredsheet.write_lawsuits_to_google_sheet(
                manager=manager,
                sheet_key=CONFIG['google']['tables']['KPI']['table'],
                page_id=CONFIG['google']['tables']['KPI']['sheets']['делопроизводство'],
                value=handler_message.text,
            )
            if status:
                bot.send_message(handler_message.from_user.id, 'Спасибо! Данные внесены \u2705')
            else:
                # TODO: logging (#10)
                bot.send_message(handler_message.from_user.id, 'Что-то пошло не так.')

    bot.send_message(
        message.from_user.id,
        f'Привет {message.from_user.first_name}!\nСколько было подано исков на этой неделе?',
    )
    bot.register_next_step_handler(message, send_week_lawsuits)


@bot.message_handler(regexp=r'красавчик\S*')
@user_has_permission
def day_leader_message_handler(message):
    """
    Day leader handler:
    allows to see the leader (an employee with the best KPI values) of the chosen department for the current day.
    Shows a markup with the departments list, which triggers day_leader callback.
    """

    bot.send_message(message.chat.id, text='Выберите отдел', reply_markup=leader_markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('красавчик'))
def day_leader_callback(call):
    """
    Day leader handler's callback:
    tell who is the leader of the specified department.
    If there is no leader for today, just sends a corresponding message.
    """

    department = call.data.split()[-1]
    # TODO: stop using json config (#6)
    # TODO: refactor spreadsheet module (#12)
    leaders = spredsheet.get_leaders_from_google_sheet(
        manager=manager,
        sheet_key=CONFIG['google']['tables']['KPI']['table'],
        page_id=CONFIG['google']['tables']['KPI']['sheets'][department],
        department=department,
    )
    if leaders:
        bot.send_message(call.message.chat.id, '\U0001f38a Красавчики дня: ' + ', '.join(leaders))
    else:
        bot.send_message(call.message.chat.id, '\U0001f5ff Красавчиков дня нет')


@bot.message_handler(regexp=r'объявление\S*')
@user_has_permission
@user_is_admin
def make_announcement_message_handler(message):
    """
    Announcement handler (admin permission required):
    sends an announcement (a message) to all users.
    """

    def send_announcement(handler_message, **kwargs):
        if handler_message.text.lower() == 'нет':
            bot.send_message(handler_message.from_user.id, 'Принял. Отменяю \U0001f44c\U0001f3fb')
        elif handler_message.text.lower() == 'да':
            # TODO: there is a bug - if some user from the DB has 'stopped' the bot, this function will return an error.
            for user_id in kwargs['ids']:
                bot.send_message(user_id, kwargs['text'])
            bot.send_message(handler_message.from_user.id, 'Готово! Сотрудники уведомлены \u2705')
        else:
            bot.send_message(message.from_user.id, 'Я не понял ответа. Отменяю. \U0001f44c\U0001f3fb')

    def prepare_announcement(handler_message):
        ids = db.return_users_ids(cursor)
        kwargs = {'text': handler_message.text, 'ids': ids}
        bot.send_message(handler_message.from_user.id, 'Записал. Отправляем? (да/нет)')
        bot.register_next_step_handler(handler_message, send_announcement, **kwargs)

    bot.send_message(
        message.from_user.id,
        f'Привет {message.from_user.first_name}! Пришли сообщение, которое нужно отправить сотрудникам \U0001f4dd')
    bot.register_next_step_handler(message, prepare_announcement)


if __name__ == '__main__':
    # TODO: investigate logs and try to catch the errors
    # TODO: logging (#10)
    while True:
        try:
            bot.polling()
        except Exception:
            time.sleep(5)
