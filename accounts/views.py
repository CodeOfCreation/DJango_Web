from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from .forms import CustomUserCreationForm, UserProfileForm, CareerGoalSelectionForm
from .models import UserProfile, CareerGoal


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to NEXTSTEP.')
            return redirect('career_goal_select')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')



@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    from roadmaps.models import UserProgress, Roadmap
    from articles.models import Article
    from communities.models import Community
    
    user = request.user
    profile = user.profile
    
    # Get active roadmap progress
    active_progress = UserProgress.objects.filter(user=user).select_related('topic__roadmap')
    completed_count = active_progress.filter(is_completed=True).count()
    total_count = active_progress.count()
    completion_percentage = profile.completion_percentage
    
    # Get current active roadmap
    active_roadmap = None
    if profile.career_goal:
        active_roadmap = Roadmap.objects.filter(
            career_goal=profile.career_goal,
            is_published=True
        ).first()
    
    # Get next recommended topic
    next_topic = None
    if active_roadmap:
        next_topic = active_progress.filter(
            is_completed=False
        ).select_related('topic').first()
    
    # Get recent articles
    recent_articles = Article.objects.filter(
        is_published=True
    ).order_by('-created_at')[:3]
    
    # Get user's communities
    user_communities = Community.objects.filter(
        members=user
    )[:3]
    
    # Get skill breakdown for heatmap
    skill_data = {}
    if active_roadmap:
        from roadmaps.models import Topic
        topics = Topic.objects.filter(roadmap=active_roadmap)
        for topic in topics:
            domain = topic.domain or 'General'
            if domain not in skill_data:
                skill_data[domain] = {'total': 0, 'completed': 0}
            skill_data[domain]['total'] += 1
            progress = UserProgress.objects.filter(user=user, topic=topic, is_completed=True).first()
            if progress:
                skill_data[domain]['completed'] += 1
    
    context = {
        'profile': profile,
        'completion_percentage': completion_percentage,
        'completed_count': completed_count,
        'total_count': total_count,
        'active_roadmap': active_roadmap,
        'next_topic': next_topic,
        'recent_articles': recent_articles,
        'user_communities': user_communities,
        'skill_data': skill_data,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def career_goal_select_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = CareerGoalSelectionForm(request.POST)
        if form.is_valid():
            profile.career_goal = form.cleaned_data['career_goal']
            profile.budget_mode = form.cleaned_data['budget_mode']
            profile.learning_style = form.cleaned_data['learning_style']
            profile.save()
            messages.success(request, 'Career goal set! Let\'s start your learning journey.')
            return redirect('dashboard')
    else:
        # Pre-fill if already selected
        initial = {}
        if profile.career_goal:
            initial['career_goal'] = profile.career_goal
        if profile.budget_mode:
            initial['budget_mode'] = profile.budget_mode
        if profile.learning_style:
            initial['learning_style'] = profile.learning_style
        form = CareerGoalSelectionForm(initial=initial)
    
    goals = CareerGoal.objects.all()
    return render(request, 'accounts/career_goal.html', {

        'form': form,
        'goals': goals
    })
