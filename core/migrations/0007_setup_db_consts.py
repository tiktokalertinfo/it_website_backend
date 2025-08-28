from django.db import migrations, connection

def create_default_activities(apps, schema_editor):
    ActivityDepartment = apps.get_model('core', 'ActivityDepartment')
    default_activities = [
        ("software", "القسم البرمجي"),
        ("translations", "قسم الترجمة"),
        ("media", "قسم الإعلام"),
        ("hr", "قسم الموارد البشرية"),
        ("scouts", "قسم الكشافة"),
        ("sports", "القسم الرياضي"),
        ("services", "قسم الخدمات العامة"),
        ("culture", "القسم الثقافي"),
        ("religion", "القسم الديني"),
        ("arts", "قسم الفنون"),
    ]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
              pg_get_serial_sequence('"core_activitydepartment"', 'id'),
              COALESCE((SELECT MAX(id) FROM "core_activitydepartment"), 1)
            )
        """)
    for title, heading in default_activities:
        ActivityDepartment.objects.update_or_create(
            dep_title=title,
            dep_heading = heading,
            defaults={}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_activitydepartment_dep_heading'),
    ]

    operations = [
        migrations.RunPython(create_default_activities),
    ]
