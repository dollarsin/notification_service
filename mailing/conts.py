STATUS_SENT = 'sent'
STATUS_NOT_SENT = 'not_sent'

STATUS_CHOICES = (
    (STATUS_SENT, 'Отправлено'),
    (STATUS_NOT_SENT, 'Не отправлено'),
)

# Способы доставки
DELIVERY_METHOD_EMAIL = 'email'
DELIVERY_METHOD_SMS = 'sms'
DELIVERY_METHOD_TELEGRAM = 'telegram'

DELIVERY_METHOD_CHOICES = (
    (DELIVERY_METHOD_EMAIL, 'Email'),
    (DELIVERY_METHOD_SMS, 'SMS'),
    (DELIVERY_METHOD_TELEGRAM, 'Telegram'),
)
