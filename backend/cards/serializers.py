from rest_framework import serializers
from cards.models import Tag, Todo

# Simple default implementations for the create() and update() methods.


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'title')


class TagApplySerializer(TagSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=120)


class TodoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    tags = TagApplySerializer(many=True)

    class Meta:
        model = Todo
        fields = ('id', 'owner', 'title', 'description', 'completed', 'tags')

    def get_tags(self, tags: dict) -> list:
        return [tag.get('id') for tag in tags]

    def create(self, validated_data: dict) -> Todo:
        tags = validated_data.pop('tags', None)
        instance = super().create(validated_data)
        instance.tags.set(self.get_tags(tags))
        return instance

    def update(self, instance: Todo, validated_data: dict) -> Todo:
        tags = validated_data.pop('tags', None)
        upd_instance = super().update(instance, validated_data)
        upd_instance.tags.set(self.get_tags(tags))
        return upd_instance
