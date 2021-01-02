from django import forms
from .models import Topic, Post
from django.core.exceptions import ValidationError


class NewTopicForm(forms.ModelForm):
	# message = forms.CharField(
	# 	widget=forms.Textarea(
	# 		attrs={'rows': 7, 'placeholder': 'What is on your mind?'}
	# 	),
	# 	max_length=4000,
	# 	help_text='The max length of the text is 4000.'
	# )

	message = forms.CharField(widget=forms.Textarea())
	# import pdb; pdb.set_trace()
	def clean_subject(self):
		sub = self.cleaned_data['subject']
		print(sub)

		if sub=='manan':
			# import pdb; pdb.set_trace()
			# raise forms.ValidationError('enter other subject...')
			# raise ValidationError('enter other subject...')
			raise forms.ValidationError("Headline must be more than 5 characters.")
		return sub

	class Meta:
		model = Topic
		fields = ['subject', 'message']

class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['message', ]