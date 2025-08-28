from rest_framework import serializers
from core.models import Member, ActivityDepartment, Post, Achievement
from django.utils import timezone
from datetime import timedelta

class SignupSerializer(serializers.ModelSerializer):
    activity_department = serializers.PrimaryKeyRelatedField(
        queryset=ActivityDepartment.objects.all(), many=True, required=False
    )
    id_card_front = serializers.ImageField(required=True)
    id_card_back = serializers.ImageField(required=True)
    residance_id_front = serializers.ImageField(required=True)
    residance_id_back = serializers.ImageField(required=True)
    personal_image = serializers.ImageField(required=True)

    class Meta:
        model = Member
        fields = [
            'first_name','last_name','third_name','fourth_name',
            'mother_full_name','phone_number','email','address','gender',
            'academic_achievement','marital_status','activity_department',
            'skills_and_exp','studying_department','stage','studying_shift',
            'id_card_front','id_card_back','residance_id_front','residance_id_back',
            'personal_image'
        ]

    def create(self, validated_data):
        activity_departments = validated_data.pop('activity_department', [])
        member = Member(**validated_data)
        member.set_unusable_password()
        member.save()
        if activity_departments:
            member.activity_department.set(activity_departments)
        return member

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            member = Member.objects.get(email__iexact=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("هذا البريد غير مسجّل.")
        if member.last_login is None:
            raise serializers.ValidationError("لم يقُم أحد المدراء بالموافقة بالموافقة على انضمامك بعد , حاول مرة أخرى لاحقاً أو قُم بالتواصل مع أحدهم شخصياً")
        return value


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    def validate(self, data):
        try:
            member = Member.objects.get(email__iexact=data['email'])
        except Member.DoesNotExist:
            raise serializers.ValidationError({"email": "هذا البريد غير مسجل."})
        if member.last_login is None:
            raise serializers.ValidationError("لم يقُم أحد المدراء بالموافقة بالموافقة على انضمامك بعد , حاول مرة أخرى لاحقاً أو قُم بالتواصل مع أحدهم شخصياً")
        if member.otp_code != data['otp_code'].strip():
            raise serializers.ValidationError({"otp_code": "رمز التحقق غير صحيح."})
        if not member.otp_generated_at or timezone.now() - member.otp_generated_at > timedelta(minutes=5):
            raise serializers.ValidationError({"otp_code": "انتهت صلاحية رمز التحقق."})
        data['member'] = member
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_of_birth',
            'skills_and_exp',
            'academic_achievement',
            'studying_department',
            'stage',
            'studying_shift',
            'personal_image',
            'score',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        settings = instance.settings or {}
        for field in data.keys():
            if settings.get(f"show_{field}", True) is False:
                data[field] = False
        mod_entry = instance.core_moderator_set.first()
        if mod_entry:
            data['is_mod'] = mod_entry.mod_level
            data['is_mod_of'] = mod_entry.activity_department.title
        else:
            data['is_mod'] = False
            data['is_mod_of'] = None
        return data

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'id',
            'first_name',
            'last_name',
            'third_name',
            'fourth_name',
            'mother_full_name',
            'date_of_birth',
            'phone_number',
            'email',
            'address',
            'gender',
            'academic_achievement',
            'marital_status',
            'skills_and_exp',
            'studying_department',
            'stage',
            'id_card_front',
            'id_card_back',
            'residance_id_front',
            'residance_id_back',
            'personal_image',
            'score',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        mod_entry = instance.core_moderator_set.first()
        if mod_entry:
            data['is_mod'] = mod_entry.mod_level
            data['is_mod_of'] = mod_entry.activity_department.title
        else:
            data['is_mod'] = False
            data['is_mod_of'] = None
        return data

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'heading', 'description', 'post_image', 'mod', 'posted_at']
        read_only_fields = ['id', 'mod', 'posted_at']

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'heading', 'description', 'post_image', 'posted_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['heading', 'post_image']

class SettingsSerializer(serializers.Serializer):
    show_date_of_birth = serializers.BooleanField()
    show_personal_image = serializers.BooleanField()
    show_dark_mode = serializers.BooleanField()

class SearchSerializer(serializers.ModelSerializer):
    personal_image = serializers.SerializerMethodField()
    class Meta:
        model = Member
        fields = ['id', 'first_name', 'last_name', 'third_name', 'fourth_name', 'personal_image']
    def get_personal_image(self, obj):
        request_user = self.context.get('request').user
        if request_user.is_staff:
            return obj.personal_image.url if obj.personal_image else None
        return obj.personal_image.url if obj.settings.get("show_personal_image", True) else None

class AchievementSerializer(serializers.Serializer):
    ach_title = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    ach_image = serializers.ImageField()
    score = serializers.IntegerField(min_value=0)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'ach_title', 'description', 'ach_image', 'created_at', 'score']

class PendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'first_name', 'last_name', 'third_name', 'fourth_name', 'email']

class PendingActionSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()

class AssignModSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    activity_department_id = serializers.IntegerField()
    mod_level = serializers.ChoiceField(choices=[('P', 'رئيس'), ('S', 'نائب')])


