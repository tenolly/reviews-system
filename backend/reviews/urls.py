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
     path("admin/reviews/", views.AdminReviewListView.as_view()),
     path("admin/reviews/<int:pk>/", views.AdminReviewDestroyView.as_view()),
    path("subjects/", views.SubjectsListView.as_view()),
    path("tags/", views.TagsListView.as_view()),
     path("profile/", views.ProfileView.as_view()),
     path("register/", views.RegisterView.as_view()),
     path("users/", views.UserList.as_view()),
     path("users/<int:pk>/", views.UserDetail.as_view()),
     path("admin/users/", views.AdminUserListView.as_view()),
     path("admin/users/<int:pk>/ban-toggle/", views.AdminUserBanToggleView.as_view()),
]
