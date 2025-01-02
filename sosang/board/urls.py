
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import base_views,question_views,answer_views,vote_views,category_views,bookmark_views,message_views,search_views,advertise_views,inquiry_views

app_name = 'board'



urlpatterns = [
    # base_views.py
    path('',base_views.index, name = 'index'),
    path('question/<int:question_id>/', base_views.detail, name = 'detail'),
    path('faq/',base_views.faq,name='faq'),
    path('privacy_law/',base_views.privacy_law,name='privacy_law'),
    path('using_rule/',base_views.using_rule,name='using_rule'),
    
    #category_views.py
    path('category/<str:slug>',category_views.category_questions, name = 'category_questions'),
    path('api/categories/', category_views.get_categories_by_type, name='get_categories_by_type'),
    
    # question_views.py
    path('question/create/', question_views.question_create,name='question_create'),
    path('question/modify/<int:question_id>/',question_views.question_modify,name='question_modify'),
    path('question/delete/<int:question_id>/',question_views.question_delete,name='question_delete'),
    
    path('advertisement/create/<int:question_id>', advertise_views.advertisement_create, name='advertisement_create'),
    path('advertisement/list/', advertise_views.advertisement_list, name='advertisement_list'),
    path('advertisement/modify/<int:question_id>/', advertise_views.advertisement_modify, name='advertisement_modify'),
    path('advertisement/delete/<int:question_id>/', advertise_views.advertisement_delete, name='advertisement_delete'),
    path('advertisement/approve/<int:question_id>/', advertise_views.advertisement_approve, name='advertisement_approve'),
    
    # 좋아요 view
    path('question/<int:question_id>/bookmark/', bookmark_views.bookmark_question, name='bookmark_question'),
    path('questions/bookmarked/',bookmark_views.bookmarked_questions,name='bookmarked_questions'),
    
    # answer_views.py
    path('answer/create/<int:question_id>/', answer_views.answer_create,name='answer_create'),
    path('answer/modify/<int:answer_id>/',answer_views.answer_modify,name="answer_modify"),
    path('answer/delete/<int:answer_id>/',answer_views.answer_delete,name='answer_delete'),
    
    path('search/', search_views.search, name='search'),
    path('search/<str:category_slug>/', search_views.category_search_results, name='category_search_results'),
    
    #vote_views.py
    path('upvote/question/<int:question_id>/',vote_views.upvote_question,name='upvote_question'),
    path('downvote/question/<int:question_id>/',vote_views.downvote_question,name='downvote_question'),
    path('upvote/answer/<int:answer_id>/',vote_views.upvote_answer,name='upvote_answer'),
    path('downvote/answer/<int:answer_id>/',vote_views.downvote_answer,name='downvote_answer'),

    
    path('messages/', message_views.message_list, name='message_list'),
    path('messages/conversation/<int:user_id>/', message_views.conversation_detail, name='conversation_detail'),
    path('messages/send/', message_views.send_message, name='send_message'),
    path('api/search-users/', message_views.search_users, name='search_users'),
    
    #문의하기
    path('inquiry/', inquiry_views.inquiry_list, name='inquiry_list'),
    path('inquiry/create/', inquiry_views.inquiry_create, name='inquiry_create'),
    path('inquiry/modify/<int:inquiry_id>/', inquiry_views.inquiry_modify, name='inquiry_modify'),
    path('inquiry/delete/<int:inquiry_id>/', inquiry_views.inquiry_delete, name='inquiry_delete'),
    
    path('inquiry/<int:inquiry_id>/', inquiry_views.inquiry_detail, name='inquiry_detail'),
    path('inquiry/<int:inquiry_id>/comment/', inquiry_views.inquiry_comment_create, name='inquiry_comment_create'),
    path('inquiry/comment/modify/<int:comment_id>/', inquiry_views.inquiry_comment_modify, name='inquiry_comment_modify'),
    path('inquiry/comment/delete/<int:comment_id>/', inquiry_views.inquiry_comment_delete, name='inquiry_comment_delete'),

]
