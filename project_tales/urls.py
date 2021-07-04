#from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   #path('admin/', admin.site.urls),
    #path('shosho/',include('shosho.urls'),namespace='shosho'),
     path('tales',views.TalesView.as_view(),name="tales_view"),
]  