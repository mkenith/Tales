#from django.contrib import admin

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
   #path('admin/', admin.site.urls),
    #path('shosho/',include('shosho.urls'),namespace='shosho'),
    path('',tales,name="tales_view"),
    path('upload/',upload, name='upload_view'),
    #path('tales/', tales, name='tales'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)