import os
from django.contrib import admin
from .models import Project, Service
from django.template.loader import render_to_string
# Register your models here.

dir_config = os.path.join('/', 'config-rules')

class ProjectAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Project._meta.fields]
    list_editable = ['is_use']
    actions = ['create_config', 'delete_config']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-is_use')
    
    @admin.action(description='create config')
    def create_config(self, request, queryset):
        for project in queryset.filter(is_use=True):
            config_path = os.path.join(dir_config, f"{project.name}.toml")
            config = ""
            for service in Service.objects.filter(project=project, is_use=True):
                context = {
                    'service_domain': service.domain,
                    'service_name': f"{service.project.name}-{service.name}",
                    'passhostheader': service.pass_host_header,
                    'service_url': service.url,
                    'path_prefix': service.path_prefix,
                    'domain': service.domain
                }
                config += render_to_string('config/template.toml', context=context)
            with open(config_path, 'w') as f:
                f.write(config)
                
    @admin.action(description='delete config')
    def delete_config(self, request, queryset):
        for project in queryset.filter(is_use=True):
            config_path = os.path.join(dir_config, f"{project.name}.toml")
            os.remove(config_path)
        queryset.update(is_use=False)
        
admin.site.register(Project, ProjectAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Service._meta.fields]
    list_filter = ['project__name']
    list_editable = ['is_use']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-is_use')
    
admin.site.register(Service, ServiceAdmin)