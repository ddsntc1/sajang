from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from ..models import Message
from common.models import CustomUser

@login_required(login_url='common:login')
def message_list(request):
    """사용자의 모든 대화 목록을 보여주는 뷰"""
    all_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver')
    
    conversations = _group_messages_by_user(all_messages, request.user)
    
    return render(request, 'board/message/message_list.html', {
        'conversations': conversations.values()
    })

@login_required(login_url='common:login')
def send_message(request):
    """새 메시지 전송 뷰"""
    initial_receiver_username = request.GET.get('receiver', '')
    initial_receiver = None
    
    # username으로 사용자 찾기
    if initial_receiver_username:
        try:
            initial_receiver = CustomUser.objects.get(username=initial_receiver_username)
        except CustomUser.DoesNotExist:
            messages.error(request, '존재하지 않는 사용자입니다.')
    
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        
        if not receiver_username or not content:
            messages.error(request, '수신자와 내용을 모두 입력해주세요.')
            return render(request, 'board/message/send_message.html', {
                'initial_receiver': initial_receiver
            })
        
        try:
            receiver = CustomUser.objects.get(username=receiver_username)
            
            if receiver == request.user:
                messages.error(request, '자기 자신에게는 메시지를 보낼 수 없습니다.')
                return render(request, 'board/message/send_message.html', {
                    'initial_receiver': initial_receiver
                })
            
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            return redirect('board:conversation_detail', user_id=receiver.id)
            
        except CustomUser.DoesNotExist:
            messages.error(request, '존재하지 않는 사용자입니다.')
            return render(request, 'board/message/send_message.html', {
                'initial_receiver': initial_receiver
            })
    
    return render(request, 'board/message/send_message.html', {
        'initial_receiver': initial_receiver
    })
    
@login_required(login_url='common:login')
def conversation_detail(request, user_id):
    """특정 사용자와의 대화 내역을 보여주는 뷰"""
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    messages_queryset = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    # 읽지 않은 메시지 읽음 처리
    messages_queryset.filter(
        receiver=request.user, 
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'board/message/conversation_detail.html', {
        'other_user': other_user,
        'message_list': messages_queryset
    })

@login_required(login_url='common:login')
def search_users(request):
    """사용자 검색 API"""
    query = request.GET.get('q', '')
    if len(query) >= 2:
        users = CustomUser.objects.filter(
            ~Q(id=request.user.id),
            username__icontains=query
        )[:10]
        return JsonResponse([
            {'username': user.username} for user in users
        ], safe=False)
    return JsonResponse([], safe=False)

def _group_messages_by_user(messages, current_user):
    """메시지를 대화 상대별로 그룹화하는 헬퍼 함수"""
    conversations = {}
    
    for msg in messages:
        other_user = msg.receiver if msg.sender == current_user else msg.sender
        
        if other_user.id not in conversations:
            conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': 0
            }
        else:
            if msg.created_at > conversations[other_user.id]['last_message'].created_at:
                conversations[other_user.id]['last_message'] = msg
        
        if msg.receiver == current_user and not msg.is_read:
            conversations[other_user.id]['unread_count'] += 1

    return dict(sorted(
        conversations.items(),
        key=lambda x: x[1]['last_message'].created_at,
        reverse=True
    ))