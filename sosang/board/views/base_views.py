from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q,Count
from ..models import Question,Category,Advertisement
from django.utils import timezone
from django.db.models import F

# views.py
# def index(request):
#    categories = Category.objects.all()
#    popular_posts = {}
   
#    for category in categories:
#        posts = Question.objects.filter(
#            category=category
#        ).annotate(
#            voter_count=Count('up_voter')
#        ).order_by('-voter_count')[:5]
#        popular_posts[category] = posts

#    return render(request, 'board/main.html', {'popular_posts': popular_posts})

def index(request):
    now = timezone.now()
    
    # 승인된 활성 광고만 가져오기
    active_advertisements = Advertisement.objects.filter(
        status='approved',
        start_date__lte=now,
        end_date__gte=now
    )
    
    # 메인  포스터터
    hero_advertisement = active_advertisements.filter(
        main_banner__isnull = False,
        main_poster = True
    ).first()
    
    # 메인 배너용 광고
    main_advertisements = active_advertisements.filter(
        main_banner__isnull=False  # 메인 배너가 있는 광고
    ).exclude(main_poster=True).order_by('order')
    
    # 사이드 배너용 광고
    side_advertisements = active_advertisements.filter(
        side_banner__isnull=False  # 사이드 배너가 있는 광고
    ).exclude(main_poster=True).order_by('order')


    hot_posts = Question.objects.annotate(
        voter_count=Count('up_voter')
    ).filter(
        create_date__gte=now - timezone.timedelta(days=31),
        category__type__in=['board', 'story'] 
    ).order_by('-voter_count')[:10]

    government_news = Question.objects.filter(category__slug = 'gov').order_by('-create_date')[:5]

    context = {
        'hero_advertisement' : hero_advertisement,
        'main_advertisements': main_advertisements,
        'side_advertisements': side_advertisements,
        'hot_posts': hot_posts,
        'government_news' : government_news,
    }
    return render(request, 'board/main.html', context)



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
    return render(request,'board/privacy-law.html')

def using_rule(request):
    return render(request,'board/using_rule.html')