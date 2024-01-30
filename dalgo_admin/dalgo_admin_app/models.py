from django.db import models

# Create your models here.

class DataSource(models.Model):
    type = models.TextField()
    number_of_streams = models.PositiveIntegerField()
    last_sync_date = models.DateTimeField(null=False)
    last_sync_status = models.TextField()
    

class PipelineConfig(models.Model):

    SCHEDULE_CHOICES = [
        ('Manual', 'Manual'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    ]

    active = models.BooleanField(default=False)
    schedule = models.CharField(max_length=7, choices=SCHEDULE_CHOICES, default='Manual')
    time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Active: {self.active}, Schedule: {self.schedule}, Time: {self.time}"
    
class Client(models.Model):
    slug = models.SlugField(unique = True)
    full_name = models.CharField(max_length=255)
    warehouse_type = models.CharField(max_length=50)
    data_sources = models.ForeignKey(DataSource,on_delete= models.CASCADE)
    pipelines = models.ForeignKey(PipelineConfig,on_delete= models.CASCADE)
    github_repo_url = models.URLField(blank=True, null=True)
    

    def __str__(self):
        return self.full_name

    

