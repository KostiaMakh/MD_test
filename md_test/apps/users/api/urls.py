from django.urls import path, include
from rest_framework import routers
from users.api.views.user import UserProfileApiView
from users.api.views.admin import (
    EmployeeApiView,
    AdminProfileApiView,
    ChangeAdminPasswordApiView,
    CustomObtainAuthToken,
)

admin_router = routers.DefaultRouter()
admin_router.register('profile', AdminProfileApiView)
admin_router.register('employee', EmployeeApiView)

user_router = routers.DefaultRouter()
user_router.register('profile', UserProfileApiView)

urlpatterns = [
    path('api-auth-token/', CustomObtainAuthToken.as_view()),
    path('change-password/', ChangeAdminPasswordApiView.as_view({'patch': 'update'})),
    path('admin/', include(admin_router.urls)),
    path('user/', include(user_router.urls))
]
