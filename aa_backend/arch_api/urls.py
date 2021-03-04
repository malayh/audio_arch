from django.urls import path
from .views import *

urlpatterns = [
    path('<str:audio_type>/',AudioList.as_view()),
    path('<str:audio_type>/<int:id>/',AudioDetail.as_view()),
]