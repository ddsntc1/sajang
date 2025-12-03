# board/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q,Count
from django.shortcuts import render
from ..models import Category,Question
from common.models import CustomUser

def search(request):
    query = request.GET.get('q', '')
    context = {'query': query}
    if not query:
        return render(request, 'board/search/search_results.html', context)
    # 전체 검색 대상
    base_qs = (
        Question.objects
        .select_related("category", "author")
        .prefetch_related("answer_set")
        .annotate(answer_count=Count("answer", distinct=True))
        .filter(
            Q(subject__icontains=query) |
            Q(content__icontains=query) |
            Q(answer__content__icontains=query) |
            Q(author__username__icontains=query)
        )
        .order_by("-create_date")
    )
    # 카테고리별로 한번에 그룹핑 (Python 측에서)
    search_results = {}
    for question in base_qs:
        cat = question.category
        if not cat:
            continue
        if cat not in search_results:
            search_results[cat] = {
                "top_results": [],
                "total_count": 0,
            }
        # total count
        search_results[cat]["total_count"] += 1
        # 상위 5개만 저장
        if len(search_results[cat]["top_results"]) < 5:
            search_results[cat]["top_results"].append(question)

    # 사용자 검색
    users = CustomUser.objects.filter(
        ~Q(id=request.user.id),
        username__icontains=query,
        is_active=True
    )

    search_users = {u.id: u.username for u in users}

    context.update({
        "search_results": search_results,
        "search_users": search_users
    })

    return render(request, 'board/search/search_results.html', context)

# 카테고리별 검색 결과 상세 보기
def category_search_results(request, category_slug):
    query = request.GET.get('q', '')
    category = get_object_or_404(Category, slug=category_slug)
    
    questions = Question.objects.filter(
        Q(category=category),
        Q(subject__icontains=query) |
        Q(content__icontains=query) |
        Q(answer__content__icontains=query) |
        Q(author__username__icontains=query)
    ).distinct().order_by('-create_date')
    
    paginator = Paginator(questions, 10)
    page = request.GET.get('page', 1)
    questions = paginator.get_page(page)
    
    return render(request, 'board/search/category_search_results.html', {
        'category': category,
        'questions': questions,
        'query': query,
    })