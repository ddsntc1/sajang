from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404,render
from django.contrib import messages
from board.models import Question
from django.utils import timezone
from datetime import timedelta
from ..models import CustomUser,UserRestrictionHistory,AdvertiserHistory
from django.db import transaction

def is_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_superuser)

@require_POST
@user_passes_test(is_admin)
def toggle_notice(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.is_notice = not question.is_notice
    question.save()
    return JsonResponse({'status': 'success'})

@require_POST
@user_passes_test(is_admin)
def admin_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return JsonResponse({'status': 'success'})


# 관리자만 접근 가능하도록 제한
@user_passes_test(is_admin, login_url='login')
def restrict_user(request):
    user_info = None
    if request.method == "POST":
        username = request.POST.get('username')
        period = request.POST.get('period')  # ajax에서 보내는 이름과 일치
        reason = request.POST.get('reason')

        # 입력값 검증
        if not username or not reason:
            messages.error(request, "모든 필드를 입력해주세요.")
            return render(request, 'common/admin/restrict_user.html', {'user_info': user_info})

        # 사용자 검색
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(username=username)

                # 정지 기간 계산
                days = int(period)

                # 정지 해제 날짜 계산
                restrict_end_date = timezone.now() + timedelta(days=days)
                user.is_restricted = True
                user.restrict_end_date = restrict_end_date
                user.save()
                
                UserRestrictionHistory.objects.create(
                    user=user,
                    restricted_by=request.user,
                    restriction_reason=reason,
                    restriction_period=days,
                    unrestricted_at=None  # 아직 해제되지 않음
                )

                messages.success(
                    request,
                    f"{user.username} (ID: {user.user_id}, Email: {user.email}) 님이 {restrict_end_date}까지 정지되었습니다."
                )
        except CustomUser.DoesNotExist:
            messages.error(request, "해당 닉네임의 사용자를 찾을 수 없습니다.")
        except Exception as e:
            messages.error(request, f"오류가 발생했습니다: {str(e)}")
            
        return render(request, 'common/admin/user_manage.html', {'user_info': user_info})

    return render(request, 'common/admin/user_manage.html', {'user_info': user_info})


@require_POST
@user_passes_test(is_admin, login_url='login')
def unrestrict_user(request):
    try:
        with transaction.atomic():
            username = request.POST.get('username')
            reason = request.POST.get('reason')
            
            user =get_object_or_404(CustomUser,username = username)
            
            restriction = UserRestrictionHistory.objects.filter(
                user = user,
                unrestricted_at__isnull = True
            ).first()
            
            if not restriction:
                return JsonResponse({
                    'error' : '해당 사용자는 현재 정지 상태가 아닙니다.'
                }, status = 400)
                
            restriction.unrestricted_at = timezone.now()
            restriction.unrestriction_reason = reason
            restriction.save()
            
            user.is_restricted = False
            user.restrict_end_date = None
            user.save()
            
            return JsonResponse({
                'message' : '사용자 정지가 해제되었습니다.',
                'user_id' : user.id,
            })
        
    except Exception as e:
        return JsonResponse({
            'error' : f'정지 해제 중 오류가 발생했습니다: {str(e)}'
        },status = 500)
        
@require_POST
@user_passes_test(is_admin, login_url='login')
def toggle_advertise(request):
    try:
        with transaction.atomic():
            username = request.POST.get('username', '').strip()
            user = get_object_or_404(CustomUser,username = username)
            
            user.is_advertise = not user.is_advertise
            user.save()
            
            AdvertiserHistory.objects.create(
                user = user,
                changed_by = request.user,
                is_advertiser = user.is_advertise,
                reason = f"관리자에 의한 광고주 권한 {'부여' if user.is_advertise else '해제'}"
            )
            
            return JsonResponse({
                'message' : f"광고주 권한이 {'부여' if user.is_advertise else '해제'}되었습니다.",
                'user_id' : user.id,
                'is_advertise' : user.is_advertise
            })
    except Exception as e:
        return JsonResponse({
            'error' : f'광고주 권한 변경 중 오류가 발생했습니다: {str(e)}'
        },status = 500)

@require_POST
def fetch_user_info(request):

    username = request.POST.get('username', '').strip()

    if not username:
        return JsonResponse({'error': '닉네임을 입력해주세요.'}, status=400)

    try:
        user = CustomUser.objects.get(username=username)
        return JsonResponse({
            'user_id': user.user_id,
            'email': user.email,
            'is_restricted': user.is_restricted,
            'is_advertise': user.is_advertise,
            'restrict_end_date': user.restrict_end_date.strftime('%Y-%m-%d %H:%M:%S') if user.is_restricted else None,
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': '사용자를 찾을 수 없습니다.'}, status=404)
    

