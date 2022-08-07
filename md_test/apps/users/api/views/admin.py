from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from users.models import User
from companies.models import Company
from users.api.serializers.admin import (
    AdminCreateSerializer,
    AdminSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeeSerializer,
    ChangePasswordSerializer,
    CustomAuthTokenSerializer,
)


class AdminProfileApiView(ModelViewSet):
    """
    An endpoint for admin profile
    """
    queryset = User.objects.all()
    serializer_class = AdminSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminCreateSerializer
        else:
            return AdminSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny(), ]
        else:
            return [permission() for permission in self.permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        admin_company = Company.objects.get(pk=instance.company.pk)
        admin_company.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeApiView(ModelViewSet):
    """
    An endpoint for displaying information about employee of admin company
    """
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EmployeeCreateSerializer
        elif self.request.method == "PATCH":
            return EmployeeUpdateSerializer
        else:
            return EmployeeSerializer

    def get_queryset(self):
        users = User.objects.filter(company__pk=self.request.user.company.pk)
        if self.request.query_params.get('first_name'):
            users = users.filter(first_name=self.request.query_params.get('first_name'))
        if self.request.query_params.get('last_name'):
            users = users.filter(last_name=self.request.query_params.get('last_name'))
        if self.request.query_params.get('email'):
            users = users.filter(email=self.request.query_params.get('email'))

        return users

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_admin:
            return Response({"error": ["User is admin. You can't delete admin by this request"]},
                            status=status.HTTP_400_BAD_REQUEST)

        return super(EmployeeApiView, self).destroy(request, *args, **kwargs)


class ChangeAdminPasswordApiView(mixins.UpdateModelMixin,
                                 GenericViewSet):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    model = User

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.data.get("new_password"))
        user.save()

        return Response(
            {"password": ["Password successfully changed"]},
            status=status.HTTP_200_OK
        )


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom API view for getting token
    """
    permission_classes = [AllowAny, ]
    serializer_class = CustomAuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="email",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )
