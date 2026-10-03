from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import (
    Chapter,
    Course,
    CourseVersion,
    ExternalReference,
    Lesson,
    LessonResource,
    Material,
    ResourceVersion,
    Topic,
    Video,
)
from .publication import publish_course, publish_resource


class ChapterInline(admin.TabularInline):
    model = Chapter
    fields = ("title", "position", "status")
    extra = 0
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    fields = ("title", "position", "status", "access_type")
    extra = 0
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "status", "updated_at")
    list_filter = ("status", "kind", "topic", "level")
    search_fields = ("title", "creator__email")
    autocomplete_fields = ("creator",)
    readonly_fields = ("created_at", "updated_at", "current_version")
    inlines = (ChapterInline,)
    actions = ("publish_version",)

    @admin.action(description="Publicar una nueva versión del curso")
    def publish_version(self, request, queryset):
        for course in queryset:
            try:
                version = publish_course(course, request.user)
            except ValidationError as exc:
                self.message_user(request, f"{course.title}: {'; '.join(exc.messages)}", level=messages.ERROR)
            else:
                self.message_user(request, f"{version} publicada. Las versiones anteriores se conservan.")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "position", "status")
    list_filter = ("status", "course")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (LessonInline,)


class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0
    autocomplete_fields = ("resource",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "position", "status", "access_type")
    list_filter = ("status", "access_type")
    search_fields = ("title", "chapter__title", "chapter__course__title")
    autocomplete_fields = ("chapter",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (LessonResourceInline,)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "status", "access_type")
    list_filter = ("status", "access_type")
    search_fields = ("title", "creator__email")
    autocomplete_fields = ("creator",)
    readonly_fields = ("created_at", "updated_at", "revision")
    actions = ("publish_revision",)

    @admin.action(description="Validar archivo y publicar una nueva revisión")
    def publish_revision(self, request, queryset):
        for resource in queryset:
            try:
                revision = publish_resource(resource, request.user)
            except ValidationError as exc:
                self.message_user(request, f"{resource.title}: {'; '.join(exc.messages)}", level=messages.ERROR)
            else:
                self.message_user(request, f"{revision} publicada.")


class RevisionAdmin(admin.ModelAdmin):
    search_fields = ("title",)

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Video, ResourceAdmin)
admin.site.register(Material, ResourceAdmin)
admin.site.register(Topic)
admin.site.register(ExternalReference)
admin.site.register(ResourceVersion, RevisionAdmin)
admin.site.register(CourseVersion, RevisionAdmin)
