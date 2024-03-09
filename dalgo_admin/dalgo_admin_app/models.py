from django.db import models

# Create your models here.


class Client(models.Model):
    """a dalgo client"""

    slug = models.SlugField(unique=True)
    full_name = models.CharField(max_length=255)
    warehouse_type = models.CharField(max_length=50)
    github_repo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ("full_name",)


class Datasource(models.Model):
    """an airbyte connection"""

    type = models.TextField()
    number_of_streams = models.PositiveIntegerField()
    last_sync_date = models.DateTimeField(null=False)
    last_sync_status = models.TextField()
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="datasource"
    )


class Pipelineconfig(models.Model):
    """an orchestration pipeline"""

    SCHEDULE_CHOICES = [
        ("Manual", "Manual"),
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
    ]
    active = models.BooleanField(default=False)
    schedule = models.CharField(
        max_length=7, choices=SCHEDULE_CHOICES, default="Manual"
    )
    time = models.TimeField(null=True, blank=True)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="pipelineconfig"
    )

    def __str__(self):
        return f"Active: {self.active}, Schedule: {self.schedule}, Time: {self.time}"
