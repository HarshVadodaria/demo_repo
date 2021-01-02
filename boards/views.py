from django.shortcuts import redirect
from django.views.generic import UpdateView, DeleteView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.views.generic import View, ListView, CreateView
from .forms import NewTopicForm, PostForm
from django.urls import reverse_lazy
from .models import Board, Post, Topic
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

def home(request):
	boards = Board.objects.all()
	return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
	board = get_object_or_404(Board, pk=pk)
	queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
	page = request.GET.get('page', 1)

	paginator = Paginator(queryset, 20)

	try:
		topics = paginator.page(page)
	except PageNotAnInteger:
		# fallback to the first page
		topics = paginator.page(1)
	except EmptyPage:
		# probably the user tried to add a page number
		# in the url, so we fallback to the last page
		topics = paginator.page(paginator.num_pages)

	return render(request, 'topics.html', {'board': board, 'topics': topics})


class NewTopicView(CreateView):
	model=Topic
	template_name='new_topic.html'
	form_class = NewTopicForm

	def get(self, request, pk, *args, **kwargs):
		board = Board.objects.get(pk=pk)
		context = {'form': NewTopicForm(),'board':board}
		return render(request, 'new_topic.html', context)

	def post(self, request,pk, *args, **kwargs):
		form =NewTopicForm(request.POST)
		if form.is_valid():
			board=Board.objects.get(pk=self.kwargs['pk'])
			topic = form.save(commit=False)
			topic.board=board
			topic.starter=request.user
			topic.save()
			Post.objects.create(message=form.cleaned_data.get('message'), topic=topic, created_by=request.user)
			return HttpResponseRedirect(reverse('board_topics', kwargs={'pk': board.id })) 



class ReplyTopic(CreateView):

	def get(self, request, pk, topic_pk, *args, **kwargs):
		topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
		context = {'form': PostForm(), 'topic':topic}
		return render(request, 'reply_topic.html', context)


	def post(self, request, pk, topic_pk, *args, **kwargs):
		form = PostForm(request.POST)
		if form.is_valid():
			topic = Topic.objects.get(pk=self.kwargs['topic_pk'])
			post = form.save(commit=False)
			post.topic = topic
			post.created_by = request.user
			post.save()
			topic.last_updated = timezone.now()
			topic.save()
			topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
			topic_post_url = '{url}?page={page}#{id}'.format(url=topic_url, id=post.pk, page=topic.get_page_count())
			return redirect(topic_post_url)
		

	
def topic_posts(request, pk, topic_pk):
	topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
	topic.views += 1
	topic.save()
	return render(request, 'topic_posts.html', {'topic': topic})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
	model = Post
	fields = ('message', )
	template_name = 'edit_post.html'
	pk_url_kwarg = 'post_pk'
	context_object_name = 'post'

	def get_queryset(self):
		queryset = super().get_queryset()
		return queryset.filter(created_by=self.request.user)

	def form_valid(self, form):
		post = form.save(commit=False)
		post.updated_by = self.request.user
		post.updated_at = timezone.now()
		post.save()
		return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class BoardListView(ListView):
	model = Board
	context_object_name = 'boards'
	template_name = 'home.html'


# def board_topics(request, pk):
#     board = get_object_or_404(Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)

#     paginator = Paginator(queryset, 20)

#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         # fallback to the first page
#         topics = paginator.page(1)
#     except EmptyPage:
#         # probably the user tried to add a page number
#         # in the url, so we fallback to the last page
#         topics = paginator.page(paginator.num_pages)

#     return render(request, 'topics.html', {'board': board, 'topics': topics})

class TopicListView(ListView):
	model = Topic
	context_object_name = 'topics'
	template_name = 'topics.html'
	paginate_by = 20

	def get_context_data(self, **kwargs):
		kwargs['board'] = self.board
		return super().get_context_data(**kwargs)

	def get_queryset(self):
		self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
		queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
		return queryset

class PostListView(ListView):
	model = Post
	context_object_name = 'posts'
	template_name = 'topic_posts.html'
	paginate_by = 20

	def get_context_data(self, **kwargs):

		session_key = 'viewed_topic_{}'.format(self.topic.pk)  
		if not self.request.session.get(session_key, False):
			self.topic.views += 1
			self.topic.save()
			self.request.session[session_key] = True           

		kwargs['topic'] = self.topic
		return super().get_context_data(**kwargs)

	def get_queryset(self):
		self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
		queryset = self.topic.posts.order_by('created_at')
		return queryset

class PostDeleteView(DeleteView):
	# success_url = reverse_lazy('topic_posts')
	context_object_name = 'posts'
	model = Post, Topic

	def get(self, request, pk, topic_pk, *args, **kwargs):
		board=Board.objects.get(id=pk)
		topic=Topic.objects.get(id=topic_pk)
		topic.delete()
		return HttpResponseRedirect(reverse('board_topics', kwargs={'pk' : pk}	))


