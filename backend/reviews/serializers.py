from django.shortcuts import get_object_or_404
from reviews.models import Contact, Faculty, Review, Subject, Tag, Teacher
from rest_framework import serializers


class ContactSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "teacher", "contact_type", "url"]


class TeacherReadSerializer(serializers.ModelSerializer):
    # contacts = ContactSerializer(many=True, read_only=True)
    contacts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Teacher
        fields = [
            "isu",
            "name",
            "photo_url",
            "phone",
            "url",
            "contacts",
        ]


class TeacherWriteSerializer(serializers.ModelSerializer):
    contacts = serializers.StringRelatedField(many=True)

    class Meta:
        model = Teacher
        fields = ["id", "isu", "name", "photo_url", "phone", "url", "contacts"]


class ReviewSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(
        slug_field="isu",
        queryset=Teacher.objects.all(),
    )

    class Meta:
        model = Review
        fields = [
            "teacher",
            "subject",
            "user",
            "study_year",
            "comment",
            "overall",
            "difficulty",
            "interesting",
            "responsibility",
            "fairness",
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class FacultiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["id", "code", "name"]
