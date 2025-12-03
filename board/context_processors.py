from .models import Category,Question
from common.models import CustomUser
from django.utils import timezone
from django.db.models import Count

def categories(request):
    return {
        'categories' : Category.objects.filter(is_active = True).order_by('order')
    }

def board_categories(request):
    board_categories = Category.objects.filter(is_active=True,type='board')
    today = timezone.now().date()
    return {
        'board_categories' : Category.objects.filter(is_active=True,type='board').order_by('order'),
        'board_Q_count' : Question.objects.filter(category__in=board_categories).count(),
        'user_count' : CustomUser.objects.filter(is_active=True).count(),
        'today_post_count' : Question.objects.filter(create_date__date=today).count()
            }


def board_business_categories(request):
    return {
        'business_categories' : Category.objects.filter(is_active=True,type='board',is_business=True).order_by('order'),
        'nonbusiness_categories' : Category.objects.filter(is_active=True,type='board',is_business=False).order_by('order')
            }
    
def each_categories(request):
    return {
        'story_categories' : Category.objects.filter(is_active=True,type='story').order_by('order'),
        'info_categories' : Category.objects.filter(is_active=True,type='info').order_by('order') ,
        'advertise_categories' : Category.objects.filter(is_active=True,type='advertise').order_by('order')       
    }
    
def global_context(request):
    today = timezone.now().date()

    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(q_count=Count('questions'))
        .order_by('order')
    )

    categories = list(categories)

    board_categories = [c for c in categories if c.type == 'board']
    story_categories = [c for c in categories if c.type == 'story']
    info_categories = [c for c in categories if c.type == 'info']
    advertise_categories = [c for c in categories if c.type == 'advertise']

    business_categories = [c for c in board_categories if c.is_business]
    nonbusiness_categories = [c for c in board_categories if not c.is_business]

    board_Q_count = sum(c.q_count for c in board_categories)

    user_count = CustomUser.objects.filter(is_active=True).count()
    today_post_count = Question.objects.filter(create_date__date=today).count()

    return {
        'categories': categories,
        'board_categories': board_categories,
        'story_categories': story_categories,
        'info_categories': info_categories,
        'advertise_categories': advertise_categories,
        'business_categories': business_categories,
        'nonbusiness_categories': nonbusiness_categories,
        'board_Q_count': board_Q_count,
        'user_count': user_count,
        'today_post_count': today_post_count,
    }
    