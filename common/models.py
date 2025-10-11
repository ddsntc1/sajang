from django.db import models
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError

class BusinessType(models.Model):
    name = models.CharField(_('업종명'), max_length=100, unique=True)
    description = models.TextField(_('설명'), blank=True)
    category = models.ForeignKey(
        'board.Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='business_types',
        verbose_name=_('관련 카테고리')
    )
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    is_active = models.BooleanField(_('활성화 여부'), default=True)

    class Meta:
        verbose_name = _('업종')
        verbose_name_plural = _('업종 목록')
        ordering = ['name']

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('닉네임'),
        max_length=150,
        unique = True,
        help_text=_('필수. 150자 이내로 입력해주세요.')
    )
    user_id = models.CharField(
        _('아이디'),
        max_length=30,
        unique=True,
        help_text=_('필수. 로그인에 사용될 아이디를 입력해주세요.')
    )
    email = models.EmailField(
        _('이메일'),
        unique=True,
        help_text=_('필수. 인증에 사용될 이메일을 입력해주세요.')
    )
    business_type = models.ForeignKey(
        BusinessType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('업종'),
        related_name='users'
    )
    business_name = models.CharField(
        _('사업장 이름'),
        max_length=100,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        _('활성화'),
        default=False,
        help_text=_('이메일 인증 후 활성화됩니다.')
    )
    
    is_staff = models.BooleanField(
        _('admin 접근 권한'),
        default=False
    )
    
    is_admin = models.BooleanField(
        _('일반 관리자 권한'),
        default=False
    )
    
    is_superuser = models.BooleanField(
        _('최고 관리자 권한'),
        default=False
    )
    
    is_advertise = models.BooleanField(
        _('광고주 권한'),
        default=False
    )
    
    is_restricted = models.BooleanField(default=False)  # 계정 정지 여부
    restrict_end_date = models.DateTimeField(null=True, blank=True)  # 정지 해제 예정일
    
    date_joined = models.DateTimeField(_('가입일'), default=timezone.now)
    email_verified = models.BooleanField(_('이메일 인증됨'), default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')

    def __str__(self):
        return self.user_id
    
    def is_currently_restricted(self):
        # """유저가 현재 정지 상태인지 확인하고 필요 시 자동 해제"""
        if self.is_restricted and self.restrict_end_date:
            if self.restrict_end_date <= timezone.now():
                # 정지 기간이 끝났으면 자동으로 정지 해제
                self.is_restricted = False
                self.restrict_end_date = None
                self.save(update_fields=['is_restricted', 'restrict_end_date'])
                return False
            return True
        return False
    
    def get_report_count(self, days=30):
        """최근 일정 기간 동안의 신고 횟수를 반환"""
        from_date = timezone.now() - timedelta(days=days)
        return Report.objects.filter(
            reported_user=self,
            created_at__gte=from_date
        ).count()

    def get_remaining_reports_until_restriction(self):
        """제재까지 남은 신고 횟수 반환"""
        current_reports = self.get_report_count()
        return max(30 - current_reports, 0) #여기수정-report기준

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    introduction = models.TextField(_('자기소개'), blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}의 프로필'

# 사용자 생성 시 프로필 자동 생성
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance) 
        
# 임시 사용자 가입상태
class PendingUserManager(models.Manager):
    def cleanup_old_pending_users(self):
        # 24시간 이상 된 미인증 사용자 삭제
        deadline = timezone.now() - timedelta(minutes=10) # 시간 deadline 설정
        self.filter(created_at__lt=deadline).delete()

class PendingUser(models.Model):
    username = models.CharField(max_length=150)
    user_id = models.CharField(max_length=30)
    objects = PendingUserManager()
    email = models.EmailField()
    password = models.CharField(max_length=128)  # 해시된 비밀번호 저장
    business_type = models.ForeignKey(
        BusinessType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    business_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activation_token = models.CharField(max_length=150)

    class Meta:
        verbose_name = _('대기 중인 사용자')
        verbose_name_plural = _('대기 중인 사용자들')


# 정지기능 및 광고 부여 기능
class UserRestrictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    restricted_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='restrictions_made')
    restricted_at = models.DateTimeField(auto_now_add=True)
    restriction_reason = models.TextField()
    restriction_period = models.IntegerField()
    unrestricted_at = models.DateTimeField(null=True,blank=True)
    unrestricted_reason = models.TextField(null=True,blank=True)
    
    class Meta:
        ordering = ['-restricted_at']
        

class AdvertiserHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='advertiser_changes_made')
    changed_at = models.DateTimeField(auto_now_add=True)
    is_advertiser = models.BooleanField()
    reason = models.TextField()
    
    class Meta:
        ordering = ['changed_at']
        
    

class Report(models.Model):
    REPORT_CATEGORIES = [
        ('HARASSMENT', '괴롭힘'),
        ('SPAM', '스팸'),
        ('INAPPROPRIATE', '부적절한 콘텐츠'),
        ('HATE_SPEECH', '혐오 발언'),
        ('OTHER', '기타'),
    ]
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='reports_created'
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_received'
    )
    category = models.CharField(max_length=20, choices=REPORT_CATEGORIES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # 새로운 신고인 경우
            # 오늘 동일 사용자에 대한 신고가 있는지 확인
            today = timezone.now().date()
            already_reported = Report.objects.filter(
                reporter=self.reporter,
                reported_user=self.reported_user,
                created_at__date=today
            ).exists()
            
            if already_reported:
                raise ValidationError('이미 오늘 이 사용자를 신고했습니다.')

        super().save(*args, **kwargs)
        self.check_report_threshold()
    
    def check_report_threshold(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        report_count = Report.objects.filter(
            reported_user=self.reported_user,
            created_at__gte=thirty_days_ago
        ).count()
        
        if report_count != 0 and report_count % 30 == 0 : #여기수정-report기준
            if not self.reported_user.is_restricted:
                UserRestrictionHistory.objects.create(
                    user=self.reported_user,
                    restricted_by=None,
                    restriction_reason=f"30일 이내 신고 {report_count}회 누적으로 인한 자동 제재",
                    restriction_period=7,
                    unrestricted_at=None
                )
                self.reported_user.is_restricted = True
                self.reported_user.restrict_end_date = timezone.now() + timedelta(days=7)
                self.reported_user.save() 

    class Meta:
        # unique_together 대신 save 메서드에서 검증
        indexes = [
            models.Index(fields=['reporter', 'reported_user', 'created_at'])
        ]