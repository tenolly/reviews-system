from django.shortcuts import get_object_or_404
from django.db.models import Count, F
from reviews.models import Contact, Review, Subject, Tag, Teacher, ReviewTag
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    reviews = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Review.objects.all()
    )

    class Meta:
        model = User
        fields = ["id", "username", "reviews"]


class ContactSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "teacher", "contact_type", "url"]


class TeacherReadSerializer(serializers.ModelSerializer):
    contacts = serializers.StringRelatedField(many=True)
    tags = serializers.SerializerMethodField()
    rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "isu",
            "name",
            "photo_url",
            "phone",
            "url",
            "contacts",
            "tags",
            "rating",
            "review_count",
            "metrics",
        ]

    def get_tags(self, obj):
        popular = (
            ReviewTag.objects.filter(teacher=obj)
            .values("tag__id", "tag__name")
            .annotate(count=Count("id"))
            .order_by("-count", "tag__name")
        )
        return [
            {
                "id": item["tag__id"],
                "name": item["tag__name"],
                "count": item["count"],
            }
            for item in popular
        ]

    def get_metrics(self, obj):
        return {
            "overall": getattr(obj, "overall_avg", 0),
            "difficulty": getattr(obj, "difficulty_avg", 0),
            "interesting": getattr(obj, "interesting_avg", 0),
            "responsibility": getattr(obj, "responsibility_avg", 0),
            "fairness": getattr(obj, "fairness_avg", 0),
        }


class TeacherWriteSerializer(serializers.ModelSerializer):
    contacts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Teacher
        fields = ["id", "isu", "name", "photo_url", "phone", "url", "contacts"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(
        slug_field="isu",
        queryset=Teacher.objects.all(),
    )
    subject = serializers.CharField()
    comment = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(allow_blank=False), required=False, allow_empty=True
    )
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Review
        fields = [
            "id",
            "teacher",
            "subject",
            "owner",
            "study_year",
            "comment",
            "overall",
            "difficulty",
            "interesting",
            "responsibility",
            "fairness",
            "created_at",
            "updated_at",
            "is_edited",
            "tags",
        ]

    def _normalize_tags(self, raw_tags):
        normalized = []
        for raw in raw_tags or []:
            text = str(raw).strip()
            if text:
                normalized.append(text)
        return normalized

    def validate_subject(self, value):
        text = str(value).strip()
        if not text:
            raise serializers.ValidationError("Subject is required")

        subject_obj = None
        try:
            subject_obj = Subject.objects.filter(pk=int(text)).first()
        except (ValueError, TypeError):
            subject_obj = None

        if subject_obj is None:
            subject_obj, _ = Subject.objects.get_or_create(name=text)

        return subject_obj

    def validate(self, attrs):
        request = self.context.get("request")
        owner = getattr(request, "user", None)
        if owner is None or not owner.is_authenticated:
            raise serializers.ValidationError("Требуется авторизация для сохранения отзыва.")

        teacher = attrs.get("teacher") or (self.instance.teacher if self.instance else None)
        if teacher:
            existing_qs = Review.objects.filter(owner=owner, teacher=teacher)
            if self.instance:
                existing_qs = existing_qs.exclude(pk=self.instance.pk)
            if existing_qs.exists():
                raise serializers.ValidationError("Вы уже оставили отзыв для этого преподавателя.")

        return attrs

    def create(self, validated_data):
        tags = self._normalize_tags(validated_data.pop("tags", []))
        review = super().create(validated_data)

        for name in tags:
            tag_obj, _ = Tag.objects.get_or_create(name=name)
            link, created = ReviewTag.objects.get_or_create(
                review=review, teacher=review.teacher, tag=tag_obj
            )
            if created:
                Tag.objects.filter(pk=tag_obj.pk).update(count=F("count") + 1)

        return review

    def update(self, instance, validated_data):
        tags = self._normalize_tags(validated_data.pop("tags", []))
        review = super().update(instance, validated_data)

        current_tags = set(review.review_tags.values_list("tag__name", flat=True))
        new_tags = set(tags)

        to_add = new_tags - current_tags
        to_remove = current_tags - new_tags

        for name in to_add:
            tag_obj, _ = Tag.objects.get_or_create(name=name)
            link, created = ReviewTag.objects.get_or_create(
                review=review, teacher=review.teacher, tag=tag_obj
            )
            if created:
                Tag.objects.filter(pk=tag_obj.pk).update(count=F("count") + 1)

        if to_remove:
            tags_to_remove = Tag.objects.filter(name__in=to_remove)
            ReviewTag.objects.filter(review=review, tag__in=tags_to_remove).delete()
            for tag_obj in tags_to_remove:
                Tag.objects.filter(pk=tag_obj.pk).update(count=F("count") - 1)

        review.is_edited = True
        review.save(update_fields=["is_edited"])

        return review

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["subject"] = instance.subject_id
        data["subject_name"] = getattr(instance.subject, "name", None)
        data["teacher_name"] = getattr(instance.teacher, "name", None)
        data["created_at"] = instance.created_at
        data["updated_at"] = instance.updated_at
        data["tags"] = list(
            instance.review_tags.values_list("tag__name", flat=True)
        )
        return data
