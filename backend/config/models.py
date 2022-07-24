from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=300)
    is_use = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name

class Service(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=300, help_text="eg, xxx.data.storemesh.com")
    path_prefix = models.CharField(max_length=100, help_text="path prefix eg, /static',/media/ or / ", default="/")
    pass_host_header = models.BooleanField(default=True)
    url = models.URLField(help_text="url for route to, eg http://192.168.24.206:8000")
    is_use = models.BooleanField(default=True)