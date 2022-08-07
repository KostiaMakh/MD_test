from datetime import datetime
from rest_framework import serializers
from rest_framework.serializers import ALL_FIELDS
from users.models import User
from companies.models import (
    Company,
    Office,
    Vehicle,
)


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'office',
        )


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ALL_FIELDS


class CompanyVehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            'id',
            'name',
            'model',
            'licence_plate'
        )


class OfficeSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False, required=False)
    employees = DriverSerializer(many=True, required=False)
    vehicles = CompanyVehiclesSerializer(many=True, required=False)

    def create(self, validated_data):
        office = Office.objects.create(
            name=validated_data['name'],
            address=validated_data['address'],
            company=self.context['request'].user.company,
            country=validated_data['country'],
            city=validated_data['city'],
            region=validated_data['region'],
        )
        return office

    class Meta:
        model = Office
        fields = serializers.ALL_FIELDS
        read_only_fields = (
            'id',
            'company',
        )


class VehicleSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(many=True, required=False)

    def validate_year_of_manufactured(self, year_of_manufactured):
        if year_of_manufactured:
            current_year = datetime.now().year
            if year_of_manufactured not in range(1900, current_year):
                raise serializers.ValidationError(
                    {"Vehicle creating error": f"Uncorrect value year_of_manufactured"})

        return year_of_manufactured

    def validate_office(self, office):
        if self.context['request'].method == "PATCH":
            if office:
                # Checking office in request with company offices
                admin_offices = Office.objects.filter(company__pk=self.context['request'].user.company.pk)

                try:
                    admin_offices.get(pk=office.pk)
                except admin_offices.model.DoesNotExist:
                    raise serializers.ValidationError(
                        {"error": f"There is no office id={office.pk} in this company"})

            # If instance office set and instance already have driver - remove driver
            if self.instance.office:
                # If new vehicle office doesn't equal with new office - remove driver
                if self.instance.office != office:
                    drivers = User.objects.filter(vehicles__pk=self.instance.pk)
                    if len(drivers) > 0:
                        for driver in drivers:
                            driver.vehicles.remove(self.instance)
                            driver.save()

        return office

    def create(self, validated_data):
        # Adding admin company in validated_data
        user_company = self.context['request'].user.company
        validated_data['company'] = user_company
        vehicle = Vehicle.objects.create(**validated_data)

        return vehicle

    class Meta:
        model = Vehicle
        fields = serializers.ALL_FIELDS
        read_only_fields = (
            'id',
            'company',
            'driver'
        )


class UserVehicleAddSerializer(serializers.ModelSerializer):
    def user_office_is_set(self):
        # Checking set user office or not
        if not self.instance.office:
            raise serializers.ValidationError(
                {"vehicle adding error": f"User office doesn't set"})

    def check_vehicle_office(self, vk_office_pk):
        # Checking user and vehicle offices registration
        if vk_office_pk != self.instance.office.pk:
            raise serializers.ValidationError(
                {"vehicle adding error": f"Employee and vehicle should be associated with same office"})

    @staticmethod
    def check_vehicle_drivers(exist_drivers):
        # Check set vehicle driver or not
        if exist_drivers:
            raise serializers.ValidationError(
                {"vehicle adding error": f"Vehicle already has driver"})

    @staticmethod
    def input_data_is_exist(attrs):
        # Checking params exist
        if len(attrs) < 1:
            raise serializers.ValidationError(
                {"vehicle adding error": f"There are any vehicles in request"})

    def validate_vehicles(self, vehicles_atr):
        self.input_data_is_exist(vehicles_atr)
        self.user_office_is_set()

        for vehicle in vehicles_atr:
            self.check_vehicle_office(vehicle.office.pk)
            # Get information about adding vehicle
            exist_drivers = User.objects.filter(company__pk=self.instance.company.pk,
                                                vehicles__pk=vehicle.pk)
            self.check_vehicle_drivers(exist_drivers)

        return vehicles_atr

    def update(self, instance, validated_data):
        adding_vehicles = validated_data['vehicles']
        for vehicle in adding_vehicles:
            instance.vehicles.add(vehicle)
            instance.save()

        return instance

    class Meta:
        model = User
        fields = (
            'vehicles',
        )


class UserVehicleRemoveSerializer(UserVehicleAddSerializer):

    def check_user_vehicles(self):
        # Check has user enable vehicles and return them if exist
        vehicles = self.instance.vehicles
        if vehicles.count() == 0:
            raise serializers.ValidationError(
                {"vehicle removing error": f"Employee {self.instance} doesn't has enable vehicles"})

        return vehicles

    @staticmethod
    def check_vehicle_in_user_vehicles(user_vehicles, vehicle):
        # Check include user vehicles removable vehicle
        try:
            user_vehicles.get(pk=vehicle.pk)
        except user_vehicles.model.DoesNotExist:
            raise serializers.ValidationError(
                {"vehicle removing error": f"Vehicle id={vehicle.pk} doesn't in user vehicles"})

    def validate_vehicles(self, vehicles_atr):
        self.input_data_is_exist(vehicles_atr)
        user_vehicles = self.check_user_vehicles()
        for vehicle in vehicles_atr:
            self.check_vehicle_in_user_vehicles(user_vehicles=user_vehicles,
                                                vehicle=vehicle)

        return vehicles_atr

    def update(self, instance, validated_data):
        adding_vehicles = validated_data['vehicles']
        for vehicle in adding_vehicles:
            instance.vehicles.remove(vehicle)
        return instance

    class Meta:
        model = User
        fields = (
            'vehicles',
        )


class VehicleDriverAddSerializer(serializers.ModelSerializer):
    def validate_driver(self, drivers):
        # Checking drivers existing in query
        if not drivers:
            raise serializers.ValidationError({"driver adding error": f"Driver not specified"})

        driver = drivers[0]

        # Checking vehicle office (set or not)
        if len(drivers) > 1:
            raise serializers.ValidationError(
                {"driver adding error": f"You can't set more then one driver for vehicle"})

        # Checking user and vehicle offices registration
        if not self.instance.office or not driver.office:
            raise serializers.ValidationError({"driver adding error": f"Vehicle/driver office doesn't set"})

        # Checking user and vehicle offices registration
        if driver.office.pk != self.instance.office.pk:
            raise serializers.ValidationError(
                {"driver adding error": f"Driver and vehicle should be associated with same office"})

        # Checking existing vehicle drivers
        if self.instance.driver.count() != 0:
            raise serializers.ValidationError({"driver adding error": f"Driver for this vehicle already set"})

        return drivers

    def update(self, instance, validated_data):
        driver = validated_data['driver'][0]
        user = User.objects.get(pk=driver.pk)
        user.vehicles.add(instance)
        user.save()

        return instance

    class Meta:
        model = Vehicle
        fields = (
            'driver',
        )
