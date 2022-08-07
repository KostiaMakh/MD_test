from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from users.models import User
from users.api.serializers.user import (
    UserSerializer,
    UserUpdateSerializer,
)


class UserProfileApiView(mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    """
    An endpoint for user profile
    """
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        elif self.request.method == "PATCH":
            return UserUpdateSerializer

    def get_queryset(self):
        user = User.objects.filter(pk=self.request.user.pk)

        return user
