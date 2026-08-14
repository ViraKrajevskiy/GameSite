from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Backend.models.resume_model.resume_model import Resume, ResumeProject
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone
from Backend.serializers.resume_serializers.resume_serializer import ResumeSerializer


class ResumeView(APIView):
    """
    GET /api/resume/ — активное резюме для страницы «О нас».

    Редактируется через админку (/admin/ → Резюме), API только читает.
    """

    permission_classes = [ReadOnlyForEveryone]
    serializer_class = ResumeSerializer

    def get(self, request):
        resume = (
            Resume.objects
            .filter(is_active=True)
            .prefetch_related(
                'contacts', 'facts', 'skill_groups', 'experience', 'education', 'languages',
                Prefetch('projects', queryset=ResumeProject.objects.prefetch_related('links')),
            )
            .order_by('-updated_at')
            .first()
        )

        if resume is None:
            return Response(
                {'detail': 'Активное резюме не найдено.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ResumeSerializer(resume).data)
