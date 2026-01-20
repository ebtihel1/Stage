from django.urls import path
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserProfileView
)

urlpatterns = [
   
    path('auth/register/', RegisterView.as_view(), name='register'),
    
   
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
  
    path('auth/me/', UserProfileView.as_view(), name='user_profile'),
]