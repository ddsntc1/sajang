# common/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Report, CustomUser
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@login_required(login_url='common:login')
@require_http_methods(["POST"])
def report_user(request, username):
    try:
        data = json.loads(request.body)
        reported_user = get_object_or_404(CustomUser, username=username)
        
        if request.user == reported_user:
            return JsonResponse({'status': 'error', 'message': '자기 자신을 신고할 수 없습니다.'})
        
        today = timezone.now().date()
        if Report.objects.filter(
            reporter=request.user,
            reported_user=reported_user,
            created_at__date=today
        ).exists():
            return JsonResponse({'status': 'error', 'message': '이미 오늘 이 사용자를 신고했습니다.'})

        Report.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            category=data.get('category'),
            reason="사용자 신고" # 기본값
        )
        
        return JsonResponse({'status': 'success', 'message': '신고가 접수되었습니다.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})