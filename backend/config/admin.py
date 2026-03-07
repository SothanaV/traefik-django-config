import os
from django.contrib import admin
from .models import Project, Service
# from django.template.loader import render_to_string
import yaml
# Register your models here.

dir_config = os.path.join('/', 'config-rules')

class ProjectAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Project._meta.fields]
    list_editable = ['is_use']
    actions = ['create_config', 'delete_config']
    search_fields = ['name']
    list_filter = ['is_use']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-is_use')
    
    @admin.action(description='create config')
    def create_config(self, request, queryset):
        for project in queryset.filter(is_use=True):
            config_path = os.path.join(dir_config, f"{project.name}.yaml")
            
            # Initialize as dictionaries, not lists
            data = {
                'http': {
                    'services': {}, 
                    'routers': {}
                }
            }
            
            for service in Service.objects.filter(project=project, is_use=True):
                service_id = f"{service.project.name}-{service.name}"
                service_back_id = f"{service_id}-backs"
                
                # Assign directly to the dictionary key
                data['http']['services'][service_back_id] = {
                    'loadBalancer': {
                        'servers': [
                            {'url': f'{service.url}'}
                        ]
                    }
                }
                
                # Assign directly to the dictionary key
                data['http']['routers'][service_id] = {
                    'rule': f'Host(`{service.domain}`)',
                    'service': service_back_id,
                    'entryPoints': ['web', 'websecure'],
                    'tls': {
                        'certResolver': 'myresolver'
                    }
                }
                
            with open(config_path, 'w') as f:
                # yaml.dump will now produce the correct key: value mapping
                f.write(yaml.dump(data=data, default_flow_style=False))
                
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