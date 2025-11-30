from .models import Category,Question
from common.models import CustomUser
from django.utils import timezone

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
    
    
    