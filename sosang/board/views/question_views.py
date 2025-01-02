from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from ..forms import QuestionForm
from ..models import Question,Category



@login_required(login_url='common:login')
def question_create(request, category_slug=None):
    initial_type = 'board'  # 기본값 설정
    initial_category = None
    
    # 카테고리 슬러그가 제공된 경우 해당 카테고리 정보 가져오기
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            initial_type = category.type
            initial_category = category
        except Category.DoesNotExist:
            pass
    
    

    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.create_date = timezone.now()
            
            # 전체 게시판 공지사항 처리
            if question.category.slug == 'all':
                if not request.user.is_staff:
                    messages.error(request, '권한이 없습니다.')
                    return redirect('board:index')
                question.is_notice = True
            
            question.save()
            
            if question.category.type == 'advertise' and request.user.is_advertise:
                return redirect('board:advertisement_create', question_id=question.id)
            
            return redirect('board:category_questions', slug=question.category.slug)

    else:
        initial = {}
        if initial_category:
            initial['category'] = initial_category
        form = QuestionForm(user=request.user, initial=initial)

    context = {
        'form': form,
        'initial_type': initial_type,
    }

    return render(request, 'board/question_form.html', context)

@login_required(login_url='common:login')
def question_modify(request,question_id):
    question = get_object_or_404(Question,pk=question_id)
    if request.user != question.author:
        messages.error(request,'수정권한이 없습니다.')
        return redirect('board:detail',question_id = question.id)
    
    if request.method == "POST":
        form = QuestionForm(request.POST,instance = question)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()
            question.save()
            return redirect('board:detail',question_id = question.id)
    else:
        form = QuestionForm(instance=question)
    context = {
        'category':question.category,
        'form':form,
        'category_type':question.category.type,
        }
    return render(request,'board/question_form.html',context)

@login_required(login_url='common:login')
def question_delete(request,question_id):
    """pybo 질문 삭제"""
    question = get_object_or_404(Question,pk=question_id)
    category = question.category
    if request.user != question.author:
        messages.error(request,'삭제권한이 없습니다.')
        return redirect('board:detail',question_id = question.id)
    question.delete()
    return redirect('board:category_questions',slug = category.slug)

