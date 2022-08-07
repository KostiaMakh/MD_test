from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from companies.api.serializers.user import (
    OfficeSerializer,
    CompanySerializer,
    VehicleSerializer,
)
from companies.models import (
    Company,
    Office,
    Vehicle
)


class BaseUserApiView(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    Base abstract class which defines permissions for user in company
    """

    def get_permissions(self):
        return [IsAuthenticated(), ]


class CompanyUserApiView(BaseUserApiView):
    """
    An endpoint for company view for user
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(
            pk=self.request.user.company.pk
        )


class OfficeUserApiView(BaseUserApiView):
    """
    An endpoint for office view for user
    """
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer

    def get_queryset(self):
        if self.request.user.office:
            return Office.objects.filter(pk=self.request.user.office.pk)


class VehicleUserApiView(BaseUserApiView):
    """
    An endpoint for vehicle view for user
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        vehicles = Vehicle.objects.filter(pk__in=self.request.user.vehicles.values().values('pk'))

        return vehicles
