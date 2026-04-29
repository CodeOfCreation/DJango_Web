from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Community, Membership, StudyBuddyMatch, Discussion
from .forms import CommunityForm, DiscussionForm
from roadmaps.models import Roadmap, Topic, UserProgress



def community_list(request):
    """List all communities with filtering"""
    category = request.GET.get('category')
    search_query = request.GET.get('q')
    
    communities = Community.objects.filter(is_public=True)
    
    if category:
        communities = communities.filter(category=category)
    if search_query:
        communities = communities.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get user's communities if authenticated
    my_communities = []
    if request.user.is_authenticated:
        my_communities = request.user.communities.all()
    
    context = {
        'communities': communities,
        'my_communities': my_communities,
        'selected_category': category,
        'search_query': search_query,
        'category_choices': Community.CATEGORY_CHOICES,
    }
    return render(request, 'communities/list.html', context)



def community_detail(request, slug):
    """Show community details and discussions"""
    community = get_object_or_404(
        Community.objects.prefetch_related('discussions__author'),
        slug=slug
    )
    
    # Check if user is a member
    is_member = False
    user_role = None
    if request.user.is_authenticated:
        membership = Membership.objects.filter(
            user=request.user,
            community=community
        ).first()
        is_member = membership is not None
        if membership:
            user_role = membership.role
    
    # Get discussions
    discussions = community.discussions.select_related('author').all()
    
    # Get members
    members = community.members.all()[:20]
    
    context = {
        'community': community,
        'is_member': is_member,
        'user_role': user_role,
        'discussions': discussions,
        'members': members,
    }
    return render(request, 'communities/detail.html', context)



@login_required
def join_community(request, slug):
    """Join a community"""
    community = get_object_or_404(Community, slug=slug)
    
    if community.is_member(request.user):
        messages.info(request, 'You are already a member of this community.')
        return redirect('community_detail', slug=slug)
    
    Membership.objects.create(
        user=request.user,
        community=community,
        role='member'
    )
    
    messages.success(request, f'You have joined {community.name}!')
    return redirect('community_detail', slug=slug)


@login_required
def leave_community(request, slug):
    """Leave a community"""
    community = get_object_or_404(Community, slug=slug)
    
    membership = Membership.objects.filter(
        user=request.user,
        community=community
    ).first()
    
    if membership:
        membership.delete()
        messages.success(request, f'You have left {community.name}.')
    else:
        messages.info(request, 'You are not a member of this community.')
    
    return redirect('community_detail', slug=slug)


@login_required
def create_community(request):
    """Create a new community"""
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            
            # Add creator as admin
            Membership.objects.create(
                user=request.user,
                community=community,
                role='admin'
            )
            
            messages.success(request, 'Community created successfully!')
            return redirect('community_detail', slug=community.slug)
    else:
        form = CommunityForm()
    
    # Get available roadmaps for study groups
    roadmaps = Roadmap.objects.all()
    
    context = {
        'form': form,
        'category_choices': Community.CATEGORY_CHOICES,
        'roadmaps': roadmaps,
    }
    return render(request, 'communities/create.html', context)



@login_required
def find_study_buddies(request):
    """Find potential study buddies based on same roadmap and progress"""
    roadmap_id = request.GET.get('roadmap')
    
    # Get user's active roadmaps
    user_progress = UserProgress.objects.filter(
        user=request.user,
        is_completed=False
    ).select_related('topic__roadmap')
    
    # Get unique roadmaps the user is pursuing
    active_roadmap_ids = set()
    for progress in user_progress:
        if progress.topic.roadmap:
            active_roadmap_ids.add(progress.topic.roadmap.id)
    
    buddies = []
    selected_roadmap = None
    
    if roadmap_id:
        selected_roadmap = get_object_or_404(Roadmap, id=roadmap_id)
        
        # Find users with same active roadmap, excluding current user and existing buddies
        existing_buddy_ids = set()
        existing_matches = StudyBuddyMatch.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).values_list('user1', 'user2')
        
        for match in existing_matches:
            existing_buddy_ids.update(match)
        
        # Find potential buddies - users with progress in same roadmap
        potential_buddy_progress = UserProgress.objects.filter(
            topic__roadmap=selected_roadmap,
            is_completed=False
        ).exclude(user=request.user).select_related('user', 'topic')
        
        seen_users = set()
        for progress in potential_buddy_progress:
            if progress.user.id not in seen_users and progress.user.id not in existing_buddy_ids:
                seen_users.add(progress.user.id)
                buddies.append({
                    'user': progress.user,
                    'current_topic': progress.topic,
                })
    
    # Get roadmaps for filter dropdown
    roadmaps = Roadmap.objects.filter(id__in=active_roadmap_ids)
    
    context = {
        'buddies': buddies,
        'roadmaps': roadmaps,
        'selected_roadmap': selected_roadmap,
    }
    return render(request, 'communities/find_buddies.html', context)



@login_required
def send_buddy_request(request, user_id):
    """Send a study buddy request"""
    from django.contrib.auth.models import User
    
    buddy = get_object_or_404(User, id=user_id)
    roadmap_id = request.POST.get('roadmap')
    topic_id = request.POST.get('topic')
    message = request.POST.get('message', '')
    
    roadmap = get_object_or_404(Roadmap, id=roadmap_id) if roadmap_id else None
    topic = get_object_or_404(Topic, id=topic_id) if topic_id else None
    
    # Check if match already exists
    existing = StudyBuddyMatch.objects.filter(
        user1=request.user,
        user2=buddy,
        roadmap=roadmap
    ).first() or StudyBuddyMatch.objects.filter(
        user1=buddy,
        user2=request.user,
        roadmap=roadmap
    ).first()
    
    if existing:
        messages.info(request, 'A study buddy request already exists with this user.')
        return redirect('find_study_buddies')
    
    StudyBuddyMatch.objects.create(
        user1=request.user,
        user2=buddy,
        roadmap=roadmap,
        current_topic=topic,
        message=message
    )
    
    messages.success(request, f'Study buddy request sent to {buddy.username}!')
    return redirect('find_study_buddies')


@login_required
def respond_buddy_request(request, match_id):
    """Accept or reject a study buddy request"""
    match = get_object_or_404(
        StudyBuddyMatch,
        id=match_id,
        user2=request.user,
        status='pending'
    )
    
    action = request.POST.get('action')
    
    if action == 'accept':
        match.status = 'accepted'
        messages.success(request, f'You are now study buddies with {match.user1.username}!')
    elif action == 'reject':
        match.status = 'rejected'
        messages.info(request, f'Study buddy request from {match.user1.username} declined.')
    
    match.save()
    return redirect('dashboard')


@login_required
def create_discussion(request, slug):
    """Create a new discussion in a community"""
    community = get_object_or_404(Community, slug=slug)
    
    # Check if user is a member
    if not community.is_member(request.user):
        messages.error(request, 'You must be a member to post discussions.')
        return redirect('community_detail', slug=slug)
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.community = community
            discussion.author = request.user
            discussion.save()
            messages.success(request, 'Discussion posted successfully!')
            return redirect('community_detail', slug=slug)
    else:
        form = DiscussionForm()
    
    return render(request, 'communities/create_discussion.html', {'community': community, 'form': form})
