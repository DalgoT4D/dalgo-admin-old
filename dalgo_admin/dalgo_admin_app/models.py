from django.db import models

# Create your models here.

class DataSource(models.Model):
    TYPE_CHOICES = [
        ('KoboToolbox', 'KoboToolbox'),
        ('MySQL', 'MySQL'),
        ('Salesforce', 'Salesforce')
    ]
    STATUS_CHOICES = [
        ('Success','Success'),
        ('Failed','Failed')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    number_of_streams = models.PositiveIntegerField()
    last_sync_date = models.DateTimeField()
    last_sync_status = models.CharField(max_length=10, choices = STATUS_CHOICES) #Success / failed 

class PipelineConfig(models.Model):
    ACTIVE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    SCHEDULE_CHOICES = [
        ('Manual', 'Manual'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    ]

    active = models.CharField(max_length=3, choices=ACTIVE_CHOICES, default='No')
    schedule = models.CharField(max_length=7, choices=SCHEDULE_CHOICES, default='Manual')
    time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Active: {self.active}, Schedule: {self.schedule}, Time: {self.time}"
    
class Client(models.Model):
    slug = models.SlugField(unique = True)
    full_name = models.CharField(max_length=255)
    warehouse_type = models.CharField(max_length=50)
    data_sources = models.ManyToManyField(DataSource)
    pipelines = models.ManyToManyField(PipelineConfig)
    github_repo_url = models.URLField(blank=True, null=True)
    

    def __str__(self):
        return self.full_name

    

