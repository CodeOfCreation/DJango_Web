import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from django.db.models import Count, Q


def generate_progress_chart(user):
    """
    Generate a progress bar chart showing % completed vs % remaining
    Returns a base64 encoded image string
    """
    from roadmaps.models import UserProgress, Topic
    
    # Get all topics the user has progress on
    user_progress = UserProgress.objects.filter(user=user).select_related('topic__roadmap')
    
    # Group by roadmap
    roadmap_data = {}
    for progress in user_progress:
        roadmap_title = progress.topic.roadmap.title if progress.topic.roadmap else 'General'
        if roadmap_title not in roadmap_data:
            roadmap_data[roadmap_title] = {'completed': 0, 'total': 0}
        roadmap_data[roadmap_title]['total'] += 1
        if progress.is_completed:
            roadmap_data[roadmap_title]['completed'] += 1
    
    if not roadmap_data:
        return None
    
    # Prepare data for chart
    roadmaps = list(roadmap_data.keys())
    completed = [roadmap_data[r]['completed'] for r in roadmaps]
    remaining = [roadmap_data[r]['total'] - roadmap_data[r]['completed'] for r in roadmaps]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(roadmaps))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, completed, width, label='Completed', color='#28a745')
    bars2 = ax.bar(x + width/2, remaining, width, label='Remaining', color='#6c757d')
    
    ax.set_xlabel('Career Roadmaps')
    ax.set_ylabel('Number of Topics')
    ax.set_title('Learning Progress by Roadmap')
    ax.set_xticks(x)
    ax.set_xticklabels(roadmaps, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    
    # Save to buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    
    return image_base64


def generate_skill_heatmap(user):
    """
    Generate a skill heatmap showing mastered vs pending domains
    Returns a base64 encoded image string
    """
    from roadmaps.models import UserProgress, Topic
    
    # Get all user progress with topic domains
    user_progress = UserProgress.objects.filter(user=user).select_related('topic')
    
    # Group by domain
    domain_data = {}
    for progress in user_progress:
        domain = progress.topic.domain
        if domain not in domain_data:
            domain_data[domain] = {'completed': 0, 'total': 0}
        domain_data[domain]['total'] += 1
        if progress.is_completed:
            domain_data[domain]['completed'] += 1
    
    if not domain_data:
        return None
    
    # Calculate completion percentage for each domain
    domains = sorted(domain_data.keys())
    completion_pct = []
    for domain in domains:
        total = domain_data[domain]['total']
        completed = domain_data[domain]['completed']
        pct = (completed / total * 100) if total > 0 else 0
        completion_pct.append(pct)
    
    # Create heatmap data (1 row, N columns)
    data = np.array([completion_pct])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Create heatmap
    sns.heatmap(
        data,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        vmin=0,
        vmax=100,
        xticklabels=domains,
        yticklabels=['Completion %'],
        cbar_kws={'label': 'Completion Percentage'},
        ax=ax
    )
    
    ax.set_title('Skill Domain Completion Heatmap')
    plt.tight_layout()
    
    # Save to buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    
    return image_base64


def calculate_time_remaining(user):
    """
    Calculate total estimated time remaining based on incomplete topics
    Returns hours and formatted string
    """
    from roadmaps.models import UserProgress, Topic
    
    # Get incomplete topics
    incomplete_progress = UserProgress.objects.filter(user=user, is_completed=False).select_related('topic')
    
    # Default: assume 2 hours per topic if no estimate
    total_hours = sum(
        (progress.topic.estimated_hours or 2) 
        for progress in incomplete_progress
    )
    
    # Convert to weeks (assuming 10 hours/week study time)
    weeks = total_hours / 10 if total_hours > 0 else 0
    
    return {
        'total_hours': total_hours,
        'weeks': round(weeks, 1),
        'formatted': f"{int(total_hours)} hours (~{round(weeks, 1)} weeks at 10 hrs/week)"
    }
