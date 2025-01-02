from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage,send_mail
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import JsonResponse

from datetime import timedelta

from ..forms import CustomUserCreationForm,UserUpdateForm,ProfileUpdateForm,FindIDForm,ResetPasswordForm
from board.models import Category
from ..models import PendingUser, CustomUser,BusinessType,Profile


def signup(request):
   if request.method == 'POST':
       form = CustomUserCreationForm(request.POST)
       if form.is_valid():
           # PendingUser에 임시 저장
           pending_user = PendingUser(
               username=form.cleaned_data['username'],
               user_id=form.cleaned_data['user_id'],
               email=form.cleaned_data['email'],
               password=make_password(form.cleaned_data['password1']),
               business_type=form.cleaned_data.get('business_type'),
               business_name=form.cleaned_data.get('business_name')
           )
           token = default_token_generator.make_token(form.instance)
           pending_user.activation_token = token
           pending_user.save()
           
           # 이메일 발송
           current_site = request.get_host()
           mail_subject = _('이메일 주소 인증')
           message = render_to_string('common/verification_email.html', {
               'user': pending_user,
               'domain': current_site,
               'uid': urlsafe_base64_encode(force_bytes(pending_user.pk)),
               'token': token,
           })
           
           email = EmailMessage(
               mail_subject,
               message,
               to=[pending_user.email]
           )
           email.content_subtype = "html"
           email.send()
           
           return render(request, 'common/verification_sent.html')
   else:
       form = CustomUserCreationForm()
       
    # is_business로 필터링
   business_categories = Category.objects.filter(
        is_business=True, 
        is_active=True
    ).order_by('order')
    
   return render(request, 'common/signup.html', {
        'form': form,
        'categories': business_categories,
    })


def get_business_types(request, category_id):
    business_types = BusinessType.objects.filter(
        category_id=category_id,
        is_active=True
    ).values('id', 'name')
    return JsonResponse(list(business_types), safe=False)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
        
        # 만료 시간 체크 (24시간)
        if timezone.now() - pending_user.created_at > timedelta(minutes=10):
            pending_user.delete()
            messages.error(request, '인증 링크가 만료되었습니다. 회원가입을 다시 진행해주세요.')
            return redirect('common:signup')
            
        # 나머지 인증 로직
        if pending_user.activation_token == token:
            user = CustomUser.objects.create(
                username=pending_user.username,
                user_id=pending_user.user_id,
                email=pending_user.email,
                password=pending_user.password,
                business_type=pending_user.business_type,
                business_name=pending_user.business_name,
                is_active=True,
                email_verified=True
            )
            pending_user.delete()
            login(request, user)
            messages.success(request, '이메일 인증이 완료되었습니다.')
            return redirect('index')
        else:
            messages.error(request, '인증 토큰이 유효하지 않습니다.')
            return redirect('index')
            
    except(TypeError, ValueError, OverflowError, PendingUser.DoesNotExist):
        messages.error(request, '인증 정보를 찾을 수 없습니다. 회원가입을 다시 진행해주세요.')
        return redirect('common:signup')