from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from ..models import Question,Advertisement
from django.utils import timezone
from django.db.models import F



def index(request):
    now = timezone.now()

    # 광고 영역 (문제 없음)
    active_advertisements = (
    Advertisement.objects
    .select_related("question", "question__author", "question__category")
    .filter(
        status='approved',
        start_date__lte=now,
        end_date__gte=now
        )
    )

    hero_advertisement = (
    active_advertisements
    .filter(main_banner__isnull=False, main_poster=True)
    .first()
    )

    main_advertisements = (
        active_advertisements
        .filter(main_banner__isnull=False)
        .exclude(main_poster=True)
        .order_by('order')
    )

    side_advertisements = (
        active_advertisements
        .filter(side_banner__isnull=False)
        .exclude(main_poster=True)
        .order_by('order')
    )


    # 1. 인기 게시글 (N+1 제거)
    hot_posts = list(Question.objects
    .select_related("category", "author")
    .prefetch_related("up_voter")
    .annotate(
        voter_count=Count("up_voter", distinct=True),
        answer_count=Count("answer", distinct=True)
    )
    .filter(
        create_date__gte=now - timezone.timedelta(days=31),
        category__type__in=["board", "story"]
    )
        .order_by("-voter_count")[:10]
    )

    government_news = list(Question.objects
        .select_related("category", "author")
        .annotate(answer_count=Count("answer"))
        .filter(category__slug="gov")
        .order_by("-create_date")[:5]
    )

    business_trends = list(Question.objects
        .select_related("category", "author")
        .annotate(answer_count=Count("answer"))
        .filter(category__slug="trend")
        .order_by("-create_date")[:5]
    )

    main_advertisements = list(main_advertisements)
    side_advertisements = list(side_advertisements)

    context = {
        "hero_advertisement": hero_advertisement,
        "main_advertisements": main_advertisements,
        "side_advertisements": side_advertisements,
        "hot_posts": hot_posts,
        "government_news": government_news,
        "business_trends": business_trends,
    }

    return render(request, "board/main.html", context)



def detail(request,question_id):
    
    question = get_object_or_404(Question, pk=question_id)
    
    # 조회수 부분
    if not request.session.get('viewed_questions'):
        request.session['viewed_questions'] = []
        
    if question_id not in request.session['viewed_questions']:
        # F() 표현식을 사용하여 race condition 방지
        Question.objects.filter(pk=question_id).update(view_count=F('view_count') + 1)
        request.session['viewed_questions'].append(question_id)
        request.session.modified = True
    question.refresh_from_db()
        
    # bread_crumb부분
    current_category = request.session.get('current_category', question.category.slug)
    context = {
        'question': question,
        'current_category': current_category,
        'current_type' : question.category.type,
    }
    return render(request, 'board/question_detail.html', context)


def faq(request):
    return render(request,'board/faq.html')


def privacy_law(request):
    if request.GET.get('modal') == '1':
        return render(request, 'board/partials/privacy_law_modal.html')
    return render(request,'board/privacy-law.html')

def using_rule(request):
    if request.GET.get('modal') == '1':
        return render(request, 'board/partials/using_rule_modal.html')
    return render(request,'board/using_rule.html')
