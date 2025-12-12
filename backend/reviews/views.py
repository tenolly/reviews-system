from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Count
from reviews.permissions import IsOwnerOrReadOnly
from reviews.serializers import *
from reviews.models import BlackList, Teacher, Contact, Review, Subject, Tag
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


class TeacherListCreateView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    queryset = Teacher.objects.all()
    serializer_class = TeacherReadSerializer

    def get_queryset(self):
        return Teacher.objects.all().prefetch_related("contacts", "review_tags__tag")


class TeacherListDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    queryset = Teacher.objects.all()
    serializer_class = TeacherReadSerializer

    def get_queryset(self):
        return Teacher.objects.all().prefetch_related("contacts", "review_tags__tag")


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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        ti = self.request.query_params.get("teacher_isu")
        if ti is not None:
            queryset = queryset.filter(teacher__isu=ti)

        return queryset.select_related("teacher", "subject", "owner").prefetch_related(
            "review_tags__tag"
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class AdminReviewListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.select_related("teacher", "subject", "owner").prefetch_related(
            "review_tags__tag"
        )


class AdminReviewDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class SubjectsListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class TagsListView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = request.data.get("password") or ""
        password_confirm = request.data.get("password_confirm") or request.data.get("password_confirmation")

        if not username or not password:
            return Response({"detail": "Укажите имя пользователя и пароль."}, status=status.HTTP_400_BAD_REQUEST)

        if password_confirm is not None and password != password_confirm:
            return Response({"detail": "Пароли не совпадают."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Пользователь с таким именем уже существует."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"id": user.id, "username": user.username, "token": token.key}, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        is_banned = BlackList.objects.filter(user=user).exists()
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_banned": is_banned,
        }
        return Response(data, status=status.HTTP_200_OK)


class AdminUserListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.order_by("-is_staff", "username")
        review_counts = {
            row["owner_id"]: row["total"]
            for row in Review.objects.values("owner_id").annotate(total=Count("id"))
        }
        banned_ids = set(BlackList.objects.values_list("user_id", flat=True))

        payload = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "reviews": review_counts.get(user.id, 0),
                "banned": user.id in banned_ids,
            }
            for user in users
        ]
        return Response(payload, status=status.HTTP_200_OK)


class AdminUserBanToggleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        record = BlackList.objects.filter(user=user)
        if record.exists():
            record.delete()
            banned = False
        else:
            BlackList.objects.create(user=user, admin=request.user, reason="Забанен администратором")
            banned = True

        data = {
            "id": user.id,
            "username": user.username,
            "banned": banned,
        }
        return Response(data, status=status.HTTP_200_OK)
