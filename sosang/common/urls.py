from django.urls import path
from django.contrib.auth import views as av
from django.urls import reverse_lazy
from .views import base_views,find_views,profile_views,admin_views,auth_views,report_views

app_name = 'common'

urlpatterns = [
    # 로그인 & 아웃
    path('login/',auth_views.login_view,name='login'),
    path('logout/',auth_views.logout_view,name='logout'),

    
    path('delete-account/',auth_views.delete_account,name='delete_account'),
    
    # 회원가입 및 메일인증
    path('activate/<str:uidb64>/<str:token>/', base_views.activate, name='activate'),
    path('signup/', base_views.signup, name='signup'),
    path('get_business_types/<int:category_id>/', base_views.get_business_types, name='get_business_types'),
    
    # 프로필 수정
    path('profile/',profile_views.profile,name = 'profile'),
    path('profile/<str:username>/', profile_views.user_profile, name='user_profile'),
    path('password_change/', av.PasswordChangeView.as_view(
        template_name='common/password_change.html',
        success_url='/common/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', av.PasswordChangeDoneView.as_view(
        template_name='common/password_change_done.html'
    ), name='password_change_done'),
    
    path('my-posts/',profile_views.my_posts,name='my_posts'),
    
    # ID/PW 찾기
    path('find_id/', find_views.find_id, name='find_id'),
    path('reset_password/', find_views.reset_password, name='reset_password'),
    path('reset_password_confirm/<uidb64>/<token>/', 
        av.PasswordResetConfirmView.as_view(
            template_name='common/password_reset_confirm.html',
            success_url=reverse_lazy('common:login')
        ),
        name='password_reset_confirm'),
    
# common/urls.py
    path('admin/toggle-notice/<int:question_id>/', admin_views.toggle_notice, name='toggle_notice'),
    path('admin/delete-post/<int:question_id>/', admin_views.admin_delete, name='admin_delete'),
    path('admin/restrict_user/', admin_views.restrict_user, name='restrict_user'),
    path('admin/unrestrict/',admin_views.unrestrict_user,name='unrestrict_user'),
    path('admin/toggle-advertiser/',admin_views.toggle_advertise,name='toggle_advertise'),

    path('ajax/fetch-user-info/', admin_views.fetch_user_info, name='fetch_user_info'),


    path('report/user/<str:username>/', report_views.report_user, name='report_user'),
]