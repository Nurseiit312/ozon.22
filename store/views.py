from rest_framework import viewsets

from . import serializers
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, TelegramUser
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        request = self.request
        telegram_id = request.data.get('telegram_id')
        items = request.data.get('items', [])


        total = 0
        for item in items:
            product = Product.objects.get(id=item['product'])
            total += product.price * item['quantity']


        try:
            tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            raise serializers.ValidationError("Telegram-пользователь не найден.")


        if tg_user.balance < total:
            raise serializers.ValidationError("Недостаточно средств для покупки.")


        tg_user.balance -= total
        tg_user.save()


        serializer.save()


from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def user_balance(request, tg_id):
    try:
        tg_user = TelegramUser.objects.get(telegram_id=tg_id)
        return Response({"balance": tg_user.balance})
    except TelegramUser.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)
