MESSAGES_CONFIG = {
    'руководство': {
        'worksheet': None,
        'руководитель': {},
        'заместитель': {},
        'помощник': {},
    },
    'делопроизводство': {
        'ведение': {
            'message': (
                'Пожалуйста, отправьте мне количественные '
                'данные в следующем формате:\n\n'
                '<заседаний>\n'
                '<решений>\n'
                '<подготовленных_исков>\n'
                '<иных_документов>\n'
                '<денег_получено>\n'
                '<событий_съедающих_бонус>\n\n'
                'Пример: 3 2 0 1 320000 0'
            ),
            'values_amount': 6,
        },
        'исполнение': {
            'message': (
                'Пожалуйста, отправьте мне следующие количественные:\n\n'
                '<заседаний>\n'
                '<решений>\n'
                '<получено_листов>\n'
                '<подано_листов>\n'
                '<иных_документов>\n'
                '<денег_получено>\n\n'
                '<напр_заявл_по_суд_расходам>\n'
                'Пример: 5 2 2 2 1 320000 0'
            ),
            'values_amount': 7,
        },
    },
    'продажи': {
        'лиды': {
            'message': (
                'Пожалуйста, отправьте мне следующие данные:\n\n'
                '<залив_заявок>\n'
                '<залив_напр_на_осмотр>\n'
                '<неустойка_заявок>\n'
                '<неустойка_получ_инн>\n'
                '<приемка_заявок>\n'
                '<приемка_напр_на_осмотр>\n'
                '<рег_учет_заявок>\n'
                '<рег_учет_назначено_встреч_в_офисе>\n\n'
                'Пример: 10 5 5 2 5 3 1 1'
            ),
            'values_amount': 8,
        },
        'хантинг': {
            'message': (
                'Пожалуйста, отправьте мне следующие данные:\n\n'
                '<залив_сделок>\n'
                '<неустойка_сделок>\n'
                '<приемка_сделок>\n'
                '<рег_учет_сделок>\n\n'
                'Пример: 10 5 0 1 '
            ),
            'values_amount': 4,
        }
    }
}

START_MESSAGE = (
    u'Привет, {}! \U0001f60a Я бот юридического центра Новиков.\n'
    'Я собираю статистику сотрудников, просчитываю их KPI и '
    'фиксирую данные в Google Sheets.\n'
    'По любым вопросам можно обратиться к '
    '@vilagov или @karlos979.'
)

DENY_ANONIMUS_MESSAGE = (
    'У вас нет прав для пользования данным бота.\n'
    'Обратитесь к @vilagov или @karlos979, если уверены '
    'что вам нужен доступ.'
)
DENY_MESSAGE = 'У вас недостаточно прав для выполнение данной команды.'

USER_ADD_MESSAGE = (
    'Отправьте данные добавляемого сотрудника в следующем формате:\n'
    '<telegram_ID_пользователя>\n<никнейм>\n<имя>\n'
    '<фамилия>\n<отдел>\n<позиция>\n<админ_доступ_(да/нет)>\n\n'
    'При указании отдела и позиции выбирайте из следующих значений:\n\n'
    'руководство:\n    руководитель, заместитель, помощник\n\n'
    'делопроизводство:\n    ведение, исполнение\n\n'
    'продажи:\n    лиды, хантинг\n\n'
    'Пример:\n'
    '123456789 ivanov Иван Иванов продажи хантинг нет'
)

USER_DELETE_MESSAGE = 'Отправьте мне id удаляемого сотрудника'

HELP_MESSAGE = (
    'Команды:\n'
    '/users - отобразить список пользователей (admin)\n'
    '/adduser - добавить пользователя (admin)\n'
    '/deluser - удалить пользователя (admin)\n\n'
    'Таблицы:\n'
    'KPI - https://docs.google.com/spreadsheets/d/{}/edit\n\n'
    'план - https://docs.google.com/spreadsheets/d/{}/edit'
)

KPI_MESSAGE = (
    'Привет! Рабочий день закончен, самое время заняться своими делами :)\n'
    'Напоследок, пожалуйста, пришли мне свои цифры за сегодня, '
    'нажав кнопку "показатели \U0001f3af"'
)
KPI_SECOND_MESSAGE = (
    'Через 30 минут руководству будет отправлена '
    'сводка за день, а я так и не получил твоих цифр. Поспеши!'
)
FAIL_MESSAGE = (
    'Я попытался с тобой связаться, '
    'но кажется тебя не добавили в мой список :(\n'
    'Пожалуйста, сообщи об ошибке ответственному лицу'
)
LAWSUITS_MESSAGE = (
    'Наконец-то конец рабочей недели! :)\n'
    'Пожалуйста, проверь на актуальность количество поданных '
    'исков за неделю.\n\nВнести данные можно через кнопку "иски \U0001f5ff"'
)

PLAN_MESSAGE = (
    'Давай выставим план \U0001F60E\n'
    'Пришли мне количество цифр соответствующее числу показателей '
    '(пример: 5 2 ... 10) \U0001F4DD'
)

WEEK_PLAN_MESSAGE = (
    'Привет! Пора выставить план на неделю! \U0001F60E\n'
    'Нажми кнопку на кнопку "мой план \U0001f4b5" чтобы '
    'выставить свой план на эту неделю :)'
)

WEEK_PLAN_SECOND_MESSAGE = (
    'Ты так и не прислал мне свой план на неделю. \n'
    'Нажми кнопку на кнопку "мой план \U0001f4b5" чтобы '
    'выставить свою цель на неделю'
)

DAY_PLAN_MESSAGE = (
    'Давай выставим план на день \U0001F60E\n'
    'Нажми кнопку на кнопку "мой план \U0001f4b5" чтобы '
    'выставить свои цели на день'
)

DAY_PLAN_SECOND_MESSAGE = (
    'Ты так и не прислал мне свои планы на день. \n'
    'Нажми кнопку на кнопку "мой план \U0001f4b5" чтобы '
    'выставить свою цель'
)
