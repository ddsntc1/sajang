from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Category(models.Model):
    TYPE_CHOICES = (
        ('board', '글게시판'),
        ('story', '이야기게시판'),
        ('advertise','광고게시판'),
        ('info','정보게시판')
    )
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_business = models.BooleanField(default=False)  # 사업 분야 대분류에 해당. profile, 회원가입에 사용됨.
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='board')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # models.py의 Category 클래스에 추가
    def __str__(self):
        return self.name



class Question(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions'
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    modify_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField()
    up_voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_up_voter',blank=True)
    down_voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_down_voter',blank=True)
    is_notice = models.BooleanField(default=False)
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_questions', blank=True)
    view_count = models.PositiveIntegerField(default=0) 
    
    @property
    def vote_count(self):
        return self.up_voter.count() - self.down_voter.count()
    


class Answer(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    modify_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField()
    up_voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='answer_up_voters')
    down_voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='answer_down_voters')
    
    @property
    def vote_count(self):
        return self.up_voter.count() - self.down_voter.count()


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.sender.username}가 {self.receiver.username}에게: {self.content[:20]}"
    
    
    
# models.py
class Advertisement(models.Model):
    STATUS_CHOICES = (
        ('pending', '승인대기'),
        ('approved', '승인완료'),
        ('rejected', '반려'),
        ('ended', '종료')
    )

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='advertisement')
    external_link = models.URLField(verbose_name='광고 링크')
    main_banner = models.ImageField(
        upload_to='advertisements/main/',
        verbose_name='메인 배너',
        help_text='권장 크기: 1200x300px'
    )
    side_banner = models.ImageField(
        upload_to='advertisements/side/',
        verbose_name='사이드 배너',
        help_text='권장 크기: 400x300px'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='상태'
    )
    admin_message = models.TextField(blank=True, verbose_name='관리자 메시지')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='시작일')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='종료일')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=10)
    main_poster = models.BooleanField(default=False,verbose_name='메인포스터 여부')
    
    def clean(self):
        # question이 있을 때만 체크
        if hasattr(self, 'question') and self.question:
            if not self.question.author.is_advertise:
                raise ValidationError('광고주만 광고를 등록할 수 있습니다.')
        
        if self.status == 'approved' and (not self.start_date or not self.end_date):
            raise ValidationError('광고 승인 시 시작일과 종료일을 설정해야 합니다.')

    def save(self, *args, **kwargs):
        if self.main_poster:
            # 다른 히어로 배너들을 false로 설정
            Advertisement.objects.filter(main_poster=True).update(main_poster=False)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        
        

# 문의기능

# models.py의 Inquiry 모델 수정
class Inquiry(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

class InquiryComment(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']