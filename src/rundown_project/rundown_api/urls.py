from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('login', views.LoginViewSet, basename='login')
router.register('register', views.RegisterViewSet, basename='register')
router.register('rundown', views.RundownViewSet, basename='rundown')
router.register('user', views.UserProfileViewSet, basename='user')
router.register('rundown_detail', views.RundownDetailViewSet, basename='rundown_detail')
router.register('friend', views.FriendViewSet, basename='friend')
router.register('reorder', views.ReoderRundownDetailViewSet, basename='reorder')
router.register('search', views.SearchViewSet, basename='search')
urlpatterns = [
    path('', include(router.urls))
]
