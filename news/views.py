from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, resolve
from django.views import View
from django.views.generic import ListView, DeleteView, CreateView, UpdateView, DetailView, FormView, TemplateView
from django.contrib.auth.models import Group

from NewsPaper.settings import DEFAULT_FROM_EMAIL
from .models import Post, Appointment, Category
from .filters import PostFilter
from .forms import PostForm, RegisterForm, LoginForm


class PostList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    ordering = ['-rating']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['choices'] = Post.CATEGORY_CHOICES
        context['form'] = PostForm()
        context['is_not_author'] = not self.request.user.groups.filter(name='author').exists()
        return context

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='author')
    if not request.user.groups.filter(name='author').exists():
        premium_group.user_set.add(user)
    return redirect('/posts/')


class PostDetail(DetailView):
    template_name = 'news/post.html'
    queryset = Post.objects.all()


class PostCreate(CreateView):
    template_name = 'news/post_create.html'
    form_class = PostForm


class PostUpdate(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    template_name = 'news/post_create.html'
    form_class = PostForm
    permission_required = ('news.change _post',)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news:posts')


class PostCategory(ListView):
    model = Post
    template_name = 'news/category.html'
    context_object_name = 'category_posts'
    ordering = ['-dateCreation']
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        c = Category.objects.get(id=self.id)
        # queryset = Post.objects.filter(categoryType=c)
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])  # Получить выбранную категорию
        queryset = self.category.post_set.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category = Category.objects.get(id=self.id)
        subscribed = category.subscribers.filter(email=user.email)
        context['category'] = self.category
        return context


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'news/register.html'
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get(name='basic')
        user.groups.add(group)
        user.save()
        return super().form_valid(form)


class LoginView(FormView):
    model = User
    form_class = LoginForm
    template_name = 'news/login.html'
    success_url = '/posts/'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'news/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'news/posts.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        send_mail(
            subject=f'{appointment.client_name}',

            message=appointment.message,
            from_email='',
            recipient_list=[]
        )

        return redirect('news:posts')


@login_required
def subscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        email = user.email
        html = render_to_string(
            'account/email/subscribed.html',
            {
                'category': category,
                'user': user
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'{category} subscription',
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email,],
        )
        msg.attach_alternative(html, 'text/html')

        try:
            msg.send()
        except Exception as e:
            print(e)

        return redirect('news:posts')
    return redirect('news:posts')


@login_required
def unsubscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return redirect('news:posts')
