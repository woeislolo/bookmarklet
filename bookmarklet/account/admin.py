from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo', 'get_preview_photo',]
    raw_id_fields = ['user']

    def get_preview_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=60>")
        return None

    get_preview_photo.short_description = 'Превью фото'
