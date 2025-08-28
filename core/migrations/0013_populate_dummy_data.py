# core/migrations/0014_populate_dummy_data_safe.py
from django.db import migrations
from django.utils import timezone
import random

def populate_dummy_data(apps, schema_editor):
    Member = apps.get_model('core', 'Member')
    Moderator = apps.get_model('core', 'Moderator')
    ActivityDepartment = apps.get_model('core', 'ActivityDepartment')
    Achievement = apps.get_model('core', 'Achievement')
    Post = apps.get_model('core', 'Post')

    dummy_image_url = "members/dummy/dummy.jpg"
    dummy_post_image = "posts/dummy_post.jpg"
    dummy_ach_image = "achievements/dummy_ach.jpg"

    # --- Activity Departments ---
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
    for title, heading in default_activities:
        ActivityDepartment.objects.filter(dep_title=title).delete()
        ActivityDepartment.objects.create(dep_title=title, dep_heading=heading)

    activities = list(ActivityDepartment.objects.all())

    # --- Special Members ---
    special_members_data = [
        {
            "email": "h2so4.1191@gmail.com",
            "first_name": "محمد",
            "last_name": "الهادي",
            "third_name": "علي",
            "fourth_name": "صالح",
        },
        {
            "email": "tiktok.alert.info@gmail.com",
            "first_name": "سارة",
            "last_name": "يوسف",
            "third_name": "خالد",
            "fourth_name": "حسن",
        }
    ]
    for data in special_members_data:
        Member.objects.filter(email=data["email"]).delete()
        Member.objects.create(
            username=data["email"].split("@")[0],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            third_name=data["third_name"],
            fourth_name=data["fourth_name"],
            mother_full_name="أم مثال مثال مثال",
            date_of_birth="2000-01-01",
            phone_number="07712345678",
            address="بغداد - الكرادة - المنطقة 1",
            gender="M",
            academic_achievement="S",
            marital_status="V",
            studying_department="C",
            stage="1",
            studying_shift="A",
            id_card_front=dummy_image_url,
            id_card_back=dummy_image_url,
            residance_id_front=dummy_image_url,
            residance_id_back=dummy_image_url,
            personal_image=dummy_image_url,
        )

    members = list(Member.objects.exclude(email="").all())

    # --- Moderators ---
    if members:
        mod_member = Member.objects.filter(email="h2so4.1191@gmail.com").first()
        Moderator.objects.filter(member_ptr_id=mod_member.id).delete()
        mod_dept = random.choice(activities)
        Moderator.objects.create(
            member_ptr_id=mod_member.id,
            mod_level="P",
            activity_dep=mod_dept
        )

    # --- Other Members (fill up to 10) ---
    while Member.objects.count() < 10:
        idx = Member.objects.count() + 1
        Member.objects.create(
            username=f"user{idx}",
            email=f"user{idx}@example.com",
            first_name="محمد",
            last_name=f"ال{idx}",
            third_name="علي",
            fourth_name="صالح",
            mother_full_name="أم مثال مثال مثال",
            date_of_birth="2000-01-01",
            phone_number=f"077123456{idx:02d}",
            address="بغداد - الكرادة - المنطقة 1",
            gender="M",
            academic_achievement="S",
            marital_status="V",
            studying_department="C",
            stage="1",
            studying_shift="A",
            id_card_front=dummy_image_url,
            id_card_back=dummy_image_url,
            residance_id_front=dummy_image_url,
            residance_id_back=dummy_image_url,
            personal_image=dummy_image_url,
        )

    # --- Achievements ---
    for i in range(1, 11):
        Achievement.objects.filter(ach_title=f"Achievement {i}").delete()
        ach = Achievement.objects.create(
            ach_title=f"Achievement {i}",
            description=f"Description {i}",
            ach_image=dummy_ach_image,
            score=random.randint(5, 20)
        )
        ach.members.set(random.sample(members, min(5, len(members))))

    # --- Posts ---
    for i in range(1, 11):
        Post.objects.filter(heading=f"Post {i}").delete()
        Post.objects.create(
            heading=f"Post {i}",
            description=f"Description {i}",
            post_image=dummy_post_image,
            mod=Moderator.objects.first()
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_achievement_ach_image_alter_member_stage_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_dummy_data),
    ]
