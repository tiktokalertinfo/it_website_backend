from django.db import migrations, connection

def create_default_activities(apps, schema_editor):
    ActivityDepartment = apps.get_model('core', 'ActivityDepartment')
    default_activities = [
        "software",
        "translations",
        "media",
        "hr",
        "scouts",
        "sports",
        "services",
        "culture",
        "religion",
        "arts",
    ]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
              pg_get_serial_sequence('"core_activitydepartment"', 'id'),
              COALESCE((SELECT MAX(id) FROM "core_activitydepartment"), 1)
            )
        """)
    for title in default_activities:
        ActivityDepartment.objects.get_or_create(dep_title=title)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_activitydepartment_moderator_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_activities),
    ]
