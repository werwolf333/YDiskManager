from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
    part_path = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    mime_type = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_key = models.CharField(max_length=255)

    class Meta:
        unique_together = ('name', 'part_path', 'api_key')

    def __str__(self):
        return f"{self.part_path}/{self.name}"
