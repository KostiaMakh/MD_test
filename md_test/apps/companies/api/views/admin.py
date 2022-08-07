from django.db.models import Count
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet
from users.models import User
from companies.api.serializers.admin import (
    OfficeSerializer,
    CompanySerializer,
    VehicleSerializer,
    UserVehicleAddSerializer,
    UserVehicleRemoveSerializer,
    VehicleDriverAddSerializer,
)
from companies.models import (
    Company,
    Office,
    Vehicle
)


class CompanyAdminApiView(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    An endpoint for company view for admin
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(pk=self.request.user.company.pk)


class OfficeAdminApiView(ModelViewSet):
    """
    An endpoint for office view for admin
    """
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer

    def get_queryset(self):
        offices = Office.objects.filter(company__pk=self.request.user.company.pk)
        offices = offices.prefetch_related('employees')
        offices = offices.prefetch_related('vehicles')
        if self.request.query_params.get('city'):
            offices = offices.filter(city=self.request.query_params.get('city'))
        if self.request.query_params.get('country'):
            offices = offices.filter(country=self.request.query_params.get('country'))
        if self.request.query_params.get('region'):
            offices = offices.filter(region=self.request.query_params.get('region'))

        return offices

    def destroy(self, request, *args, **kwargs):
        # Clear employee vehicles list
        instance = self.get_object()
        office_employees = User.objects.filter(office__pk=instance.pk)
        if len(office_employees) > 0:
            for employee in office_employees:
                employee.vehicles.clear()
        super(OfficeAdminApiView, self).destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_204_NO_CONTENT)


class VehicleAdminApiView(ModelViewSet):
    """
    An endpoint for vehicles view for admin
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        vehicles = Vehicle.objects.filter(company__pk=self.request.user.company.pk)
        vehicles = vehicles.prefetch_related('driver')
        if self.request.query_params.get('office'):
            vehicles = vehicles.filter(office=self.request.query_params.get('office'))
        if self.request.query_params.get('driver'):
            vehicles = vehicles.filter(driver=self.request.query_params.get('driver'))
        return vehicles


class UserVehicleAddApiView(mixins.UpdateModelMixin,
                            GenericViewSet):
    """
    An endpoint for adding vehicle to user (set vehicle)
    """
    queryset = User.objects.all()
    serializer_class = UserVehicleAddSerializer


class UserVehicleRemoveApiView(UserVehicleAddApiView):
    """
    An endpoint for remove vehicle from user vehicles (remove vehicle)
    """
    serializer_class = UserVehicleRemoveSerializer


class VehicleDriverAddApiView(mixins.UpdateModelMixin,
                              GenericViewSet):
    """
    An endpoint for adding driver for vehicle (set driver)
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleDriverAddSerializer

    def get_queryset(self):
        vehicles = Vehicle.objects.filter(company__pk=self.request.user.company.pk)
        vehicles = vehicles.prefetch_related('driver')

        return vehicles


class VehicleDriverRemoveApiView(mixins.DestroyModelMixin,
                                 GenericViewSet):
    """
    An endpoint for adding driver for vehicle (set driver)
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        vehicle = Vehicle.objects.filter(company__pk=self.request.user.company.pk)
        vehicle = vehicle.prefetch_related('driver')

        return vehicle

    def destroy(self, request, *args, **kwargs):
        vehicle = self.get_object()
        if vehicle.driver.count() == 0:
            raise serializers.ValidationError({"driver removing error": f"Vehicle driver doesn't set"})
        else:
            driver = self.get_object().driver.first()
            driver.vehicles.remove(vehicle)
            driver.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
