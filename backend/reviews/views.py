from django.shortcuts import get_object_or_404
from rest_framework import generics
from reviews.permissions import IsOwnerOrReadOnly
from reviews.serializers import *
from reviews.models import *
from rest_framework import permissions
from django.contrib.auth.models import User


class UserList(generics.ListAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = Teacher.objects.all()
    serializer_class = TeacherReadSerializer

    def get_queryset(self):
        return Teacher.objects.all().prefetch_related("contacts")


class TeacherListDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = Teacher.objects.all()
    serializer_class = TeacherWriteSerializer

    def get_queryset(self):
        return Teacher.objects.all().prefetch_related("contacts")


class ContactListCreateView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    serializer_class = ContactSerializer

    def get_queryset(self):
        teacher_id = self.kwargs["teacher_id"]
        return Contact.objects.filter(teacher_id=teacher_id)

    def perform_create(self, serializer):
        teacher = get_object_or_404(Teacher, pk=self.kwargs["teacher_id"])
        serializer.save(teacher=teacher)


class ContactListDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    lookup_url_kwarg = "contact_id"
    serializer_class = ContactSerializer

    def get_queryset(self):
        teacher_id = self.kwargs["teacher_id"]
        return Contact.objects.filter(teacher_id=teacher_id)


class ReviewListCreateView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly]  # the user can see all reviews
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        ti = self.request.query_params.get("teacher_isu")
        if ti is not None:
            queryset = queryset.filter(teacher__isu=ti)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class SubjectsListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class TagsListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class FacultiesListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAdminUser
    ]
    queryset = Faculty.objects.all()
    serializer_class = TagsSerializer
