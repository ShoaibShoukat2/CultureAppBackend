from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('artist-profile/', ArtistProfileAPIView.as_view(), name='artist-profile'),
]






