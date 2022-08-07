from django.urls import path, include
from rest_framework import routers
from companies.api.views.admin import (
    OfficeAdminApiView,
    VehicleAdminApiView,
    CompanyAdminApiView,
    UserVehicleAddApiView,
    UserVehicleRemoveApiView,
    VehicleDriverAddApiView,
    VehicleDriverRemoveApiView
)
from companies.api.views.user import (
    OfficeUserApiView,
    VehicleUserApiView,
    CompanyUserApiView,
)

admin_router = routers.DefaultRouter()
admin_router.register('company', CompanyAdminApiView)
admin_router.register('office', OfficeAdminApiView)
admin_router.register('vehicle', VehicleAdminApiView)
admin_router.register('vehicle/set-driver', VehicleDriverAddApiView)
admin_router.register('vehicle/remove-driver', VehicleDriverRemoveApiView)
admin_router.register('employee/add-vehicle', UserVehicleAddApiView)
admin_router.register('employee/remove-vehicle', UserVehicleRemoveApiView)

user_router = routers.DefaultRouter()
user_router.register('company', CompanyUserApiView)
user_router.register('office', OfficeUserApiView)
user_router.register('vehicle', VehicleUserApiView)

urlpatterns = [
    path('user/', include(user_router.urls)),
    path('admin/', include(admin_router.urls)),
]
