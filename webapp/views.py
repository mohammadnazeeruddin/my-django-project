from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
#from django.http import Http404
from .models import Board,Topic,Post
from .forms import NewTopicForm,PostForm
from django.db.models import Count
from django.views.generic import UpdateView
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import viewsets
from webapp.serilaizer import EmployeeSerializer 

class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serilaizer_class = EmployeeSerializer


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'webapp/home.html'
#def home(request):
	#H_boards=Board.objects.all()
	#return render(request,'webapp/home.html',{"H_boards":H_boards})

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'webapp/topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
        return queryset

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'webapp/topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewd_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key,False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key]=True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

#def boards_topics(request,pk):
	# we are importing 'get_object_or_404'
	#T_boards = get_object_or_404(Board,pk=pk)
	#queryset = T_boards.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
	#page =request.GET.get('page',1)
	#paginator = Paginator(queryset, 20)
	#try:
		#topics = paginator.page(page)
	#except PageNotAnInteger:
		#topics = paginator.page(1)
	#except EmptyPage:
		#topics = paginator.page(paginator.num_pages)
	#return render(request,'webapp/topics.html',{"T_boards":T_boards,"topics":topics})

	# we can write code like this also
	#try:
	#	boards = Board.objects.get(pk=pk)
	#except Board.DoesNotExist:
	#	raise Http404 
	#return render(request,'webapp/topics.html',{"boards":boards})
#def new_topics(request,pk):
#	N_boards = get_object_or_404(Board, pk=pk)
#	if request.method == 'POST' :

#		subject= request.POST['subject']
#		message = request.POST['message']
#		user1= User.objects.first()

#		topic1= Topic.objects.create(
 #           subject=subject,
  #          board=N_boards,
   #         starter=user1
    #    )
		#post = Post.objects.create(
         #   message=message,
          #  topic=topic1,
           # created_by=user1
        #)
		#return redirect('boards_topics', pk=N_boards.pk)
	#return render(request,'webapp/new_topic.html',{"N_boards":N_boards})

@login_required
def new_topics(request,pk):
	N_boards = get_object_or_404(Board,pk=pk)
	user1 = User.objects.first()
	if request.method == 'POST':
		form = NewTopicForm(request.POST)#just imagine its a html form 
         #in side NewTopicForm class we used Topic model through Meta class reference 
		if form.is_valid():
			topic = form.save(commit=False)# Topic Model 
			topic.board = N_boards 
			#topic.board = N_boards;'board' is from Topic Model 
			topic.starter=request.user # here we are requesting present new topic created user
            # if we used like this topic.starter = user1 we get admin user name.
			topic.save()

			post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
			return redirect('boards_topics',pk=N_boards.pk)
			return redirect('topic_posts', pk=pk, topic_pk=topic.pk)   # TODO: redirect to the created topic page
	else :
		form = NewTopicForm()
	return render(request,'webapp/new_topic.html',{"N_boards":N_boards,"form":form})

def topic_posts(request, pk,topic_pk):
    topic =get_object_or_404(Topic,board__pk = pk,pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'webapp/topic_posts.html', {'topic': topic})
 	

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_update = timezone.now()
            topic.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'webapp/reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'webapp/edit_post.html'
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
