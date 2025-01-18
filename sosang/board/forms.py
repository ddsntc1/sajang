from django import forms
from board.models import Question,Answer,Category,Advertisement,Inquiry,InquiryComment
from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'subject', 'content', 'is_notice']
        widgets = {
            'content': SummernoteWidget(),
            'subject': forms.TextInput(attrs={'class': 'form-control'})
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_admin:
            self.fields['is_notice'].widget = forms.HiddenInput()
            self.fields['category'].queryset = Category.objects.filter(is_active=True).exclude(slug__in=['all', 'hot'])
        
        if user and user.is_admin:
            self.fields['is_notice'].label = "공지사항으로 등록"
            
    def clean(self):
        cleaned_data = super().clean()
        if self.is_edit:
            cleaned_data['category'] = self.instance.category
        return cleaned_data

class QuestionModifyForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'content']  # category 제외

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content' : '답변내용',
        }
        
    

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['external_link', 'main_banner', 'side_banner']
        widgets = {
            'external_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://'
            }),
            'main_banner': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'side_banner': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class AdvertisementApprovalForm(forms.ModelForm):
   class Meta:
       model = Advertisement
       fields = ['status', 'start_date', 'end_date', 'admin_message']
       widgets = {
           'status': forms.Select(attrs={
               'class': 'form-control'
           }),
           'start_date': forms.DateTimeInput(attrs={
               'class': 'form-control',
               'type': 'datetime-local'
           }),
           'end_date': forms.DateTimeInput(attrs={
               'class': 'form-control',
               'type': 'datetime-local'
           }),
           'admin_message': forms.Textarea(attrs={
               'class': 'form-control',
               'rows': 3,
               'placeholder': '광고주에게 전달할 메시지를 입력하세요'
           })
       }

   def clean(self):
       cleaned_data = super().clean()
       start_date = cleaned_data.get('start_date')
       end_date = cleaned_data.get('end_date')
       status = cleaned_data.get('status')

       if status == 'approved':
           if not start_date:
               raise forms.ValidationError('승인 시 시작일을 설정해야 합니다.')
           if not end_date:
               raise forms.ValidationError('승인 시 종료일을 설정해야 합니다.')
           if start_date and end_date and start_date >= end_date:
               raise forms.ValidationError('종료일은 시작일보다 이후여야 합니다.')

       return cleaned_data
        
        
class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['subject', 'content']
        widgets = {
            'content': SummernoteWidget(),
        }

class InquiryCommentForm(forms.ModelForm):
    class Meta:
        model = InquiryComment
        fields = ['content']
        widgets = {
            'content': SummernoteWidget(),
        }