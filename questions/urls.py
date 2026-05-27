from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag>/', views.tag, name='tag'),
    path('question/<int:id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('ajax/question/vote/', views.question_vote, name='question_vote'),
    path('ajax/answer/vote/', views.answer_vote, name='answer_vote'),
    path('ajax/answer/correct/', views.mark_correct, name='mark_correct'),
]