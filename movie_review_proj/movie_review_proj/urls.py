from django.contrib import admin
from django.urls import path, include 

# these imports are used for the profile pictures
from django.conf.urls.static import static 
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movie_review_app.urls'))
]


# if we are in DEBUG add the below pattern to urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)