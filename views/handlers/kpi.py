from typing import Union, Optional

from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardButton

from sheets.handlers.disbonuses import get_user_actual_bonus_value, update_disbonus_for_user
from sheets.handlers.statistics import update_employee_kpi, prepare_kpi_keys_and_questions
from settings import settings, telegram as tele
from utils.statistics import get_user_disbonus_data


class KPIHandler:
    """TODO: docstring"""

    YES_NO_CHOICES = {
        'yes': '\U00002705 - да',
        'no': '\U0000274c - нет',
    }
    DISBONUS_COMMON_CHOICES = {
        'quit': 'закончить',
    }

    def __init__(self, sender_id: str):
        self.sender_id = sender_id
        self.yes_no_markup = ReplyKeyboardMarkup(row_width=2)
        for text in self.YES_NO_CHOICES.values():
            self.yes_no_markup.add(InlineKeyboardButton(text=text))

        self.disbonus_personal_markup = ReplyKeyboardMarkup(row_width=1)
        self.disbonus_personal_markup.add(InlineKeyboardButton(text=self.DISBONUS_COMMON_CHOICES['quit']))

    def _handle_disbonuses(
            self,
            message: Message,
            user_disbonus_data: dict[str, dict[str, Union[int, str]]],
            disbonus_map: dict[str, str],
    ) -> None:
        if message.text == self.DISBONUS_COMMON_CHOICES['quit']:
            user_actual_bonus_value = get_user_actual_bonus_value(user_id=self.sender_id)

            tele.bot.send_message(
                chat_id=self.sender_id,
                text=f'\U00002705 - данные внесены. Ваш бонусный баланс: {user_actual_bonus_value}. Хорошего вечера!',
                reply_markup=tele.main_markup,
            )

            return

        if message.text in disbonus_map.values():

            # FIXME
            for disbonus_id, disbonus_name in disbonus_map.items():
                if disbonus_name == message.text:
                    target_disbonus_id = disbonus_id

            target_disbonus: Optional[str] = None
            keyboard: list[list[dict[str, str]]] = self.disbonus_personal_markup.keyboard

            for button_idx, keyboard_item in enumerate(keyboard):
                disbonus_name = keyboard_item[0]['text']
                if message.text == disbonus_name:
                    target_disbonus = keyboard.pop(button_idx)[0]['text']
                    break

            if target_disbonus:
                tele.bot.send_message(chat_id=self.sender_id, text='\U0001f552 - Вношу данные.')
                update_disbonus_for_user(user_id=self.sender_id, disbonus_id=target_disbonus_id, disbonus_value=1)

                tele.bot.send_message(
                    chat_id=self.sender_id,
                    text='\U0001f4dd - внес. Еще что-нибудь?',
                    reply_markup=self.disbonus_personal_markup,
                )
            else:
                tele.bot.send_message(
                    chat_id=self.sender_id,
                    text='\U00002b07\U0000fe0f - выберите соответствующие дисбонусы, или закончите ввод.',
                )
        else:
            tele.bot.send_message(
                chat_id=self.sender_id,
                text='\U00002b07\U0000fe0f - выберите соответствующие дисбонусы, или закончите ввод.',
            )
        tele.bot.register_next_step_handler(message, self._handle_disbonuses, user_disbonus_data, disbonus_map)

    def _manage_disbonuses_question(self, message: Message) -> None:
        if message.text == self.YES_NO_CHOICES['yes']:
            user_data = get_user_disbonus_data(self.sender_id)

            disbonus_map = {disbonus_id: disbonus_data['name'] for disbonus_id, disbonus_data in user_data.items()}
            for disbonus_name in disbonus_map.values():
                self.disbonus_personal_markup.add(InlineKeyboardButton(text=disbonus_name))

            tele.bot.send_message(
                chat_id=self.sender_id,
                text='\U00002b07\U0000fe0f - выберите соответствующие дисбонусы.',
                reply_markup=self.disbonus_personal_markup,
            )
            tele.bot.register_next_step_handler(message, self._handle_disbonuses, user_data, disbonus_map)
        elif message.text == self.YES_NO_CHOICES['no']:
            user_actual_bonus_value = get_user_actual_bonus_value(user_id=self.sender_id)

            tele.bot.send_message(
                chat_id=self.sender_id,
                text=f'\U00002705 - данные внесены. Ваш бонусный баланс: {user_actual_bonus_value}. Хорошего вечера!',
                reply_markup=tele.main_markup,
            )
        else:
            tele.bot.send_message(self.sender_id, '\U00002b07\U0000fe0f - выберите один из вариантов ответа.')
            tele.bot.register_next_step_handler(message, self._manage_disbonuses_question)

    def _parse_answer(self, message: Message, kpi_keys: list[str]) -> None:
        values_from_user = message.text.split()

        if len(values_from_user) != len(kpi_keys):
            tele.bot.send_message(
                chat_id=self.sender_id,
                text='\U0000274E - количество показателей не соответствует числу вопросов. Попробуйте еще раз.',
            )
            return

        if list(filter(lambda item: not item.isnumeric(), values_from_user)):
            tele.bot.send_message(
                chat_id=self.sender_id,
                text='\U0000274E - неверный формат показателей. Попробуйте еще раз.',
            )
            return

        tele.bot.send_message(self.sender_id, '\U0001f552 - вношу данные.')

        data = list(zip(kpi_keys, values_from_user))
        update_employee_kpi(self.sender_id, data)
        tele.bot.send_message(
            chat_id=self.sender_id,
            text='\U00002753 - Были ли сегодня дисбонусы?',
            reply_markup=self.yes_no_markup,
        )
        tele.bot.register_next_step_handler(message, self._manage_disbonuses_question)

    def receive_kpi(self, message: Message):
        """TODO: docstring"""
        kpi_keys, kpi_questions = prepare_kpi_keys_and_questions(self.sender_id)
        if len(kpi_keys) == 0:
            tele.bot.send_message(
                chat_id=self.sender_id,
                text='\U0001F44C - сегодня у вас не нет запланированных отчетов. Спасибо!',
            )
            return

        questions_str = '\n'.join([f'{order + 1}. {question}' for order, question in enumerate(kpi_questions)])
        text = '\U0001F4CB - пришлите следующие количественные данные одним сообщением, ' \
               f'согласно приведенному порядку. Разделяйте числа пробелами:\n\n{questions_str}',
        tele.bot.send_message(self.sender_id, text)

        tele.bot.register_next_step_handler(message, self._parse_answer, kpi_keys)

    @staticmethod
    def build_result_message_bonuses() -> str:
        """TODO: docstring"""
        user_ids = [
            (str(user_id), f'{user_data["firstname"]} {user_data["lastname"]}')
            for user_id, user_data in settings.config['employees'].items()
            if user_data['bonuses']
        ]

        messages_batch = ['\U0001f4b0 - бонусный баланс по сотрудникам:\n']
        for user_id, user_name in user_ids:
            user_bonus_value = get_user_actual_bonus_value(user_id=user_id)
            messages_batch.append(f'\t\t\t{user_name} -> {user_bonus_value}')

        return '\n'.join(messages_batch)

    @staticmethod
    def get_users_ids_with_empty_kpi_data() -> list[str]:
        """
        TODO: currently a plug and returns all users who's kpi is being tracked.
        Should be refactored to return only users who's kpi is not filled yet.
        """
        users_with_empty_kpi_data: list[str] = [
            user_id
            for user_id, user_data in settings.config['employees'].items()
            if user_data['statistics'] is not None and user_data['statistics']['kpi'] is not None
        ]

        return users_with_empty_kpi_data
