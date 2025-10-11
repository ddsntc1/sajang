# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Inquiry, InquiryComment
from ..forms import InquiryForm, InquiryCommentForm

@login_required(login_url='common:login')
def inquiry_list(request):
    if request.user.is_admin:
        inquiries = Inquiry.objects.all()
    else:    
        inquiries = Inquiry.objects.filter(author=request.user)
    return render(request, 'board/inquiry/inquiry_list.html', {'inquiries': inquiries})

@login_required(login_url='common:login')
def inquiry_detail(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    if inquiry.author != request.user and not request.user.is_admin:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('board:inquiry_list')
    
    
    form = InquiryCommentForm()  # 답변 폼 추가
    return render(request, 'board/inquiry/inquiry_detail.html', {
        'inquiry': inquiry,
        'form': form,
    })

@login_required(login_url='common:login')
def inquiry_create(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.author = request.user
            inquiry.save()
            messages.success(request, '문의가 등록되었습니다.')
            return redirect('board:inquiry_detail', inquiry_id=inquiry.id)
    else:
        form = InquiryForm()
    return render(request, 'board/inquiry/inquiry_form.html', {'form': form})

@login_required(login_url='common:login')
def inquiry_modify(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if inquiry.author != request.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('board:inquiry_detail', inquiry_id=inquiry.id)
        
    if request.method == 'POST':
        form = InquiryForm(request.POST, instance=inquiry)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, '문의가 수정되었습니다.')
            return redirect('board:inquiry_detail', inquiry_id=inquiry.id)
    else:
        form = InquiryForm(instance=inquiry)
    
    return render(request, 'board/inquiry/inquiry_form.html', {
        'form': form,
        'is_modify': True,
    })

@login_required(login_url='common:login')
def inquiry_delete(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if inquiry.author != request.user:
        messages.error(request, '삭제 권한이 없습니다.')
    else:
        inquiry.delete()
        messages.success(request, '문의가 삭제되었습니다.')
    
    return redirect('board:inquiry_list')

@login_required(login_url='common:login')
def inquiry_comment_create(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if not request.user.is_admin:
        messages.error(request, '답변 권한이 없습니다.')
        return redirect('board:inquiry_detail', inquiry_id=inquiry.id)
        
    if request.method == 'POST':
        form = InquiryCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.inquiry = inquiry
            comment.author = request.user
            comment.save()
            inquiry.is_answered = True
            inquiry.save()
            messages.success(request, '답변이 등록되었습니다.')
    
    return redirect('board:inquiry_detail', inquiry_id=inquiry.id)

@login_required(login_url='common:login')
def inquiry_comment_modify(request, comment_id):
    comment = get_object_or_404(InquiryComment, id=comment_id)
    
    if not request.user.is_admin:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('board:inquiry_detail', inquiry_id=comment.inquiry.id)
        
    if request.method == 'POST':
        form = InquiryCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            messages.success(request, '답변이 수정되었습니다.')
            return redirect('board:inquiry_detail', inquiry_id=comment.inquiry.id)
    else:
        form = InquiryCommentForm(instance=comment)
    
    return render(request, 'board/inquiry/inquiry_comment_form.html', {
        'form': form,
        'inquiry': comment.inquiry,
    })

@login_required(login_url='common:login')
def inquiry_comment_delete(request, comment_id):
    comment = get_object_or_404(InquiryComment, id=comment_id)
    
    if not request.user.is_admin:
        messages.error(request, '삭제 권한이 없습니다.')
    else:
        inquiry = comment.inquiry
        comment.delete()
        
        # 답변이 없으면 is_answered를 False로 변경
        if not inquiry.comments.exists():
            inquiry.is_answered = False
            inquiry.save()
            
        messages.success(request, '답변이 삭제되었습니다.')
    
    return redirect('board:inquiry_detail', inquiry_id=comment.inquiry.id)