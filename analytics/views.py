from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from roadmaps.models import Roadmap, Topic, Resource, UserProgress
from communities.models import Community, StudyBuddyMatch
from articles.models import Article
from internships.models import Application as InternshipApplication
from jobs.models import JobApplication
from .utils import generate_progress_chart, generate_skill_heatmap, calculate_time_remaining


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with charts and stats"""
    user = request.user
    
    # Overall progress statistics
    total_topics = UserProgress.objects.filter(user=user).count()
    completed_topics = UserProgress.objects.filter(user=user, is_completed=True).count()
    completion_percentage = round((completed_topics / total_topics * 100), 1) if total_topics > 0 else 0
    remaining_topics = total_topics - completed_topics
    
    # Roadmap statistics
    active_roadmaps = Roadmap.objects.filter(
        topics__userprogress__user=user,
        topics__userprogress__is_completed=False
    ).distinct().count()
    
    # Community stats
    communities_joined = user.communities.count()
    study_buddies = StudyBuddyMatch.objects.filter(
        Q(user1=user) | Q(user2=user),
        status='accepted'
    ).count()
    
    # Content stats
    articles_written = Article.objects.filter(author=user).count()
    internships_applied = InternshipApplication.objects.filter(applicant=user).count()
    jobs_applied = JobApplication.objects.filter(applicant=user).count()
    
    # Generate charts
    progress_chart = generate_progress_chart(user)
    skill_heatmap = generate_skill_heatmap(user)
    
    # Time estimation
    time_data = calculate_time_remaining(user)
    
    context = {
        # Progress stats
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'remaining_topics': remaining_topics,
        'completion_percentage': completion_percentage,
        'active_roadmaps': active_roadmaps,
        
        # Community stats
        'communities_joined': communities_joined,
        'study_buddies': study_buddies,
        
        # Content stats
        'articles_written': articles_written,
        'internships_applied': internships_applied,
        'jobs_applied': jobs_applied,
        
        # Charts
        'progress_chart': progress_chart,
        'skill_heatmap': skill_heatmap,
        
        # Time
        'time_remaining': time_data,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def progress_data_api(request):
    """API endpoint for progress data (JSON) for dynamic chart updates"""
    user = request.user
    
    # Get progress by roadmap
    roadmaps = Roadmap.objects.filter(
        topics__userprogress__user=user
    ).distinct()
    
    data = []
    for roadmap in roadmaps:
        topics = Topic.objects.filter(roadmap=roadmap)
        total = topics.count()
        completed = UserProgress.objects.filter(
            user=user,
            topic__in=topics,
            is_completed=True
        ).count()
        
        data.append({
            'roadmap': roadmap.title,
            'total': total,
            'completed': completed,
            'remaining': total - completed,
            'percentage': round((completed / total * 100), 1) if total > 0 else 0,
        })
    
    return JsonResponse({'roadmaps': data})


@login_required
def skill_data_api(request):
    """API endpoint for skill domain data (JSON)"""
    user = request.user
    
    # Get progress grouped by domain
    progress_data = UserProgress.objects.filter(user=user).select_related('topic')
    
    domain_stats = {}
    for progress in progress_data:
        domain = progress.topic.domain
        if domain not in domain_stats:
            domain_stats[domain] = {'completed': 0, 'total': 0}
        domain_stats[domain]['total'] += 1
        if progress.is_completed:
            domain_stats[domain]['completed'] += 1
    
    # Calculate percentages
    data = []
    for domain, stats in sorted(domain_stats.items()):
        pct = round((stats['completed'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
        data.append({
            'domain': domain,
            'completed': stats['completed'],
            'total': stats['total'],
            'percentage': pct,
        })
    
    return JsonResponse({'domains': data})


@login_required
def overall_stats_api(request):
    """API endpoint for overall dashboard statistics"""
    user = request.user
    
    stats = {
        'total_topics': UserProgress.objects.filter(user=user).count(),
        'completed_topics': UserProgress.objects.filter(user=user, is_completed=True).count(),
        'communities': user.communities.count(),
        'study_buddies': StudyBuddyMatch.objects.filter(
            Q(user1=user) | Q(user2=user),
            status='accepted'
        ).count(),
        'articles': Article.objects.filter(author=user).count(),
        'internship_applications': InternshipApplication.objects.filter(applicant=user).count(),
        'job_applications': JobApplication.objects.filter(applicant=user).count(),
    }
    
    # Calculate completion percentage
    total = stats['total_topics']
    completed = stats['completed_topics']
    stats['completion_percentage'] = round((completed / total * 100), 1) if total > 0 else 0
    
    return JsonResponse(stats)
