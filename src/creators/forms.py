from django import forms
from django.db.models import Q

from content.models import Chapter, Course, Lesson, Material, ResourceVersion, Video
from media.models import Asset

from .models import CreatorProfile


class ProfileForm(forms.ModelForm):
    accept_rights = forms.BooleanField(label="Me comprometo a publicar materiales propios o con autorización y atender las observaciones de revisión.")

    class Meta:
        model = CreatorProfile
        fields = ("display_name", "bio", "specialty", "website")


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "kind", "description", "objective", "requirements", "topic", "level", "estimated_minutes")


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
        fields = ("title", "description", "body", "access_type", "position", "status")

    def clean_position(self):
        position = self.cleaned_data["position"]
        if Lesson.objects.filter(chapter_id=self.instance.chapter_id, position=position).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este orden ya lo ocupa otra lección. Elige un número libre.")
        return position

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        # Only approved current revisions can be attached to an educational draft.
        video_ids = Video.objects.filter(creator=actor, revision__isnull=False).values_list("revision_id", flat=True)
        material_ids = Material.objects.filter(creator=actor, revision__isnull=False).values_list("revision_id", flat=True)
        self.fields["resources"].queryset = ResourceVersion.objects.filter(creator=actor).filter(Q(pk__in=video_ids) | Q(pk__in=material_ids)).order_by("title", "number")
        if self.instance.pk:
            existing = self.instance.attachments.values_list("resource_id", flat=True)
            self.fields["resources"].queryset = ResourceVersion.objects.filter(creator=actor).filter(Q(pk__in=video_ids) | Q(pk__in=material_ids) | Q(pk__in=existing)).order_by("title", "number")
            self.initial["resources"] = list(existing)


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ("title", "description", "topic", "access_type", "pending_asset", "pending_subtitles", "transcript")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        kind = "video" if isinstance(self.instance, Video) else "material"
        self.fields["pending_asset"].queryset = Asset.objects.filter(creator=actor, kind=kind)
        self.fields["pending_asset"].required = True
        self.fields["pending_subtitles"].queryset = Asset.objects.filter(creator=actor, kind="subtitle")
        if kind == "material":
            self.fields.pop("pending_subtitles")


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
