from django.contrib import admin
from django.db.models.query import QuerySet
from rest_framework.request import Request

from cards.models import Todo, Tag


# Register your models here.
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_tags', 'completed')
    fields = ('owner', 'title', 'description', 'completed', 'tags')

    def get_queryset(self, request: Request) -> QuerySet:
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('tags')
        return queryset

    def get_tags(self, value: Todo) -> str:
        lst = [t.title for t in value.tags.all()]
        return ' '.join(lst)
    get_tags.short_description = 'Tags'


class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_count')
    fields = ('title', 'get_todos')
    readonly_fields = ('get_todos',)

    def get_queryset(self, request: Request) -> QuerySet:
        return super().get_queryset(request).prefetch_related('tags')

    def get_todos(self, value: Tag) -> str:
        lst = [t.title for t in value.todo_set.all()]
        return '\n'.join(lst)
    get_todos.short_description = 'Todos'

    def get_count(self, value: Tag) -> str:
        return str(value.todo_set.count())
    get_count.short_description = 'Count'


admin.site.register(Todo, TodoAdmin)
admin.site.register(Tag, TagAdmin)
