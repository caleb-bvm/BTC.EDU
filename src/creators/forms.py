from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from content.education import EDUCATION_FIELDS
from content.models import (
    Chapter,
    Course,
    Lesson,
    Material,
    ResourceVersion,
    Topic,
    Video,
)
from media.models import Asset

from .models import CreatorProfile


def education_widgets(form):
    for field in EDUCATION_FIELDS:
        if field != "activity_kind":
            form.fields[field].widget = forms.Textarea(attrs={"rows": 3})


def group_topic_choices(form):
    field = form.fields["topic"]
    field.label = "Subcategoría"
    field.queryset = Topic.objects.select_related("category").order_by("category__name", "name", "pk")
    grouped = {}
    unassigned = []
    for topic in field.queryset:
        if topic.category_id is None:
            unassigned.append((topic.pk, topic.name))
        else:
            grouped.setdefault(topic.category.name, []).append((topic.pk, topic.name))
    field.choices = [("", "Sin subcategoría"), *grouped.items()]
    if unassigned:
        field.choices = [*field.choices, ("Otros temas", unassigned)]


class ProfileForm(forms.ModelForm):
    application_revision = forms.IntegerField(required=False, min_value=0, widget=forms.HiddenInput)
    accept_rights = forms.BooleanField(label="Me comprometo a publicar materiales propios o con autorización y atender las observaciones de revisión.")

    class Meta:
        model = CreatorProfile
        fields = ("display_name", "bio", "specialty", "website")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["application_revision"].initial = self.instance.review_revision
        self.fields["bio"].widget = forms.Textarea(attrs={"rows": 5, "maxlength": 2000})
        self.fields["bio"].max_length = 2000


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "kind", "description", "objective", "requirements", "topic", "level", "estimated_minutes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        group_topic_choices(self)


class ChapterForm(forms.ModelForm):
    status = forms.ChoiceField(label="En el temario", choices=(("published", "Incluir en la próxima versión"), ("draft", "Guardar para después")))

    class Meta:
        model = Chapter
        fields = ("title", "description", "position", "status")

    def clean_position(self):
        position = self.cleaned_data["position"]
        if Chapter.objects.filter(course_id=self.instance.course_id, position=position).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este orden ya lo ocupa otro capítulo. Elige un número libre.")
        return position


class LessonForm(forms.ModelForm):
    status = forms.ChoiceField(label="En el temario", choices=(("published", "Incluir en la próxima versión"), ("draft", "Guardar para después")))
    resources = forms.ModelMultipleChoiceField(queryset=ResourceVersion.objects.none(), label="Videos y materiales revisados", required=False)

    class Meta:
        model = Lesson
        fields = ("title", "description", *EDUCATION_FIELDS, "body", "access_type", "position", "status")

    def clean_position(self):
        position = self.cleaned_data["position"]
        if Lesson.objects.filter(chapter_id=self.instance.chapter_id, position=position).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este orden ya lo ocupa otra lección. Elige un número libre.")
        return position

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        education_widgets(self)
        # Only approved current revisions can be attached to an educational draft.
        video_ids = Video.objects.filter(creator=actor, revision__isnull=False).values_list("revision_id", flat=True)
        material_ids = Material.objects.filter(creator=actor, revision__isnull=False).values_list("revision_id", flat=True)
        self.fields["resources"].queryset = ResourceVersion.objects.filter(creator=actor).filter(Q(pk__in=video_ids) | Q(pk__in=material_ids)).order_by("title", "number")
        if self.instance.pk:
            existing = self.instance.attachments.values_list("resource_id", flat=True)
            self.fields["resources"].queryset = ResourceVersion.objects.filter(creator=actor).filter(Q(pk__in=video_ids) | Q(pk__in=material_ids) | Q(pk__in=existing)).order_by("title", "number")
            self.initial["resources"] = list(existing)


class ResourceForm(forms.ModelForm):
    new_file = forms.FileField(label="Cargar un archivo nuevo", required=False, help_text="Selecciona un archivo de tu equipo o elige uno de tu biblioteca más abajo.")
    new_subtitles = forms.FileField(label="Cargar subtítulos nuevos", required=False, help_text="Archivo VTT en español; también puedes elegir uno de tu biblioteca.")

    class Meta:
        model = Video
        fields = ("title", "description", *EDUCATION_FIELDS, "topic", "access_type", "pending_asset", "pending_subtitles", "transcript")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.uploaded_assets = {}
        education_widgets(self)
        group_topic_choices(self)
        kind = "video" if isinstance(self.instance, Video) else "material"
        self.fields["pending_asset"].queryset = Asset.objects.filter(creator=actor, kind=kind)
        self.fields["pending_asset"].required = False
        self.fields["pending_asset"].label = "O elegir de mi biblioteca"
        self.fields["pending_subtitles"].queryset = Asset.objects.filter(creator=actor, kind="subtitle")
        if kind == "material":
            self.fields.pop("pending_subtitles")
            self.fields.pop("new_subtitles")

    def clean(self):
        values = super().clean()
        kind = "video" if isinstance(self.instance, Video) else "material"
        for upload_field, target, expected in (("new_file", "pending_asset", kind), ("new_subtitles", "pending_subtitles", "subtitle")):
            upload = values.get(upload_field)
            if not upload:
                continue
            asset = Asset(creator=self.actor, file=upload)
            try:
                asset.clean()
                if asset.kind != expected:
                    raise ValidationError("El formato del archivo no corresponde a este recurso.")
            except ValidationError as exc:
                self.add_error(upload_field, exc)
            else:
                self.uploaded_assets[target] = asset
        if not values.get("pending_asset") and "pending_asset" not in self.uploaded_assets:
            self.add_error("pending_asset", "Carga un archivo o selecciona uno de tu biblioteca.")
        return values

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field, asset in self.uploaded_assets.items():
            asset.save()
            setattr(instance, field, asset)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class MaterialForm(ResourceForm):
    class Meta(ResourceForm.Meta):
        model = Material


class UploadForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ("file",)


class DecisionForm(forms.Form):
    decision = forms.ChoiceField(label="Decisión", choices=(("approve", "Aprobar y publicar"), ("changes", "Solicitar cambios")))
    feedback = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea)

    def clean(self):
        values = super().clean()
        if values.get("decision") == "changes" and not values.get("feedback", "").strip():
            self.add_error("feedback", "Indica qué debe corregirse.")
        return values
