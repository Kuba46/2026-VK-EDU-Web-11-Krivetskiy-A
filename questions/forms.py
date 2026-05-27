import re

from django import forms

from .models import Answer, Question, Tag


class QuestionCreateForm(forms.ModelForm):
    tags = forms.CharField(
        label='Tags',
        help_text='Enter tags separated by spaces or commas.',
        max_length=255,
    )

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags')

    def clean_tags(self):
        raw_tags = self.cleaned_data['tags']
        tags = [item.strip().lower() for item in re.split(r'[,\s]+', raw_tags) if item.strip()]
        if not tags:
            raise forms.ValidationError('Please provide at least one tag.')
        if len(tags) > 10:
            raise forms.ValidationError('Please provide no more than 10 tags.')
        return list(dict.fromkeys(tags))

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author
        if commit:
            question.save()
            tag_objects = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in self.cleaned_data['tags']]
            question.tags.set(tag_objects)
        return question


class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)

    def save(self, author, question, commit=True):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        if commit:
            answer.save()
        return answer


class QuestionVoteForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    value = forms.ChoiceField(choices=(('1', 'like'), ('-1', 'dislike')))


class AnswerVoteForm(forms.Form):
    answer_id = forms.IntegerField(min_value=1)
    value = forms.ChoiceField(choices=(('1', 'like'), ('-1', 'dislike')))


class CorrectAnswerForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    answer_id = forms.IntegerField(min_value=1)
