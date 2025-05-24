from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.views import CategoryViewSet, ProductViewSet, OrderViewSet, get_balance
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="OzonShop API",
      default_version='v1',
      description="Документация API интернет-магазина",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # <-- admin импортирован, теперь здесь ошибки не будет
    path('api/', include(router.urls)),
    path('api/telegram-users/<int:telegram_id>/balance/', get_balance, name='get_balance'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('swagger(<format>\\.json|\\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
