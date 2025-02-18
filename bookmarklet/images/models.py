from django.db import models
from django.conf import settings

from unidecode import unidecode


class Image(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, 
                             related_name='images_created',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    users_like = models.ManyToManyField(to=settings.AUTH_USER_MODEL,
                                        related_name='images_liked',
                                        blank=True)


    def __str__(self):
        return self.title
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.title)
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = unidecode(self.title.lower().replace(' ', '_'))
        super(Image, self).save(*args, **kwargs)

 
    class Meta:
        indexes = [models.Index(fields=['-created']),]
        ordering = ['-created']