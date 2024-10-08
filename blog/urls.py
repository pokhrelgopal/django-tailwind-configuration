from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),

    path("blog/add/", views.add_blog, name="add_blog"),
    path("blog/<int:id>/", views.delete_blog, name="delete_blog"),
    path("profile", views.profile, name="profile"),
]
