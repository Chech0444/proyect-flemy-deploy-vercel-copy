from django.contrib import admin

from courses.models import Course, Lesson, Section


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "is_premium", "is_published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "is_premium", "order")
