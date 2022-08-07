from rest_framework import serializers
from companies.models import (
    Company,
    Office,
    Vehicle
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = serializers.ALL_FIELDS


class OfficeSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False)

    class Meta:
        model = Office
        fields = serializers.ALL_FIELDS


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = serializers.ALL_FIELDS
