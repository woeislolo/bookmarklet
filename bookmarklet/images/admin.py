from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'total_likes', 'get_preview_photo', 'image', 'created']
    list_display_links = ['id', 'title', 'slug', 'image']
    list_filter = ['created']

    def get_preview_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=60>")
        return None

    get_preview_photo.short_description = 'Превью фото'
    