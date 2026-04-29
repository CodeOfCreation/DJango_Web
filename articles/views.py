from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Article, Category
from .forms import ArticleForm



def article_list(request):
    """List all published articles with filtering"""
    categories = Category.objects.all()
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')
    
    # Base queryset
    articles = Article.objects.filter(is_published=True).select_related('author', 'category')
    
    # Apply filters
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    if difficulty:
        articles = articles.filter(difficulty=difficulty)
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Get featured articles
    featured_articles = articles.filter(featured=True)[:3]
    
    context = {
        'articles': articles,
        'categories': categories,
        'featured_articles': featured_articles,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'search_query': search_query,
    }
    return render(request, 'articles/list.html', context)



def article_detail(request, slug):
    """Show full article content"""
    article = get_object_or_404(
        Article.objects.select_related('author', 'category'),
        slug=slug,
        is_published=True
    )
    
    # Increment view count
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    # Get related articles
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'articles/detail.html', context)



@login_required
def article_create(request):
    """Create a new article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article published successfully!')
            return redirect('article_detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'difficulty_choices': Article.DIFFICULTY_CHOICES,
    }
    return render(request, 'articles/create.html', context)
