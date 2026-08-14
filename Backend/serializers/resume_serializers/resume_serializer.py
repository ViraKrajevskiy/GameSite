from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from Backend.models.resume_model.resume_model import Resume


def _pick(obj, field, lang):
    """Берёт поле нужного языка, а если оно пустое — откатывается на русское."""
    value = getattr(obj, f'{field}_{lang}', '') or ''
    if not value and lang != 'ru':
        value = getattr(obj, f'{field}_ru', '') or ''
    return value


def _lines(text):
    """Многострочное поле → список непустых строк."""
    return [line.strip() for line in (text or '').splitlines() if line.strip()]


def build_resume(resume, lang):
    """Собирает резюме в том виде, в каком его ждёт страница /about на фронте."""
    return {
        'eyebrow': _pick(resume, 'eyebrow', lang),
        'name': _pick(resume, 'name', lang),
        'role': _pick(resume, 'role', lang),
        'tagline': _pick(resume, 'tagline', lang),

        'contactsTitle': _pick(resume, 'contacts_title', lang),
        'contacts': [
            {
                'label': _pick(contact, 'label', lang),
                'value': contact.value,
                'href': contact.url,
            }
            for contact in resume.contacts.all()
        ],

        'factsTitle': _pick(resume, 'facts_title', lang),
        'facts': [
            {'num': fact.num, 'lab': _pick(fact, 'label', lang)}
            for fact in resume.facts.all()
        ],

        'aboutTitle': _pick(resume, 'about_title', lang),
        'about': _lines(_pick(resume, 'about', lang)),

        'stackTitle': _pick(resume, 'stack_title', lang),
        'stack': [
            {'group': _pick(group, 'title', lang), 'items': group.items_list}
            for group in resume.skill_groups.all()
        ],

        'expTitle': _pick(resume, 'exp_title', lang),
        'experience': [
            {
                'period': _pick(job, 'period', lang),
                'company': job.company,
                'place': _pick(job, 'place', lang),
                'title': _pick(job, 'title', lang),
                'points': _lines(_pick(job, 'points', lang)),
                'stack': job.stack,
            }
            for job in resume.experience.all()
        ],

        'projTitle': _pick(resume, 'proj_title', lang),
        'projects': [
            {
                'name': project.name,
                'kind': _pick(project, 'kind', lang),
                'desc': _pick(project, 'description', lang),
                'links': [
                    {'label': _pick(link, 'label', lang), 'href': link.url}
                    for link in project.links.all()
                ],
            }
            for project in resume.projects.all()
        ],

        'eduTitle': _pick(resume, 'edu_title', lang),
        'education': [
            {
                'year': item.year,
                'place': item.place,
                'detail': _pick(item, 'detail', lang),
            }
            for item in resume.education.all()
        ],

        'langTitle': _pick(resume, 'lang_title', lang),
        'languages': [
            {'name': _pick(item, 'name', lang), 'level': _pick(item, 'level', lang)}
            for item in resume.languages.all()
        ],

        'ctaTitle': _pick(resume, 'cta_title', lang),
        'ctaText': _pick(resume, 'cta_text', lang),
        'ctaBtn': _pick(resume, 'cta_btn1_text', lang),
        'ctaBtnUrl': resume.cta_btn1_url,
        'ctaBtn2': _pick(resume, 'cta_btn2_text', lang),
        'ctaBtn2Url': resume.cta_btn2_url,
    }


class _LabelValueSerializer(serializers.Serializer):
    label = serializers.CharField(allow_blank=True)
    value = serializers.CharField(allow_blank=True)
    href = serializers.CharField(allow_blank=True)


class _ExperienceSerializer(serializers.Serializer):
    period = serializers.CharField(allow_blank=True)
    company = serializers.CharField(allow_blank=True)
    place = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True)
    points = serializers.ListField(child=serializers.CharField())
    stack = serializers.CharField(allow_blank=True)


class _ProjectSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    kind = serializers.CharField(allow_blank=True)
    desc = serializers.CharField(allow_blank=True)
    links = serializers.ListField(child=serializers.DictField())


class ResumeLangSerializer(serializers.Serializer):
    """
    Форма резюме для одного языка — то, что возвращает build_resume.

    Нужна ради схемы: drf-spectacular не выводит тип из
    SerializerMethodField, и ru/en уходили в OpenAPI строками,
    хотя это объекты.
    """
    eyebrow = serializers.CharField(allow_blank=True)
    name = serializers.CharField(allow_blank=True)
    role = serializers.CharField(allow_blank=True)
    tagline = serializers.CharField(allow_blank=True)

    contactsTitle = serializers.CharField(allow_blank=True)
    contacts = _LabelValueSerializer(many=True)

    factsTitle = serializers.CharField(allow_blank=True)
    facts = serializers.ListField(child=serializers.DictField())

    aboutTitle = serializers.CharField(allow_blank=True)
    about = serializers.ListField(child=serializers.CharField())

    stackTitle = serializers.CharField(allow_blank=True)
    stack = serializers.ListField(child=serializers.DictField())

    expTitle = serializers.CharField(allow_blank=True)
    experience = _ExperienceSerializer(many=True)

    projTitle = serializers.CharField(allow_blank=True)
    projects = _ProjectSerializer(many=True)

    eduTitle = serializers.CharField(allow_blank=True)
    education = serializers.ListField(child=serializers.DictField())

    langTitle = serializers.CharField(allow_blank=True)
    languages = serializers.ListField(child=serializers.DictField())

    ctaTitle = serializers.CharField(allow_blank=True)
    ctaText = serializers.CharField(allow_blank=True)
    ctaBtn = serializers.CharField(allow_blank=True)
    ctaBtnUrl = serializers.CharField(allow_blank=True)
    ctaBtn2 = serializers.CharField(allow_blank=True)
    ctaBtn2Url = serializers.CharField(allow_blank=True)


class ResumeSerializer(serializers.ModelSerializer):
    """Отдаёт резюме сразу на двух языках: {"ru": {...}, "en": {...}}."""

    ru = serializers.SerializerMethodField()
    en = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['ru', 'en', 'updated_at']

    @extend_schema_field(ResumeLangSerializer)
    def get_ru(self, obj):
        return build_resume(obj, 'ru')

    @extend_schema_field(ResumeLangSerializer)
    def get_en(self, obj):
        return build_resume(obj, 'en')
