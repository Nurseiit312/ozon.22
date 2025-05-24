
from rest_framework.response import Response
from rest_framework.decorators import api_view

from store.serializers import TelegramUser


@api_view(['GET'])
def user_balance(request, tg_id):
    try:
        tg_user = TelegramUser.objects.get(telegram_id=tg_id)
        return Response({"balance": tg_user.balance})
    except TelegramUser.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)
