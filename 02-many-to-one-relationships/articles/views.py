from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# 지정된 HTTP method만 허용
from django.views.decorators.http import require_http_methods,require_POST
from .models import Article,Comment
from .forms import ArticleForm,CommentForm


# Create your views here.
def index(request):
    articles = Article.objects.all()
    context = {
        'articles': articles,
    }
    return render(request, 'articles/index.html', context)


def detail(request, pk):
    article = Article.objects.get(pk=pk)
    comment_form = CommentForm()
    comments = article.comment_set.all()
    context = {
        'article': article,
        'comment_form' : comment_form,
        'comments' : comments,
    }
    return render(request, 'articles/detail.html', context)


@login_required
# POST요청과 GET요청만 허용
# 아래와 같은 데코레이터가 없는 상황에서 PUT/PATH, DELETE 등의 메서드 등의 요청이 들어오게 되면?
# 로직에는 IF문으로 POST에 대한 조건 분기를 해놨는데 나머지는 HTML 반환 하는 형식으로 코드 작성
@require_http_methods(['POST','GET']) 
# 데코레이터를 통해서 POST와 GET요청만 허용하게 해둔 상태에서 다른 메서드로 요청이 온다면?
def create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            form.save()
            return redirect('articles:detail', article.pk)
    else:
        form = ArticleForm()
    context = {
        'form': form,
    }
    return render(request, 'articles/create.html', context)


@login_required
def update(request, pk):
    article = Article.objects.get(pk=pk)
    if article.user == request.user:
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return redirect('articles:detail', article.pk)
        else:
            form = ArticleForm(instance=article)
        context = {
            'article': article,
            'form': form,
        }
        return render(request, 'articles/update.html', context)
   
    return redirect('articles:detail', article.pk)


@login_required
@require_POST
def delete(request, pk):
    if request.user == article.user:
        article = Article.objects.get(pk=pk)
        article.delete()
        return redirect('articles:index')
    return redirect('articles:index')

def comment_create(request, pk):
    article = Article.objects.get(pk = pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        # 외래 키 데이터를 넣는 타이밍이 필요
        # 외래 키를 넣으러면 2가지 조건이 필요
        # 1. comment 인스턴스 필요
        # 2. save 메서드가 호출 되기 전이어야 함
        # 하지만 comment 인스턴스가 생성되는 조건은 save 메서드가 먼저 호출되어야함
        # django의 save 메서드는 인스턴스만 제공하고, 실제 저장은 잠시 대기하는 옵션을 제공
        # commit = False 옵션을 주면 저장은 하지 않고 인스턴스만 return
        comment = comment_form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
        return redirect('articles:detail', article.pk)
    context = {
        'article' : article,
        'comment_form' : comment_form,
    }
    return render(request , 'articles/detail.html' , context)

def comment_delete(request,article_pk,comment_pk):
    
    comment = Comment.objects.get(pk=comment_pk)
    # article의 pk를 가져오는 첫번 째 방법
    #article_pk = comment.article.pk
    # article의 pk를 가져오는 두번 째 방법
    # urls에서 pk를 2개 가져오가
    if request.user == comment.user:
        article = Article.objects.get(pk=article_pk)
        comment.delete()
        return redirect('articles:detail', article.pk)
    return redirect('articles:index')