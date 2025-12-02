from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, BusinessType,Profile
from django.core.validators import RegexValidator
import re
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


        
        
class CustomUserCreationForm(UserCreationForm):
    business_type = forms.ModelChoiceField(
        queryset=BusinessType.objects.filter(is_active=True),
        required=False,
        label=_('업종'),
        empty_label=_('선택하지 않음')
    )
    FORBIDDEN_WORDS = ['admin', 'sex', 'fuck', 'administrator', '관리자', '운영자','광고자','개발자']
    
    user_id_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]{4,20}$',
        message='아이디는 4~20자의 영문, 숫자, 밑줄(_)만 사용 가능합니다.'
    )
    
    user_id = forms.CharField(
        validators=[user_id_validator],
        label='아이디'
    )

    privacy_agree = forms.BooleanField(
        required=True,
        label=_('개인정보 처리방침 동의')
    )
    terms_agree = forms.BooleanField(
        required=True,
        label=_('이용약관 동의')
    )
    
    username = forms.CharField(
        min_length=2,
        max_length=10,
        label='닉네임'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'user_id', 'email', 'business_type', 'business_name', 'terms_agree', 'privacy_agree', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('이미 등록된 이메일입니다.'))
        return email

    def clean_user_id(self):
        user_id = self.cleaned_data.get('user_id')
        
        if CustomUser.objects.filter(user_id=user_id).exists():
            raise forms.ValidationError(_('이미 사용중인 아이디입니다.'))
        
        for word in self.FORBIDDEN_WORDS:
            if word in user_id.lower():
                raise forms.ValidationError(
                    '부적절한 아이디입니다. 다른 아이디를 사용해주세요.'
                )
                
        return user_id
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(_('이미 사용중인 닉네임입니다.'))
            
        # 특수문자 검사
        if re.search('[!@#$%^&*(),.?":{}|<>]', username):
            raise forms.ValidationError(
                '닉네임에 특수문자를 사용할 수 없습니다.'
            )
        # 금지어 검사
        for word in self.FORBIDDEN_WORDS:
            if word in username.lower():
                raise forms.ValidationError(
                    '부적절한 닉네임입니다. 다른 닉네임을 사용해주세요.'
                )
        return username
    
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['introduction']
        widgets = {
            'introduction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '자기소개를 입력해주세요'
            })
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'business_type', 'business_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사용자 이름'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사업장 이름'
            })
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        user = get_user_model().objects.filter(username=username)
        
        if user.exists() and user.first() != self.instance:
            raise ValidationError("이미 사용 중인 사용자 이름입니다.")
            
        return username
        
        

class FindIDForm(forms.Form):
    email = forms.EmailField(
        label=_('이메일'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '가입시 등록한 이메일을 입력하세요'
        })
    )

class ResetPasswordForm(forms.Form):
    user_id = forms.CharField(
        label=_('아이디'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디를 입력하세요'
        })
    )
    email = forms.EmailField(
        label=_('이메일'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '가입시 등록한 이메일을 입력하세요'
        })
    )
