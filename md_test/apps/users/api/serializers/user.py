from rest_framework import serializers
from users.models import User
from companies.api.serializers.admin import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying users profile information
    """
    company = CompanySerializer(many=False)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'office',
            'company',
            'vehicles'
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name'
        )
