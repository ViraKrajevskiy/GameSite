from rest_framework import serializers
from Backend.models.comments_model.vlogs_coment import VlogsComment


class VlogsCommentSerializer(serializers.ModelSerializer):
    vl_comment_author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VlogsComment
        fields = ['id', 'vlogs', 'vl_comment_author', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'vl_comment_author', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['vl_comment_author'] = self.context['request'].user
        return super().create(validated_data)