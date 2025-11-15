# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Teacher(models.Model):
    isu = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    photo_url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    url = models.URLField(null=True)  # isu.ifmo
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teachers"

    def __str__(self):
        return f"{self.name}"


class Contact(models.Model):
    contact_type = models.CharField(max_length=64, null=True, blank=True)
    teacher = models.ForeignKey(
        Teacher, related_name="contacts", on_delete=models.CASCADE)
    url = models.URLField(null=True)

    class Meta:
        db_table = "contacts"

    def __str__(self):
        return f"{self.contact_type}: {self.url}"


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "subjects"

    def __str__(self):
        return self.name


class Tag(models.Model):
    count = models.IntegerField(default=0)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name


class Faculty(models.Model):
    code = models.CharField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "faculties"

    def __str__(self):
        return self.name


# TODO: just use a simple models.ManyToMany?
class TeacherFaculty(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.RESTRICT)

    class Meta:
        db_table = "teacher_faculties"

    def __str__(self):
        return f"{self.teacher} — {self.faculty}"


class Review(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    study_year = models.IntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(2050)])
    comment = models.TextField(null=False)

    overall = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    difficulty = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    interesting = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    responsibility = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    fairness = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject", "comment"], name="uniq_review"),
            models.CheckConstraint(check=models.Q(study_year__gte=2000) & models.Q(study_year__lte=2100),
                                   name="reviews_study_year_2000_2100"),
            models.CheckConstraint(check=models.Q(overall__gte=1) & models.Q(overall__lte=5),
                                   name="reviews_overall_1_5"),
            models.CheckConstraint(check=models.Q(difficulty__gte=1) & models.Q(difficulty__lte=5),
                                   name="reviews_difficulty_1_5"),
            models.CheckConstraint(check=models.Q(interesting__gte=1) & models.Q(interesting__lte=5),
                                   name="reviews_interesting_1_5"),
            models.CheckConstraint(check=models.Q(responsibility__gte=1) & models.Q(responsibility__lte=5),
                                   name="reviews_responsibility_1_5"),
            models.CheckConstraint(check=models.Q(fairness__gte=1) & models.Q(fairness__lte=5),
                                   name="reviews_fairness_1_5"),
        ]
        indexes = [
            models.Index(fields=["teacher"]),
            models.Index(fields=["subject"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Review #{self.id} by {self.user} for {self.teacher}"


class ReviewTag(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="review_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name="review_tags")
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="review_tags")

    class Meta:
        db_table = "review_tags"
        constraints = [
            models.UniqueConstraint(
                fields=["review", "tag", "teacher"], name="uniq_review_tag_teacher")
        ]
        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["tag"]),
            models.Index(fields=["teacher"]),
        ]

    def __str__(self):
        return f"{self.review_id}-{self.tag_id}-{self.teacher_id}"


class BlackList(models.Model):
    reason = models.TextField(null=True, blank=True)
    blacklist_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blacklists_as_user")
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blacklists_as_admin")

    class Meta:
        db_table = "black_list"

    def __str__(self):
        return f"BlackList #{self.id} for {self.user}"


class ModerationAction(models.Model):
    ACTION_DELETE = "delete"
    ACTION_BAN = "ban"
    ACTION_CHOICES = (
        (ACTION_DELETE, "delete"),
        (ACTION_BAN, "ban"),
    )

    target_id = models.BigIntegerField()  # GenericForeignKey?
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name="moderation_actions")
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "moderation_actions"

    def __str__(self):
        return f"{self.action} by {self.moderator_id} -> {self.target_id}"
