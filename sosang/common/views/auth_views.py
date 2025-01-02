# common/views/auth_views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from ..models import UserRestrictionHistory
from django.utils import timezone
from django.utils.timezone import datetime
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 유저가 정지된 경우 처리
            if user.is_restricted:
                latest_restriction = UserRestrictionHistory.objects.filter(
                        user=user,
                        unrestricted_at__isnull=True
                    ).order_by('-restricted_at').first()
                
                # 정지 기한이 지난경우 -> 정지 해제제
                if user.restrict_end_date and user.restrict_end_date <= now():
                    # 정지 해제 처리
                    user.is_restricted = False
                    user.restrict_end_date = None
                    user.save(update_fields=['is_restricted', 'restrict_end_date'])
                    
                    if latest_restriction:
                        latest_restriction.unrestricted_at = now()
                        latest_restriction.unrestricted_reason = "제한 기간 만료로 인한 자동 해제"
                        latest_restriction.save(update_fields=['unrestricted_at', 'unrestricted_reason'])
                    
                    login(request, user)
                    messages.success(request, '계정 정지가 해제되었습니다. 환영합니다!')
                    return redirect('index')
                else:
                    # 정지 중인 경우 남은 시간 계산
                    remaining = user.restrict_end_date - now()
                    days = remaining.days
                    hours, remainder = divmod(remaining.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    remaining_time = f"{days}일 {hours}시간 {minutes}분"

                    context = {
                        'user_id': user.user_id,
                        'username': user.username,
                        'restriction_reason': latest_restriction.restriction_reason if latest_restriction else "알 수 없는 사유",
                        'remaining_time': remaining_time,
                        'restrict_end_date': user.restrict_end_date if user.restrict_end_date else None
                    }
                    return render(request, 'common/restricted.html', context)
            else:
                # 정상 로그인
                login(request, user)
                messages.success(request, f'환영합니다, {user.username}님!')
                return redirect('index')
        else:
            # 인증 실패
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')

    return render(request, 'common/login.html')


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='common:login')
def delete_account(request):
    if request.method == 'POST':
        if request.POST.get('confirm_delete') == 'yes':
            user = request.user
            logout(request)
            user.profile.delete()
            user.delete()
            messages.success(request,'계정이 성공적으로 삭제되었습니다.')
            return redirect('index')
    # get요청시 확인 페이지 표시
    return render(request,'common/delete_confirmation.html')