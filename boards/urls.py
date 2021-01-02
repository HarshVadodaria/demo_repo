from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from boards import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
	path('<int:pk>/', login_required(views.TopicListView.as_view()), name='board_topics'),
	# path('<int:pk>/new/',  login_required(views.new_topic), name='new_topic'),
	path('<int:pk>/new/',  login_required(views.NewTopicView.as_view()), name='new_topic'),
	path('<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/', login_required(views.PostUpdateView.as_view()), name='edit_post'),
	path('<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/delete/', login_required(views.PostDeleteView.as_view()), name='delete_post'),
	path('<int:pk>/topics/<int:topic_pk>/', login_required(views.PostListView.as_view()), name='topic_posts'),
	path('<int:pk>/topics/<int:topic_pk>/reply/', login_required(views.ReplyTopic.as_view()), name='reply_topic'),
	

]