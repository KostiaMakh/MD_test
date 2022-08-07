from django.contrib.auth import authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from users.models import User
from companies.api.serializers.admin import CompanySerializer
from companies.models import (
    Company,
    Vehicle,
)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "company",
            "last_login",
            "email",
            "first_name",
            "last_name",
            "office",
            "vehicles"
        )


class EmployeeUpdateSerializer(serializers.ModelSerializer):

    def validate_office(self, office):
        if self.instance.office and office:
            if self.instance.office.pk != office.pk:
                self.instance.vehicles.clear()
                self.instance.save()

        return office

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'office',
        )


class EmployeeCreateSerializer(serializers.ModelSerializer):
    password_repeat = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'password_repeat',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password_repeat': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] and attrs['password_repeat']:
            if attrs['password'] == attrs['password_repeat']:
                return attrs
            else:
                raise serializers.ValidationError({"password_error": "Passwords are not equals"})

    def create(self, validated_data):
        user = User.objects.create_employee(
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.company = self.context['request'].user.company
        user.save()

        return user


class AdminCreateSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False)
    password_repeat = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'password_repeat',
            'first_name',
            'last_name',
            'company'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password_repeat': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({"password_error": "Passwords are not equals"})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_admin(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        company = Company.objects.create(
            name=validated_data['company']['name'],
            address=validated_data['company']['address']
        )
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.company = company
        user.save()

        return user


class AdminSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False)

    class Meta:
        model = User
        fields = (
            "id",
            "company",
            "last_login",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_admin",
            "office",
            "vehicles"
        )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_repeat = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_repeat']:
            raise serializers.ValidationError({"password_error": "password and password repeat aren't equal"})
        print(attrs['old_password'])
        print(self.context['request'].user)
        if not self.context['request'].user.check_password(raw_password=attrs['old_password']):
            raise serializers.ValidationError({"password_error": "wrong password"})

        return attrs


class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Custom view for getting token
    """
    email = serializers.CharField(
        label=_("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
