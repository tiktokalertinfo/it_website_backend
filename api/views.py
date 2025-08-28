from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer, OTPSerializer, ProfileSerializer, AdminSerializer, PostSerializer, FeedSerializer, NotificationSerializer, SettingsSerializer, SearchSerializer, AchievementSerializer, HistorySerializer, PendingSerializer, PendingActionSerializer, AssignModSerializer
from core.models import Member, Post, Achievement, Moderator, ActivityDepartment
from django.core.mail import send_mail
from django.conf import settings
import random
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination
from datetime import timedelta
from django.db.models import Q
from django.db import models
from django.utils import timezone

class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            return Response({
                "success": True,
                "member_id": member.id,
                "message": "تم تسجيل العضو بنجاح"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            member = Member.objects.get(email__iexact=serializer.validated_data['email'])
            if member.otp_generated_at and timezone.now() - member.otp_generated_at < timedelta(minutes=3):
                remaining = 180 - (timezone.now() - member.otp_generated_at).seconds
                return Response({
                    "success": False,
                    "message": f"لقد تم إرسال رمز التحقق بالفعل. حاول مرة أخرى بعد {remaining} ثانية."
                }, status=status.HTTP_400_BAD_REQUEST)
            otp = f"{random.randint(100000, 999999)}"
            member.otp_code = otp
            member.otp_generated_at = timezone.now()
            member.save()
            send_mail(
                subject='رمز تسجيل الدخول',
                message=f'رمز تسجيل الدخول الخاص بك هو\n\n{otp}\n\nسوف تنتهي صلاحية الرمز بعد 5 دقائق.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[member.email],
            )
            return Response({"success": True, "message": "تم إرسال رمز التحقق إلى بريدك"})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class OTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.validated_data['member']
            member.otp_code = None
            member.otp_generated_at = None
            member.save()
            refresh = RefreshToken.for_user(member)
            is_mod = Moderator.objects.filter(member_ptr_id=member.id).exists()
            return Response({
                "success": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "member_id": member.id,
                "is_staff": member.is_staff,
                "is_mod": is_mod
            })
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, id):
        try:
            member = Member.objects.get(pk=id)
        except Member.DoesNotExist:
            return Response({"success": False, "error": "Member not found"}, status=404)
        if member.last_login is None:
            return Response({"success": False, "error": "Member not found"}, status=404)
        serializer = ProfileSerializer(member)
        return Response({"success": True, "data": serializer.data})

class AdminView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        if not request.user.is_staff:
            return Response({"success": False, "error": "Unauthorized"}, status=403)
        try:
            member = Member.objects.get(pk=id)
        except Member.DoesNotExist:
            return Response({"success": False, "error": "Member not found"}, status=404)
        if member.last_login is None:
            return Response({"success": False, "error": "Member not found"}, status=404)
        serializer = AdminSerializer(member)
        return Response({"success": True, "data": serializer.data})

class PostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not hasattr(request.user, 'moderator'):
            return Response({"success": False, "message": "غير مخوّل للنشر"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(mod=request.user.moderator)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PostPagination(CursorPagination):
    page_size = 10
    ordering = '-posted_at'
    cursor_query_param = 'cursor'

class FeedView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = FeedSerializer
    pagination_class = PostPagination
    permission_classes = [AllowAny]

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        member = request.user
        departments = member.activity_department.all()
        mods = []
        for dep in departments:
            if dep.moderator:
                mods.append(dep.moderator)
            if dep.second_in_command:
                mods.append(dep.second_in_command)
        two_days_ago = timezone.now() - timedelta(days=2)
        posts = Post.objects.filter(
            mod__in=mods,
            posted_at__gte=two_days_ago
        ).order_by('-posted_at')
        serializer = NotificationSerializer(posts, many=True)
        return Response({'success': True, 'notifications': serializer.data})

class SettingsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        member = request.user
        settings = member.settings
        default_settings = {
            "show_date_of_birth": True,
            "show_personal_image": True,
            "show_dark_mode": False
        }
        data = {**default_settings, **settings}
        return Response({"success": True, "settings": data})
    def post(self, request):
        serializer = SettingsSerializer(data=request.data)
        if serializer.is_valid():
            member = request.user
            member.settings.update(serializer.validated_data)
            member.save()
            return Response({"success": True, "settings": member.settings})
        return Response({"success": False, "errors": serializer.errors}, status=400)

class SearchView(ListAPIView):
    serializer_class = SearchSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Member.objects.none()
        return Member.objects.filter(
            (
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(third_name__icontains=query) |
                Q(fourth_name__icontains=query)
            ) & Q(last_login__isnull=False)
        )
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AchievementView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = AchievementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            achievement = Achievement.objects.create(
                ach_title=data['ach_title'],
                description=data.get('description', ''),
                ach_image=data['ach_image'],
                score=data['score']
            )
            members = Member.objects.filter(id__in=data['member_ids'])
            achievement.members.set(members)
            members.update(score=models.F('score') + data['score'])
            return Response({
                "success": True,
                "achievement_id": achievement.id,
                "member_ids": list(members.values_list('id', flat=True))
            })
        return Response({"success": False, "errors": serializer.errors}, status=400)

class HistoryPagination(CursorPagination):
    page_size = 10
    ordering = '-created_at'

class HistoryView(APIView):
    def get(self, request, id):
        try:
            member = Member.objects.get(id=id)
        except Member.DoesNotExist:
            return Response({"success": False, "message": "Member not found"}, status=404)
        achievements = member.achievements.all().order_by('-created_at')
        paginator = HistoryPagination()
        page = paginator.paginate_queryset(achievements, request)
        serializer = HistorySerializer(page, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data = {"success": True, "data": paginated_response.data}
        return paginated_response


class PendingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            mod = Moderator.objects.get(member_ptr_id=request.user.id)
        except Moderator.DoesNotExist:
            return Response({"success": False, "error": "You are not a moderator."}, status=403)

        mod_departments = mod.activitydepartment_set.all()
        pending_members = Member.objects.filter(
            last_login__isnull=True,
            activity_department__in=mod_departments
        ).distinct()
        serializer = PendingSerializer(pending_members, many=True)
        return Response({"success": True, "members": serializer.data})

class AcceptPendingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PendingActionSerializer(data=request.data)
        if serializer.is_valid():
            member_id = serializer.validated_data['member_id']
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                return Response({"success": False, "error": "Member does not exist"}, status=status.HTTP_404_NOT_FOUND)
            logged_member = request.user
            if not Moderator.objects.filter(member_ptr_id=logged_member.id,
                                            activitydepartment__in=member.activity_department.all()).exists():
                return Response({"success": False, "error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            member.last_login = timezone.now()
            member.save()
            send_mail(
                subject='تم قبول تسجيلك',
                message='لقد تمت الموافقة على على طلبك للإنضمام الى الفريق التطوعي من قبل أحد رؤساء الأقسام , توجّه إلى موقع الفريق و قُ بتسجيل الدخول.\n\n\nأهلا بك معنا!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[member.email],
            )
            return Response({"success": True, "message": "Member accepted"})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DeclinePendingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PendingActionSerializer(data=request.data)
        if serializer.is_valid():
            member_id = serializer.validated_data['member_id']
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                return Response({"success": False, "error": "Member does not exist"}, status=status.HTTP_404_NOT_FOUND)
            logged_member = request.user
            if not Moderator.objects.filter(member_ptr_id=logged_member.id,
                                            activitydepartment__in=member.activity_department.all()).exists():
                return Response({"success": False, "error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            member_email = member.email
            member.delete()
            send_mail(
                subject='تم رفض تسجيلك',
                message='نرجو المعذرة , قد تم رفض طلبك للإنضمام الر الفريق التطوعي من قبل أحد مدراء الأقسام , إن كنت تعتقد بوجود خطأ قُم بالتواصل مع أحدهم ثم قم يالتسجيل محدداً\n\n\nنتمنى لكم فرصة سعيدة',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[member_email],
            )
            return Response({"success": True, "message": "Member declined and deleted"})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AssignModView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = AssignModSerializer(data=request.data)
        if serializer.is_valid():
            member_id = serializer.validated_data['member_id']
            dept_id = serializer.validated_data['activity_department_id']
            mod_level = serializer.validated_data['mod_level']
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                return Response({"success": False, "error": "Member does not exist"}, status=status.HTTP_404_NOT_FOUND)
            try:
                dept = ActivityDepartment.objects.get(id=dept_id)
            except ActivityDepartment.DoesNotExist:
                return Response({"success": False, "error": "Activity Department does not exist"}, status=status.HTTP_404_NOT_FOUND)
            if dept not in member.activity_department.all():
                return Response({"success": False, "error": "Member is not in this activity department"}, status=status.HTTP_400_BAD_REQUEST)
            Moderator.objects.filter(activitydepartment=dept, mod_level=mod_level).delete()
            Moderator.objects.create(member_ptr_id=member.id, activitydepartment=dept, mod_level=mod_level)
            level_name = "رئيس" if mod_level == "P" else "نائب"
            return Response({"success": True, "message": f"Member assigned as {level_name} for the activity department"})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class DeletePendingView(APIView):
    def post(self, request):
        threshold = timezone.now() - timedelta(hours=48)
        members_to_delete = Member.objects.filter(last_login__isnull=True, date_joined__lte=threshold)
        count = members_to_delete.count()
        members_to_delete.delete()
        return Response({"success": True, "deleted_count": count})

class K1NG0FTHEH1LL(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        settings.SITE_LOCKED = True
        return Response({"success": True, "message": "1191"})
    def delete(self, request):
        settings.SITE_LOCKED = False
        return Response({"success": True, "message": "1911"})

