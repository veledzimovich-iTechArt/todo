from django.db.models.query import QuerySet

from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets

from cards.serializers import TagSerializer, TodoSerializer
from cards.models import Tag, Todo
from cards.permissions import IsOwnerOrReadOnly

# Create your views here.

# ModelViewSet(mixins.CreateModelMixin,
#                    mixins.RetrieveModelMixin,
#                    mixins.UpdateModelMixin,
#                    mixins.DestroyModelMixin,
#                    mixins.ListModelMixin,
#                    GenericViewSet):
# GenericViewSet(ViewSetMixin, generics.GenericAPIView)


class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [
        # for list
        permissions.IsAuthenticatedOrReadOnly,
        # for object allows to edit only for the owner
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self) -> QuerySet:
        tags = self.request.query_params.getlist('tags')
        queryset = (
            Todo.objects
            .filter(owner_id=self.request.user.id)
            .select_related('owner')
            .prefetch_related('tags')
        )
        return (
            queryset.filter(tags__id__in=tags).distinct()
            if tags else queryset
        )

    def perform_create(self, serializer: TodoSerializer) -> None:
        serializer.validated_data['owner'] = self.request.user
        super().perform_create(serializer)


class TagView(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self) -> QuerySet:
        title = self.request.query_params.get('title')
        return (
            Tag.objects.all()
            if title is None else
            Tag.objects.filter(title=title)
        )
