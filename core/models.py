from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

def validate_image_size(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("يجب أن يكون حجم الصورة بحدود 5 ميجابايت")
    
def member_upload_path(instance, filename):
    folder_name = f"{instance.first_name}_{instance.last_name}_{instance.third_name}_{instance.fourth_name}"
    return f"members/{folder_name}/{filename}"

arabic_name_validator = RegexValidator(
    regex=r'^[\u0600-\u06FF]+$',
    message="يرجى إدخال اسم عربي صحيح بدون مسافات."
)

arabic_four_name_validator = RegexValidator(
    regex=r'^[\u0600-\u06FF]+ [\u0600-\u06FF]+ [\u0600-\u06FF]+ [\u0600-\u06FF]+$',
    message="يرجى إدخال الاسم بالكامل (أربعة أسماء) مفصولة بمسافات."
)
iraqi_phone_validator = RegexValidator(
    regex=r'^07\d{9}$',
    message="رقم الهاتف يجب أن يبدأ بـ 07 ويتكون من 11 رقماً."
)
arabic_address_validator = RegexValidator(
    regex=r'^[\u0600-\u06FF\s]+ - [\u0600-\u06FF\s]+ - [\u0600-\u06FF\s]+$',
    message="يرجى إدخال العنوان بالشكل: المحافظة - المدينة أو الناحية - المنطقة"
)

GENDER_CHOICES = [('M', 'ذكر'), ('F', 'أنثى'),]
ACADEMIC_ACHIEVEMENT_CHOICES = [('S', 'طالب'), ('G', 'خريج'),]
MARITAL_STATUS_CHOICES = [('V', 'أعزب/عزباء'), ('M', 'متزوج/ة'), ('D', 'مطلّق/ة'), ('W', 'أرمل/ة'),]
STUDYING_DEPARTMENT_CHOICES = [('C', 'علوم الحاسوب'), ('I', 'نظم المعلومات'), ('S', 'الأمن السيبراني'), ('D', 'الأنظمة الطبية الذكية'),]
STAGE_CHOICES = [('1', 'الأولى'), ('2', 'الثانية'), ('3', 'الثالثة'), ('4', 'الرابعة'),]
STUDYING_SHIFT_CHOICES = [('A', 'صباحي'), ('P', 'مسائي')]
MOD_CHOICES = [('P', 'رئيس'), ('S', 'نائب'),]

class Member(AbstractUser):
    first_name = models.CharField(max_length=50, validators=[arabic_name_validator])
    last_name = models.CharField(max_length=50, validators=[arabic_name_validator])
    third_name = models.CharField(max_length=50, validators=[arabic_name_validator])
    fourth_name = models.CharField(max_length=50, validators=[arabic_name_validator])
    mother_full_name = models.CharField(max_length=200, validators=[arabic_four_name_validator])
    date_of_birth = models.DateField(default="2000-01-01")
    phone_number = models.CharField(max_length=12, validators=[iraqi_phone_validator])
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=200, validators=[arabic_address_validator])
    gender = models.CharField(max_length=1, choices= GENDER_CHOICES)
    academic_achievement = models.CharField(max_length=1, choices=ACADEMIC_ACHIEVEMENT_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)
    activity_department = models.ManyToManyField('ActivityDepartment', related_name="activity_departments")
    skills_and_exp = models.TextField(blank=True)
    studying_department = models.CharField(max_length=1, choices=STUDYING_DEPARTMENT_CHOICES, default='G')
    stage = models.CharField(max_length=1, choices=STAGE_CHOICES, default='G')
    studying_shift = models.CharField(max_length=1, choices=STUDYING_SHIFT_CHOICES, default='G')
    id_card_front = models.ImageField(upload_to=member_upload_path, validators=[validate_image_size])
    id_card_back = models.ImageField(upload_to=member_upload_path, validators=[validate_image_size])
    residance_id_front = models.ImageField(upload_to=member_upload_path, validators=[validate_image_size])
    residance_id_back = models.ImageField(upload_to=member_upload_path, validators=[validate_image_size])
    personal_image = models.ImageField(upload_to=member_upload_path, validators=[validate_image_size])
    username = models.CharField(max_length=150, unique=True, blank=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)
    settings = models.JSONField(default=dict)
    score = models.PositiveIntegerField(default=0)
    def save(self, *args, **kwargs):
        if self.email and not self.username:
            self.username = self.email.split("@")[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class ActivityDepartment(models.Model):
    dep_title = models.CharField(max_length=50)
    dep_heading = models.CharField(max_length=50, blank= True, null=True)
    moderator = models.ForeignKey('Moderator', on_delete=models.CASCADE, related_name='primary_head', blank=True, null=True)
    second_in_command = models.ForeignKey('Moderator', on_delete=models.CASCADE, related_name='secondary_head', blank=True, null=True)

    def __str__(self):
        return self.dep_title
    
class Moderator(Member):
    mod_level = models.CharField(max_length=1, choices=MOD_CHOICES)
    activity_dep = models.ForeignKey('ActivityDepartment', on_delete=models.CASCADE, related_name='moderators')

    def __str__(self):
        return self.email + ": " + str(self.activity_dep)
    
class Achievement(models.Model):
    ach_title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ach_image = models.ImageField(upload_to="achievements/", null=True, blank=True)
    members = models.ManyToManyField("Member", related_name="achievements")
    score = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.ach_title
    
class Post(models.Model):
    heading = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    post_image = models.ImageField(upload_to="posts/", null=True, blank=True)
    mod = models.ForeignKey('Moderator', on_delete=models.CASCADE)

