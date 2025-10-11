from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from ..models import Question
from django.views.decorators.http import require_POST

@login_required(login_url='common:login')
@require_POST
def bookmark_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user in question.bookmarks.all():
        question.bookmarks.remove(request.user)
        is_bookmarked = False
    else:
        question.bookmarks.add(request.user)
        is_bookmarked = True
    return JsonResponse({'is_bookmarked': is_bookmarked})

@login_required(login_url='common:login')
def bookmarked_questions(request):
    question_list = request.user.bookmarked_questions.all().order_by('-create_date')
    
    # 페이징 처리
    paginator = Paginator(question_list, 10)
    page = request.GET.get('page', '1')
    page_obj = paginator.get_page(page)
    
    context = {
        'question_list': page_obj,
    }
    return render(request, 'board/bookmarked_questions.html', context)

