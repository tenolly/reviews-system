from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
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
        queryset = Teacher.objects.all().prefetch_related("contacts", "review_tags__tag")

        search = self.request.query_params.get("q", "").strip()
        if search:
            try:
                isu_value = int(search)
            except ValueError:
                isu_value = None
            name_filter = Q(name__icontains=search)
            if isu_value is not None:
                queryset = queryset.filter(name_filter | Q(isu=isu_value))
            else:
                queryset = queryset.filter(name_filter)

        raw_tags = self.request.query_params.getlist("tags") or []
        if not raw_tags:
            raw_tags_param = self.request.query_params.get("tags")
            if raw_tags_param:
                raw_tags = [item for item in raw_tags_param.split(",") if item]

        tag_ids = []
        for raw in raw_tags:
            try:
                tag_ids.append(int(raw))
            except (TypeError, ValueError):
                continue

        if tag_ids:
            queryset = queryset.annotate(
                matched_tags=Count(
                    "review_tags__tag",
                    filter=Q(review_tags__tag__id__in=tag_ids),
                    distinct=True,
                )
            ).filter(matched_tags=len(tag_ids))

        queryset = queryset.annotate(
            review_count=Count("review", distinct=True),
            overall_avg=Coalesce(Avg("review__overall"), 0.0),
            difficulty_avg=Coalesce(Avg("review__difficulty"), 0.0),
            interesting_avg=Coalesce(Avg("review__interesting"), 0.0),
            responsibility_avg=Coalesce(Avg("review__responsibility"), 0.0),
            fairness_avg=Coalesce(Avg("review__fairness"), 0.0),
        )

        queryset = queryset.annotate(
            rating=ExpressionWrapper(
                (
                    F("overall_avg")
                    + F("difficulty_avg")
                    + F("interesting_avg")
                    + F("responsibility_avg")
                    + F("fairness_avg")
                )
                / 5.0,
                output_field=FloatField(),
            )
        )

        ordering_param = (self.request.query_params.get("ordering") or "").strip()
        allowed = {
            "rating": "rating",
            "overall": "overall_avg",
            "difficulty": "difficulty_avg",
            "interesting": "interesting_avg",
            "responsibility": "responsibility_avg",
            "fairness": "fairness_avg",
            "review_count": "review_count",
        }

        if ordering_param:
            direction = "-" if ordering_param.startswith("-") else ""
            key = ordering_param.lstrip("-")
            if key in allowed:
                queryset = queryset.order_by(f"{direction}{allowed[key]}")
        else:
            queryset = queryset.order_by("-rating", "name")

        return queryset


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

        if user.is_superuser and not record.exists():
            return Response({"detail": "Нельзя банить суперпользователя."}, status=status.HTTP_403_FORBIDDEN)

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
