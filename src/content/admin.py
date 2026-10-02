from django.contrib import admin

from .models import Chapter, Course, Lesson, Material, Video


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
    list_filter = ("status",)
    search_fields = ("title", "creator__email")
    autocomplete_fields = ("creator",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (ChapterInline,)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "position", "status")
    list_filter = ("status", "course")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (LessonInline,)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "position", "status", "access_type")
    list_filter = ("status", "access_type")
    search_fields = ("title", "chapter__title", "chapter__course__title")
    autocomplete_fields = ("chapter",)
    readonly_fields = ("created_at", "updated_at")


class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "status", "access_type")
    list_filter = ("status", "access_type")
    search_fields = ("title", "creator__email")
    autocomplete_fields = ("creator",)
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Video, ResourceAdmin)
admin.site.register(Material, ResourceAdmin)
