from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("teachers/", views.TeacherListCreateView.as_view()),
    path("teachers/<int:pk>/", views.TeacherListDetailView.as_view()),
    path("teachers/<int:teacher_id>/contacts/",
         views.ContactListCreateView.as_view()),
    path("teachers/<int:teacher_id>/contacts/<int:contact_id>/",
         views.ContactListDetailView.as_view()),
    path("reviews/", views.ReviewListCreateView.as_view()),
    path("reviews/<int:pk>/", views.ReviewDetailView.as_view()),
    path("subjects/", views.SubjectsListView.as_view()),
    path("tags/", views.TagsListView.as_view()),
    path("faculties/", views.FacultiesListView.as_view()),
    path("users/", views.UserList.as_view()),
    path("users/<int:pk>/", views.UserDetail.as_view()),
]
