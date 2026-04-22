# # """
# # URL configuration for elderycare project.

# # The `urlpatterns` list routes URLs to views. For more information please see:
# #     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# # Examples:
# # Function views
# #     1. Add an import:  from my_app import views
# #     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# # Class-based views
# #     1. Add an import:  from other_app.views import Home
# #     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# # Including another URLconf
# #     1. Import the include() function: from django.urls import include, path
# #     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# # """
# # # from django.contrib import admin
# # # from django.urls import path, include
# # from myapp.views import home   # 👈 import home

# # # urlpatterns = [
# # #     path('admin/', admin.site.urls),
# # #     path('', home),                 # 👈 THIS FIXES "/"
# # #     path('api/', include('myapp.urls')),
# # # ]


# # # from django.contrib import admin
# # # from django.urls import path,include
# # # from myapp import views

# # # urlpatterns = [
# # #     path('admin/', admin.site.urls),

# # #     path('', views.home, name="home"),
# # #     path('medicine/', views.medicine, name="medicine"),
# # #     path('emergency/', views.emergency, name="emergency"),
# # #     path('exercise/', views.exercise, name="exercise"),

# # #     path('api/chat/', views.ChatView.as_view(), name="chat"),
# # # ]


# # # urlpatterns = [
# # #     path('admin/', admin.site.urls),
# # #     path('', include('myapp.urls')),
# # # ]


# # from django.contrib import admin
# # from django.urls import path, include
# # from myapp import views   # ✅ import views

# # urlpatterns = [
# #     path('admin/', admin.site.urls),

# #     # main app routes
# #     path('', include('myapp.urls')),

# #     # chatbot API
# #     path('api/chat/', views.ChatView.as_view(), name="chat"),
# # ]


# """ElderCare AI — URL Configuration"""

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.generic import TemplateView

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', TemplateView.as_view(template_name='home.html'), name='home'),
#     path('chatbot/', include('apps.chatbot.urls')),
#     path('medicine/', include('apps.medicine.urls')),
#     path('exercise/', include('apps.exercise.urls')),
#     path('signlanguage/', include('apps.signlanguage.urls')),
#     path('carecentre/', include('apps.carecentre.urls')),
#     path('emergency/', include('apps.emergency.urls')),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



"""ElderCare AI — URL Configuration (FIXED)"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('chatbot/', include('myapp.chatbot.urls')),
    path('medicine/', include('myapp.medicine.urls')),
    path('exercise/', include('myapp.exercise.urls')),
    path('signlanguage/', include('myapp.signlanguage.urls')),
    path('carecentre/', include('myapp.carecentre.urls')),
    path('emergency/', include('myapp.emergency.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
