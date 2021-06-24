from django.urls import path

from . import views

urlpatterns = [
    path('all/', views.kube_all_resources_api),
    path('name/', views.get_name_of_namespace_api),
    path('resource/', views.get_resource_of_namespace_api),
]
