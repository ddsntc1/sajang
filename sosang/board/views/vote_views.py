from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..models import Question,Answer

# 게시글 추천 비추천 기능

@login_required(login_url='common:login')
def upvote_question(request,question_id):
    question = get_object_or_404(Question,pk=question_id)
    if request.user == question.author:
        messages.error(request,'본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in question.down_voter.all():
        messages.error(request,'이미 비추천 하였습니다.')
    else:
        if request.user in question.up_voter.all():
           question.up_voter.remove(request.user)  # 추천 취소
        else:
           question.up_voter.add(request.user) 
    return redirect('board:detail',question_id=question.id)

@login_required(login_url='common:login')
def downvote_question(request,question_id):
    question = get_object_or_404(Question,pk=question_id)
    if request.user == question.author:
        messages.error(request,'본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in question.up_voter.all():
        messages.error(request,'이미 추천 하였습니다.')
    else:
        if request.user in question.down_voter.all():
           question.down_voter.remove(request.user)  # 추천 취소
        else:
           question.down_voter.add(request.user) 
    return redirect('board:detail',question_id=question.id)

# 댓글 추천 비추천 기능

@login_required(login_url='common:login')
def upvote_answer(request,answer_id):
    answer = get_object_or_404(Answer, pk= answer_id)
    if request.user == answer.author:
        messages.error(request,'본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in answer.up_voter.all():
        messages.error(request,'이미 비추천 하였습니다.')
    else:
        if request.user in answer.up_voter.all():
            answer.up_voter.remove(request.user)
        else:
            answer.up_voter.add(request.user)
    return redirect('board:detail',question_id = answer.question.id)

@login_required(login_url='common:login')
def downvote_answer(request,answer_id):
    answer = get_object_or_404(Answer, pk= answer_id)
    if request.user == answer.author:
        messages.error(request,'본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in answer.up_voter.all():
        messages.error(request,'이미 추천 하였습니다.')
    else:
        if request.user in answer.down_voter.all():
            answer.down_voter.remove(request.user)
        else:
            answer.down_voter.add(request.user)
    return redirect('board:detail',question_id = answer.question.id)