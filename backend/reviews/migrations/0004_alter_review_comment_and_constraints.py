from django.db import migrations, models
from django.db.models import Count


def dedupe_reviews(apps, schema_editor):
    Review = apps.get_model("reviews", "Review")
    duplicates = (
        Review.objects.values("teacher_id", "owner_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )

    for entry in duplicates:
        teacher_id = entry["teacher_id"]
        owner_id = entry["owner_id"]
        qs = Review.objects.filter(teacher_id=teacher_id, owner_id=owner_id).order_by("-id")
        keep = qs.first()
        to_delete = qs.exclude(pk=keep.pk)
        to_delete.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("reviews", "0003_remove_review_reviews_user_id_79db63_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="comment",
            field=models.TextField(blank=True),
        ),
        migrations.RemoveConstraint(
            model_name="review",
            name="uniq_review",
        ),
        migrations.RunPython(dedupe_reviews, migrations.RunPython.noop),
        migrations.RunSQL("SET CONSTRAINTS ALL IMMEDIATE;"),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(
                fields=["teacher", "owner"], name="uniq_review_per_teacher_owner"
            ),
        ),
    ]