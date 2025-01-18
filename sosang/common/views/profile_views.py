from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from ..forms import UserUpdateForm,ProfileUpdateForm
from board.models import Category,Question
from ..models import BusinessType,Profile


@login_required(login_url='common:login')
def profile(request):
    # 프로필이 없는 경우 생성
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    remaining = request.user.get_remaining_reports_until_restriction()
    warning_message = None
    if remaining <= 5:
        warning_message = f"주의: 신고 {remaining}회 추가 누적 시 7일 정지됩니다."
        
        
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            old_username = request.user.username
            user = u_form.save()
            p_form.save()
            
            if old_username != user.username:
                messages.success(request, 
                    f'사용자 이름이 {old_username}에서 {user.username}으로 변경되었습니다.')
            else:
                messages.success(request, '프로필이 업데이트되었습니다.')
            
            return redirect('common:profile')
        else:
            for field, errors in u_form.errors.items():
                for error in errors:
                    messages.error(request, f'{u_form.fields[field].label}: {error}')
            for field, errors in p_form.errors.items():
                for error in errors:
                    messages.error(request, f'{p_form.fields[field].label}: {error}')
            
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    # 비즈니스 카테고리만 필터링
    business_categories = Category.objects.filter(
        type='board',
        is_business=True
    ).order_by('order')

    # 현재 사용자의 business_type이 있고, 그것의 category가 있다면 해당 카테고리의 business_types를 가져옴
    current_business_types = []
    if request.user.business_type and request.user.business_type.category:
        current_business_types = BusinessType.objects.filter(
            category=request.user.business_type.category
        ).order_by('name')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'business_categories': business_categories,
        'business_types': current_business_types,
        'warning_message': warning_message,
    }
    
    return render(request, 'common/profile/profile.html', context) # 수정


def user_profile(request, username): # 타 유저 프로필 조회
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    
    try : 
        introduction = profile_user.profile.introduction
    except Profile.DoesNotExist:
        introduction = ''
    
    context = {
        'profile_user': profile_user,
        'introduction': introduction,
    }
    return render(request, 'common/profile/user_profile.html', context)


@login_required(login_url='common:login')
def my_posts(request):
    tab = request.GET.get('tab', 'posts')  # default는 posts
    page = request.GET.get('page', '1')
    
    if tab == 'posts':
        # 내가 쓴 글
        questions = Question.objects.filter(author=request.user).order_by('-create_date')
    else:
        # 내가 댓글 단 글
        questions = Question.objects.filter(answer__author=request.user).distinct().order_by('-create_date')
    
    # 페이징 처리
    paginator = Paginator(questions, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'questions': page_obj,
        'page': page,
        'tab': tab,
    }
    return render(request, 'common/my_posts.html', context)