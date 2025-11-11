"""
Модуль для отправки уведомлений с fallback механизмом.
Порядок попыток: Email -> SMS -> Telegram
"""
import logging

import requests
from constance import config
from django.core.mail import send_mail
from django.conf import settings

from mailing import conts, models

logger = logging.getLogger('tasks')


class NotificationSender:
    """Класс для отправки уведомлений с fallback механизмом"""
    
    def __init__(self, client: models.Client, text: str, message_id: int):
        self.client = client
        self.text = text
        self.message_id = message_id
        self.delivery_methods = [
            (self._send_email, conts.DELIVERY_METHOD_EMAIL),
            (self._send_sms, conts.DELIVERY_METHOD_SMS),
            (self._send_telegram, conts.DELIVERY_METHOD_TELEGRAM),
        ]
    
    def send(self) -> tuple[bool, str | None]:
        """
        Отправляет уведомление, пробуя разные способы доставки.
        Возвращает (успех, способ_доставки)
        """
        for send_method, method_name in self.delivery_methods:
            try:
                if send_method():
                    logger.info(
                        f'Сообщение {self.message_id} успешно отправлено '
                        f'клиенту {self.client.id} через {method_name}'
                    )
                    return True, method_name
            except Exception as e:
                logger.warning(
                    f'Не удалось отправить сообщение {self.message_id} '
                    f'клиенту {self.client.id} через {method_name}: {e}. '
                    f'Пробуем следующий способ...'
                )
                continue
        
        logger.error(
            f'Не удалось отправить сообщение {self.message_id} '
            f'клиенту {self.client.id} ни одним из способов'
        )
        return False, None
    
    def _send_email(self) -> bool:
        """Отправка через Email"""
        if not self.client.email:
            raise ValueError('У клиента не указан email')
        
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            raise ValueError('Email не настроен в настройках проекта')
        
        send_mail(
            subject='Уведомление',
            message=self.text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.client.email],
            fail_silently=False,
        )
        return True
    
    def _send_sms(self) -> bool:
        """Отправка через SMS (внешний API)"""
        if not config.API_SERVICE_URL or not config.API_SERVICE_TOKEN:
            raise ValueError('SMS сервис не настроен')
        
        response = requests.post(
            url=config.API_SERVICE_URL + str(self.message_id),
            headers={'Authorization': f'Bearer {config.API_SERVICE_TOKEN}'},
            json={
                'id': self.message_id,
                'phone': self.client.phone,
                'text': self.text,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.status_code == requests.codes.ok
    
    def _send_telegram(self) -> bool:
        """Отправка через Telegram"""
        if not self.client.telegram_id:
            raise ValueError('У клиента не указан Telegram ID')
        
        telegram_bot_token = config.TELEGRAM_BOT_TOKEN
        if not telegram_bot_token:
            raise ValueError('Telegram бот не настроен')
        
        # Определяем chat_id
        # Telegram API принимает:
        # - числовой ID (как число или строку)
        # - username с @ или без @
        chat_id = self.client.telegram_id.strip()
        
        # Если это не числовой ID и не начинается с @, добавляем @
        try:
            int(chat_id)
            # Это числовой ID, используем как есть
        except ValueError:
            # Это username, добавляем @ если его нет
            if not chat_id.startswith('@'):
                chat_id = f'@{chat_id}'
        
        telegram_api_url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
        
        response = requests.post(
            url=telegram_api_url,
            json={
                'chat_id': chat_id,
                'text': self.text,
            },
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get('ok'):
            return True
        else:
            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")

