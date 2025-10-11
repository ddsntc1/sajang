from django.contrib import admin
from .models import Category, Question,Answer,Advertisement
from .models import Inquiry, InquiryComment
# Register your models here.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']
    list_display = ['subject', 'get_category_name', 'is_notice', 'create_date']  # category 대신 get_category_name 사용
    list_editable = ['is_notice']
    list_filter = ['category', 'is_notice']

    def get_category_name(self, obj):
        return obj.category.name  # category의 name 필드를 반환
    get_category_name.short_description = '카테고리'  # 관리자 페이지에서 보여질 열 이름
    get_category_name.admin_order_field = 'category__name'  # 이 열로 정렬 가능하게 함

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_notice=False)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['subject']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active','is_business','type']  # 목록에서 보여줄 필드들
    list_editable = ['order', 'is_active','is_business','type']  # 목록에서 바로 수정 가능한 필드들
    

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['question_subject', 'order', 'status', 'start_date', 'end_date', 'created_at']
    list_editable = ['order']
    list_filter = ['status']
    search_fields = ['question__subject', 'question__content', 'question__author__username']
    readonly_fields = ['created_at', 'updated_at']

    def question_subject(self, obj):
        return obj.question.subject
    question_subject.short_description = '제목'  # admin 페이지에서 보여질 컬럼명

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['question', 'created_at', 'updated_at']
        return ['created_at', 'updated_at']
    
    
    

class InquiryCommentInline(admin.TabularInline):
    model = InquiryComment
    extra = 1

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['subject', 'author', 'created_at', 'is_answered']
    list_filter = ['is_answered']
    search_fields = ['subject', 'content', 'author__username']
    inlines = [InquiryCommentInline]