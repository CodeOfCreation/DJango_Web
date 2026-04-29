from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from .models import Roadmap, Topic, Resource, UserProgress
from accounts.models import CareerGoal


def explore_roadmaps(request):
    """Explore all published roadmaps with filtering options"""
    career_goals = CareerGoal.objects.all()
    
    # Get filter parameters
    selected_goal = request.GET.get('career_goal')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')
    
    # Base queryset
    roadmaps = Roadmap.objects.filter(is_published=True).select_related('career_goal')
    
    # Apply filters
    if selected_goal:
        roadmaps = roadmaps.filter(career_goal__slug=selected_goal)
    if difficulty:
        roadmaps = roadmaps.filter(difficulty=difficulty)
    if search_query:
        roadmaps = roadmaps.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get user's active roadmap if authenticated
    user_active_roadmap = None
    if request.user.is_authenticated and request.user.profile.career_goal:
        user_active_roadmap = roadmaps.filter(
            career_goal=request.user.profile.career_goal
        ).first()
    
    context = {
        'roadmaps': roadmaps,
        'career_goals': career_goals,
        'selected_goal': selected_goal,
        'selected_difficulty': difficulty,
        'search_query': search_query,
        'user_active_roadmap': user_active_roadmap,
    }
    return render(request, 'roadmaps/explore.html', context)


def roadmap_detail(request, slug):
    """Detailed view of a roadmap with topics and resources"""
    roadmap = get_object_or_404(
        Roadmap.objects.select_related('career_goal', 'created_by'),
        slug=slug,
        is_published=True
    )
    
    # Get all topics with resources
    topics = Topic.objects.filter(roadmap=roadmap).prefetch_related('resources')
    
    # Get user progress if authenticated
    user_progress = {}
    if request.user.is_authenticated:
        progress_qs = UserProgress.objects.filter(
            user=request.user,
            topic__in=topics
        )
        user_progress = {p.topic_id: p for p in progress_qs}
    
    # Calculate progress stats
    total_topics = topics.count()
    completed_topics = sum(1 for t in topics if user_progress.get(t.id, {}).is_completed)
    progress_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0
    
    # Get next recommended topic
    next_topic = None
    for topic in topics:
        progress = user_progress.get(topic.id)
        if not progress or not progress.is_completed:
            next_topic = topic
            break
    
    # Budget filtering
    show_free_only = False
    if request.user.is_authenticated:
        show_free_only = request.user.profile.budget_mode == 'free_only'
    
    context = {
        'roadmap': roadmap,
        'topics': topics,
        'user_progress': user_progress,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'progress_percentage': progress_percentage,
        'next_topic': next_topic,
        'show_free_only': show_free_only,
    }
    return render(request, 'roadmaps/roadmap_detail.html', context)


@login_required
def create_roadmap(request):
    """Create a new roadmap (admin/creator only)"""
    if not request.user.is_staff and not request.user.profile.is_mentor:
        messages.error(request, 'You do not have permission to create roadmaps.')
        return redirect('explore_roadmaps')
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        career_goal_id = request.POST.get('career_goal')
        difficulty = request.POST.get('difficulty')
        estimated_duration = request.POST.get('estimated_duration')
        
        career_goal = get_object_or_404(CareerGoal, id=career_goal_id)
        
        roadmap = Roadmap.objects.create(
            title=title,
            description=description,
            career_goal=career_goal,
            difficulty=difficulty,
            estimated_duration=estimated_duration,
            created_by=request.user
        )
        
        messages.success(request, 'Roadmap created successfully!')
        return redirect('roadmap_detail', slug=roadmap.slug)
    
    context = {
        'career_goals': CareerGoal.objects.all(),
        'difficulty_choices': Roadmap.DIFFICULTY_CHOICES,
    }
    return render(request, 'roadmaps/create_roadmap.html', context)


@login_required
@require_POST
def mark_topic_complete(request, topic_id):
    """Toggle topic completion status"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        topic=topic,
        defaults={'is_completed': True}
    )
    
    if not created:
        progress.is_completed = not progress.is_completed
        if progress.is_completed:
            from django.utils import timezone
            progress.completed_at = timezone.now()
        else:
            progress.completed_at = None
        progress.save()
    
    # Calculate updated progress
    total_topics = Topic.objects.filter(roadmap=topic.roadmap).count()
    completed_count = UserProgress.objects.filter(
        user=request.user,
        topic__roadmap=topic.roadmap,
        is_completed=True
    ).count()
    percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0
    
    return JsonResponse({
        'success': True,
        'is_completed': progress.is_completed,
        'completed_count': completed_count,
        'total_topics': total_topics,
        'percentage': round(percentage, 1)
    })


@login_required
def my_progress(request):
    """View user's overall progress across all roadmaps"""
    progress_data = UserProgress.objects.filter(
        user=request.user
    ).select_related('topic__roadmap').order_by('-updated_at')
    
    # Group by roadmap
    roadmap_progress = {}
    for p in progress_data:
        roadmap = p.topic.roadmap
        if roadmap not in roadmap_progress:
            roadmap_progress[roadmap] = {
                'total': 0,
                'completed': 0,
                'topics': []
            }
        roadmap_progress[roadmap]['total'] += 1
        if p.is_completed:
            roadmap_progress[roadmap]['completed'] += 1
        roadmap_progress[roadmap]['topics'].append(p)
    
    context = {
        'roadmap_progress': roadmap_progress,
        'total_progress': progress_data.count(),
        'completed_count': progress_data.filter(is_completed=True).count(),
    }
    return render(request, 'roadmaps/my_progress.html', context)
