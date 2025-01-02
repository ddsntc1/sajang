from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from board.models import Question, Category
from django.db.models import Q,Count
from django.http import JsonResponse

def category_questions(request, slug):
    
    if slug == 'all':
        category = type('Category', (), {'name': '전체게시판', 'slug': 'all','type': 'board'})()
        question_list = Question.objects.filter(category__type='board')
    elif slug == 'hot':
        category = type('Category', (), {'name': '인기게시판', 'slug': 'hot','type': 'board'})()
        question_list = Question.objects.filter(
            category__type='board'
        ).annotate(
            voter_count=Count('up_voter')
        ).filter(
            voter_count__gte=50
        )
    else:
        category = get_object_or_404(Category, slug=slug)
        question_list = Question.objects.filter(category=category)

    # 검색 기능
    so = request.GET.get('so', 'recent')
    kw = request.GET.get('kw', '')

    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(answer__content__icontains=kw)
        ).distinct()

    # 정렬 적용
    if so == 'recommend':
        question_list = question_list.annotate(voter_count=Count('up_voter')).order_by('-voter_count', '-create_date')
    elif so == 'popular':
        question_list = question_list.annotate(answer_count=Count('answer')).order_by('-answer_count', '-create_date')
    else:  # recent
        question_list = question_list.order_by('-create_date')

    # 공지사항과 일반 게시글 분리 후 결합
    # 이미 정렬된 상태를 유지하면서 공지사항을 상단에 배치
    
    notice_list = list(question_list.filter(is_notice=True))
    normal_list = list(question_list.filter(is_notice=False))
    
    if slug != 'all' and category.type == 'board':
        all_notices = Question.objects.filter(
            category__slug='all',
            is_notice=True
        ).order_by('-create_date')
        
        question_list = list(all_notices) + notice_list + normal_list
    else:
        question_list = notice_list + normal_list

    # 페이징 처리
    paginator = Paginator(question_list, 10)
    page = request.GET.get('page', '1')
    page_obj = paginator.get_page(page)
    max_idx = len(paginator.page_range)
    
    #세션 저장 - 목록으로 기능
    request.session['last_visited_type'] = category.type
    request.session['current_category'] = slug # current session에 저장 -> bread_crumb // 글 작성시 기존 게시판 돌아가는 기능
    request.session['last_page'] = request.GET.get('page', '1')
    request.session['last_sort'] = request.GET.get('so', 'recent')
    request.session['last_keyword'] = request.GET.get('kw', '')
    
    context = {
        'category': category,
        'question_list': page_obj,
        'max_index': max_idx,
        'page': page,
        'kw': kw,
        'so': so,
        # 사이드바를 위한 context
        'current_type': category.type,  # 현재 타입
        'current_category': slug , # 현재 카테고리
    }

    return render(request, 'board/question_list.html', context)

# views.py
def get_categories_by_type(request):
    board_type = request.GET.get('type', '')
    
    if request.user.is_admin: # 관리자
        categories = Category.objects.filter(
            type=board_type,
            is_active=True
        )
        
    elif request.user.is_advertise: # 광고주
        categories = Category.objects.filter(
            type=board_type,
            is_active=True
        ).exclude(slug__in=['all', 'hot'])
        
    else:
        categories = Category.objects.filter(
            type=board_type,
            is_active=True
        ).exclude(slug__in=['all', 'hot']).exclude(type='advertise')
        
    
    data = [{'id': cat.id, 'name': cat.name, 'slug':cat.slug} for cat in categories]
    return JsonResponse(data, safe=False)
