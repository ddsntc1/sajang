from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template.loader import render_to_string

from ..forms import FindIDForm,ResetPasswordForm
from ..models import CustomUser


def find_id(request):
   if request.method == 'POST':
       form = FindIDForm(request.POST)
       if form.is_valid():
           email = form.cleaned_data['email']
           try:
               user = CustomUser.objects.get(email=email)
               # 이메일로 아이디 전송
               subject = _('[소상공인 커뮤니티] 아이디 찾기 결과')
               message = render_to_string('common/find_id_email.html', {
                   'user': user,
               })
               
               email = EmailMessage(
                   subject=subject,
                   body=message,
                   to=[email]
               )
               email.content_subtype = "html"
               email.send()
               
               messages.success(request, '입력하신 이메일로 아이디를 발송했습니다.')
               return redirect('common:login')
           except CustomUser.DoesNotExist:
               messages.error(request, '해당 이메일로 가입된 계정이 없습니다.')
   else:
       form = FindIDForm()
   return render(request, 'common/find_id.html', {'form': form})

def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(user_id=user_id, email=email)
                # 비밀번호 재설정 링크 생성
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('common:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                # 이메일 발송
                subject = _('[소상공인 커뮤니티] 비밀번호 재설정')
                message = render_to_string('common/reset_password_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    to=[email]
                )
                email.content_subtype = "html"  # HTML 형식으로 설정
                email.send()

                messages.success(request, '비밀번호 재설정 링크를 이메일로 발송했습니다.')
                return redirect('common:login')
            except CustomUser.DoesNotExist:
                messages.error(request, '입력하신 정보와 일치하는 계정이 없습니다.')
    else:
        form = ResetPasswordForm()
    return render(request, 'common/reset_password.html', {'form': form})