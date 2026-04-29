from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm



def job_list(request):
    """List all active jobs with advanced filtering"""
    # Get filter parameters
    job_type = request.GET.get('type')
    experience = request.GET.get('experience')
    location = request.GET.get('location')
    search_query = request.GET.get('q')
    
    # Base queryset - only active jobs that haven't passed deadline
    jobs = Job.objects.filter(
        is_active=True,
        application_deadline__gte=timezone.now()
    )
    
    # Apply filters
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience:
        jobs = jobs.filter(experience_level=experience)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) | 
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(skills_required__icontains=search_query)
        )
    
    context = {
        'jobs': jobs,
        'selected_type': job_type,
        'selected_experience': experience,
        'location_filter': location,
        'search_query': search_query,
        'type_choices': Job.TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    }
    return render(request, 'jobs/list.html', context)



def job_detail(request, slug):
    """Show full job details"""
    job = get_object_or_404(
        Job,
        slug=slug,
        is_active=True
    )
    
    # Check if user has already applied
    has_applied = False
    user_application = None
    if request.user.is_authenticated:
        user_application = JobApplication.objects.filter(
            job=job,
            applicant=request.user
        ).first()
        has_applied = user_application is not None
    
    # Get similar jobs
    similar_jobs = Job.objects.filter(
        is_active=True,
        job_type=job.job_type,
        experience_level=job.experience_level
    ).exclude(id=job.id)[:3]
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'user_application': user_application,
        'similar_jobs': similar_jobs,
    }
    return render(request, 'jobs/detail.html', context)



@login_required
def apply_job(request, slug):
    """Apply for a job"""
    job = get_object_or_404(Job, slug=slug, is_active=True)
    
    # Check if already applied
    existing = JobApplication.objects.filter(
        job=job,
        applicant=request.user
    ).first()
    
    if existing:
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', slug=slug)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Job application submitted successfully!')
            return redirect('job_detail', slug=slug)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply.html', {'job': job, 'form': form})



@login_required
def post_job(request):
    """Post a new job (for employers and staff)"""
    if not request.user.is_staff and not request.user.profile.is_employer:
        messages.error(request, 'You do not have permission to post jobs.')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', slug=job.slug)
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'type_choices': Job.TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    }
    return render(request, 'jobs/post.html', context)



@login_required
def my_job_applications(request):
    """View user's job applications"""
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)
