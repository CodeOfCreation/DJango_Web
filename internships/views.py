from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Internship, Application
from .forms import InternshipForm, ApplicationForm



def internship_list(request):
    """List all active internships with filtering"""
    # Get filter parameters
    internship_type = request.GET.get('type')
    duration = request.GET.get('duration')
    search_query = request.GET.get('q')
    
    # Base queryset - only active internships that haven't passed deadline
    internships = Internship.objects.filter(
        is_active=True,
        application_deadline__gte=timezone.now()
    )
    
    # Apply filters
    if internship_type:
        internships = internships.filter(internship_type=internship_type)
    if duration:
        internships = internships.filter(duration=duration)
    if search_query:
        internships = internships.filter(
            Q(title__icontains=search_query) | 
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    context = {
        'internships': internships,
        'selected_type': internship_type,
        'selected_duration': duration,
        'search_query': search_query,
        'type_choices': Internship.TYPE_CHOICES,
        'duration_choices': Internship.DURATION_CHOICES,
    }
    return render(request, 'internships/list.html', context)



def internship_detail(request, slug):
    """Show full internship details"""
    internship = get_object_or_404(
        Internship,
        slug=slug,
        is_active=True
    )
    
    # Check if user has already applied
    has_applied = False
    user_application = None
    if request.user.is_authenticated:
        user_application = Application.objects.filter(
            internship=internship,
            applicant=request.user
        ).first()
        has_applied = user_application is not None
    
    # Get application count
    applications_count = internship.applications_count
    
    context = {
        'internship': internship,
        'has_applied': has_applied,
        'user_application': user_application,
        'applications_count': applications_count,
    }
    return render(request, 'internships/detail.html', context)



@login_required
def apply_internship(request, slug):
    """Apply for an internship"""
    internship = get_object_or_404(Internship, slug=slug, is_active=True)
    
    # Check if already applied
    existing = Application.objects.filter(
        internship=internship,
        applicant=request.user
    ).first()
    
    if existing:
        messages.warning(request, 'You have already applied for this internship.')
        return redirect('internship_detail', slug=slug)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('internship_detail', slug=slug)
    else:
        form = ApplicationForm()
    
    return render(request, 'internships/apply.html', {'internship': internship, 'form': form})



@login_required
def post_internship(request):
    """Post a new internship (for mentors and staff)"""
    if not request.user.is_staff and not request.user.profile.is_mentor:
        messages.error(request, 'You do not have permission to post internships.')
        return redirect('internship_list')
    
    if request.method == 'POST':
        form = InternshipForm(request.POST, request.FILES)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.posted_by = request.user
            internship.save()
            messages.success(request, 'Internship posted successfully!')
            return redirect('internship_detail', slug=internship.slug)
    else:
        form = InternshipForm()
    
    context = {
        'form': form,
        'type_choices': Internship.TYPE_CHOICES,
        'duration_choices': Internship.DURATION_CHOICES,
    }
    return render(request, 'internships/post.html', context)



@login_required
def my_applications(request):
    """View user's internship applications"""
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('internship').order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'internships/my_applications.html', context)
