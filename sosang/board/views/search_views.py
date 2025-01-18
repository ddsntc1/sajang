# board/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from ..models import Category,Question
from common.models import CustomUser

def search(request):
    query = request.GET.get('q', '')
    
    if query:
        # 카테고리별로 검색 결과 그룹화
        categories = Category.objects.filter(is_active=True)
        search_results = {}
        
        for category in categories:
            # 각 카테고리별 검색 결과
            questions = Question.objects.filter(
                Q(category=category),
                Q(subject__icontains=query) |    
                Q(content__icontains=query) |
                Q(answer__content__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct().order_by('-create_date')
            
            if questions.exists():
                search_results[category] = {
                    'top_results': questions[:5],
                    'total_count': questions.count(),
                }

        # 유저 검색 - username(닉네임)으로만 검색
        users = CustomUser.objects.filter(
            ~Q(id=request.user.id),  # 현재 사용자 제외
            username__icontains=query,  # username이 닉네임 필드
            is_active=True  # 활성화된 사용자만
        )
        
        search_users = {user.id: user.username for user in users}
        
        context = {
            'query': query,
            'search_results': search_results,
            'search_users': search_users,
        }
    else:
        context = {'query': ''}
    
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