from django.contrib import admin
from django.contrib.admin import ModelAdmin
from rest_framework.request import Request
from rest_framework.response import Response

from mailing import models
from mailing.datatools.message_statistics import get_message_statistics
from mailing.serializers import MailingStatistic


class TagInline(admin.TabularInline):
    model = models.Mailing.tags.through


class MobileOperatorInline(admin.TabularInline):
    model = models.Mailing.operators.through


@admin.register(models.MailingSummary)
class MailingSummaryAdmin(ModelAdmin):
    """
    Кастомная страница с статистикой по рассылкам
    """
    change_list_template = 'mailing/admin/mailing_summary.html'

    def changelist_view(
            self, request: Request, extra_context=None
    ) -> Response:
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        data = get_message_statistics()
        serializer = MailingStatistic(data, many=True)
        response.context_data['summary'] = serializer.data
        return response


@admin.register(models.Message)
class Message(ModelAdmin):
    list_display = ('status', 'delivery_method', 'mailing', 'client', 'dc')
    search_fields = ('status', 'mailing__id', 'client__phone', 'delivery_method')
    list_filter = ('status', 'delivery_method')
    readonly_fields = ('dc',)
    search_help_text = 'Поиск по: статусу, способу доставки, id рассылки, номер телефона'


@admin.register(models.Client)
class Client(ModelAdmin):
    list_display = ('phone', 'email', 'telegram_id', 'operator', 'tag', 'timezone')
    search_fields = ('phone', 'email', 'telegram_id', 'operator__name', 'tag__name', 'timezone')
    search_help_text = ('Поиск по: номеру телефона, email, telegram_id, оператору, '
                        'тэгу и часовому поясу')


@admin.register(models.MobileOperator)
class MobileOperator(ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    search_help_text = 'Поиск по: названию и коду'


@admin.register(models.Mailing)
class Mailing(ModelAdmin):
    list_display = ('id', 'date_begin', 'date_end')
    search_fields = ('tags__name', 'operators__name')
    search_help_text = 'Поиск по: тегу и оператору'
    inlines = [TagInline, MobileOperatorInline]
    exclude = ('tags', 'operators')


@admin.register(models.Tag)
class Tag(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
