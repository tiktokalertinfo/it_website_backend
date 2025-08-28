from django.urls import path
from .views import SignupView, LoginView, OTPView, ProfileView, AdminView, PostView, FeedView, NotificationView, SettingsView, SearchView, AchievementView, HistoryView, PendingView, AcceptPendingView, DeclinePendingView, AssignModView, DeclinePendingView, DeletePendingView, K1NG0FTHEH1LL
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/', OTPView.as_view(), name='otp'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
    path('admin/<int:id>/', AdminView.as_view(), name='admin'),
    path('post/', PostView.as_view(), name='post'),
    path('feed/', FeedView.as_view(), name='feed'),
    path('notification/', NotificationView.as_view(), name='notification'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('search/', SearchView.as_view(), name='search'),
    path('achievement/', AchievementView.as_view(), name='achievement'),
    path('history/<int:id>/', HistoryView.as_view(), name='history'),
    path('pending/', PendingView.as_view(), name='pending'),
    path('acceptpending/', AcceptPendingView.as_view(), name='acceptpending'),
    path('declinepending/', DeclinePendingView.as_view(), name='declinepending'),
    path('assignmod/', AssignModView.as_view(), name='assignmod'),
    path('cleanup/b64553161e16890e748cecaf973cc78367faa3fe0bbea6b87216950ef1c14297/', DeletePendingView.as_view(), name='deletepending'),
    path('K1NG0FTHEH1LL/', K1NG0FTHEH1LL.as_view(), name='K1NG0FTHEH1LL'),
]