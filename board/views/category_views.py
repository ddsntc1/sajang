from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from board.models import Question, Category
from django.db.models import Q,Count
from django.http import JsonResponse

def category_questions(request, slug):

    # --- 1) 기본 category 설정 ---
    if slug == 'all':
        category = type('Category', (), {'name': '전체게시판','slug': 'all','type': 'board'})()
        base_queryset = Question.objects.filter(category__type='board')

    elif slug == 'hot':
        category = type('Category', (), {'name': '인기게시판','slug': 'hot','type': 'board'})()
        base_queryset = (
            Question.objects
            .filter(category__type='board')
            .annotate(voter_count=Count('up_voter'))
            .filter(voter_count__gte=50)
        )

    else:
        category = get_object_or_404(Category, slug=slug)
        base_queryset = Question.objects.filter(category=category)

    base_queryset = (
        base_queryset
        .select_related("category", "author")
        .prefetch_related("up_voter")           
        .annotate(
            answer_count=Count("answer", distinct=True),
            upvote_count=Count("up_voter", distinct=True),
        )
    )

    kw = request.GET.get('kw', '')
    if kw:
        base_queryset = base_queryset.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(answer__content__icontains=kw)
        ).distinct()
        
    so = request.GET.get('so', 'recent')

    if so == 'recommend':
        base_queryset = base_queryset.order_by('-upvote_count', '-create_date')
    elif so == 'popular':
        base_queryset = base_queryset.order_by('-answer_count', '-create_date')
    else:
        base_queryset = base_queryset.order_by('-create_date')

    # --- 5) 공지 포함한 리스트 정렬 ---
    notices = base_queryset.filter(is_notice=True)
    normals = base_queryset.filter(is_notice=False)

    if slug != 'all' and category.type == 'board':
        # 전체 게시판 공지 추가
        all_notices = (
            Question.objects.filter(
                category__slug='all',
                is_notice=True
            )
            .select_related("category", "author")
            .prefetch_related("up_voter")
            .annotate(
                answer_count=Count("answer", distinct=True),
                upvote_count=Count("up_voter", distinct=True),
            )
            .order_by('-create_date')
        )
        final_queryset = list(all_notices) + list(notices) + list(normals)
    else:
        final_queryset = list(notices) + list(normals)

    # --- Pagination ---
    paginator = Paginator(final_queryset, 10)
    page = request.GET.get('page', '1')
    page_obj = paginator.get_page(page)
    max_idx = len(paginator.page_range)

    request.session['last_visited_type'] = category.type
    request.session['current_category'] = slug
    request.session['last_page'] = page
    request.session['last_sort'] = so
    request.session['last_keyword'] = kw

    context = {
        'category': category,
        'question_list': page_obj,
        'max_index': max_idx,
        'page': page,
        'kw': kw,
        'so': so,
        'current_type': category.type,
        'current_category': slug,
    }

    return render(request, 'board/question_list.html', context)

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
