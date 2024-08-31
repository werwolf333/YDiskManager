from django.db import models


class Item(models.Model):
    path = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    part_path = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    mime_type = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
