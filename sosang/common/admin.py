# common/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _  # 이 줄을 추가
from .models import CustomUser, BusinessType,Report, UserRestrictionHistory
from django.utils.html import format_html


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'restrict_end_date', 'is_staff')
    list_filter = ('is_restricted', 'is_active', 'is_staff', 'business_type')
    # list_editable = []
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'email', 'password')}),
        ('사업자 정보', {'fields': ('business_type', 'business_name')}),
        ('계정 상태', {'fields': ('is_restricted', 'restrict_end_date')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_admin','is_superuser', 'email_verified','is_advertise')}),
    )

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reported_user','report_date', 'reporter', 'category', 'get_report_count']
    list_filter = ['category', 'created_at']
    search_fields = ['reported_user__username', 'reporter__username']
    ordering = ['-created_at']

    def report_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    report_date.short_description = '신고일시'

    def get_report_count(self, obj):
        count = Report.objects.filter(reported_user=obj.reported_user).count()
        return format_html(
            '<span style="color: {};">{} 회</span>',
            'red' if count >= 25 else 'black',
            count
        )
    get_report_count.short_description = '누적 신고수'

@admin.register(UserRestrictionHistory)
class UserRestrictionHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'restricted_user', 
        'restriction_status',
        'restricted_date', 
        'restriction_period',
        'unrestricted_date',
        'restricted_by'
    ]
    list_filter = ['restricted_at', 'unrestricted_at']
    search_fields = ['user__username', 'restricted_by__username']
    ordering = ['-restricted_at']

    def restricted_user(self, obj):
        return obj.user.username
    restricted_user.short_description = '제재 대상자'

    def restricted_date(self, obj):
        return obj.restricted_at.strftime("%Y-%m-%d %H:%M")
    restricted_date.short_description = '제재 일시'

    def unrestricted_date(self, obj):
        if obj.unrestricted_at:
            return obj.unrestricted_at.strftime("%Y-%m-%d %H:%M")
        return '-'
    unrestricted_date.short_description = '해제 일시'

    def restriction_status(self, obj):
        if not obj.unrestricted_at:
            return format_html('<span style="color: red;">진행중</span>')
        return format_html('<span style="color: green;">해제됨</span>')
    restriction_status.short_description = '상태'

    readonly_fields = ['restricted_at', 'unrestricted_at']

    # 상세 보기 페이지 필드 구성
    fieldsets = (
        ('제재 정보', {
            'fields': ('user', 'restricted_by', 'restriction_period', 'restriction_reason')
        }),
        ('제재 기간', {
            'fields': ('restricted_at', 'unrestricted_at')
        }),
        ('해제 정보', {
            'fields': ('unrestricted_reason',),
        }),
    )

    # 관리자 페이지에서 추가 액션 정의
    actions = ['release_restriction']

    def release_restriction(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(unrestricted_at__isnull=True).update(
            unrestricted_at=timezone.now(),
            unrestricted_reason='관리자에 의한 수동 해제'
        )
        self.message_user(request, f'{updated}개의 제재가 해제되었습니다.')
    release_restriction.short_description = '선택된 제재 해제하기'

