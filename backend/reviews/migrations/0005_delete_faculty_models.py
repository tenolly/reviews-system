from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0004_alter_review_comment_and_constraints"),
    ]

    operations = [
        migrations.DeleteModel(name="TeacherFaculty"),
        migrations.DeleteModel(name="Faculty"),
    ]
