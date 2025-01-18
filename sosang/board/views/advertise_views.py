from django.shortcuts import render, get_object_or_404,redirect
from ..models import Question, Advertisement
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..forms import AdvertisementForm,AdvertisementApprovalForm
from django.contrib import messages


@login_required(login_url='common:login')
def advertisement_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.user != question.author or not request.user.is_advertise:
        raise PermissionDenied('광고 등록 권한이 없습니다.')
    
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.question = question
            advertisement.save()
            messages.success(request, '광고가 신청되었습니다. 관리자 승인 후 게시됩니다.')
            return redirect('board:detail', question_id=question.id)
    else:
        form = AdvertisementForm()
    
    context = {
        'form': form,
        'question': question
    }
    return render(request, 'board/advertisement/advertisement_form.html', context)


@login_required(login_url='common:login')
def advertisement_modify(request, question_id):
    advertisement = get_object_or_404(Advertisement, question_id=question_id)
    
    if request.user != advertisement.question.author and not request.user.is_admin:
        raise PermissionDenied('수정 권한이 없습니다.')
        
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES, instance=advertisement)
        if form.is_valid():
            advertisement = form.save()
            return redirect('board:detail', question_id=question_id)
    else:
        form = AdvertisementForm(instance=advertisement)
    
    context = {
        'form': form,
        'question': advertisement.question
    }
    return render(request, 'board/advertisement/advertisement_form.html', context)


@login_required(login_url='common:login')
def advertisement_delete(request, question_id):
    advertisement = get_object_or_404(Advertisement, question_id=question_id)
    
    if request.user != advertisement.question.author and not request.user.is_admin:
        raise PermissionDenied('삭제 권한이 없습니다.')
    
    if request.method == "POST":
        advertisement.delete()
        messages.success(request, '광고가 삭제되었습니다.')
        return redirect('board:detail', question_id=question_id)
    
    return render(request, 'board/advertisement/advertisement_confirm_delete.html', {
        'advertisement': advertisement
    })

@login_required(login_url='common:login')
def advertisement_list(request):
    # 일반 광고주는 자신의 광고만, 관리자는 모든 광고 조회
    if request.user.is_admin:
        advertisements = Advertisement.objects.all()
    else:
        advertisements = Advertisement.objects.filter(question__author=request.user)
        
    context = {'advertisements': advertisements}
    return render(request, 'board/advertisement/advertisement_list.html', context)

@login_required(login_url='common:login')
def advertisement_approve(request, question_id):
    # question_id로 Advertisement 찾기
    advertisement = get_object_or_404(Advertisement, question_id=question_id)
    
    if not request.user.is_admin:
        raise PermissionDenied('관리자만 접근 가능합니다.')
    
    if request.method == 'POST':
        form = AdvertisementApprovalForm(request.POST, instance=advertisement)
        if form.is_valid():
            advertisement = form.save()
            messages.success(request, '광고 상태가 업데이트되었습니다.')
            return redirect('board:advertisement_list')
    else:
        form = AdvertisementApprovalForm(instance=advertisement)
    
    context = {
        'form': form,
        'advertisement': advertisement,
    }
    return render(request, 'board/advertisement/advertisement_approve.html', context)