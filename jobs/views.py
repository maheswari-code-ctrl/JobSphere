

# Create your views here.

# from django.shortcuts import render

# def home(request):
#     return render(request, 'jobs/home.html')


# from django.shortcuts import render


# def home(request):
#     jobs = [
#         {
#             "title": "Python Developer",
#             "company": "ABC Technologies",
#             "location": "Hyderabad",
#             "type": "Full Time",
#             "salary": "3-5 LPA"
#         },
#         {
#             "title": "Frontend Developer",
#             "company": "XYZ Solutions",
#             "location": "Bangalore",
#             "type": "Full Time",
#             "salary": "3-4 LPA"
#         },
#         {
#             "title": "Django Developer",
#             "company": "Tech India",
#             "location": "Hyderabad",
#             "type": "Internship",
#             "salary": "15,000/month"
#         },
#         {
#             "title": "Junior Web Developer",
#             "company": "Digital Solutions",
#             "location": "Chennai",
#             "type": "Full Time",
#             "salary": "3-4 LPA"
#         }
#     ]

#     query = request.GET.get("q", "").strip()

#     if query:
#         jobs = [
#             job for job in jobs
#             if query.lower() in job["title"].lower()
#             or query.lower() in job["location"].lower()
#             or query.lower() in job["company"].lower()
#         ]

#     return render(
#         request,
#         "jobs/home.html",
#         {"jobs": jobs, "query": query}
#     )


# from django.shortcuts import render
# from .models import Job


# def home(request):
#     jobs = Job.objects.all()

#     query = request.GET.get("q", "").strip()

#     if query:
#         jobs = jobs.filter(
#             title__icontains=query
#         ) | jobs.filter(
#             company__icontains=query
#         ) | jobs.filter(
#             location__icontains=query
#         )

#     return render(
#         request,
#         "jobs/home.html",
#         {
#             "jobs": jobs,
#             "query": query
#         }
#     )


# from django.shortcuts import render, get_object_or_404
# from .models import Job


# def home(request):
#     jobs = Job.objects.all()

#     query = request.GET.get("q", "").strip()

#     if query:
#         jobs = jobs.filter(title__icontains=query) | jobs.filter(
#             company__icontains=query
#         ) | jobs.filter(location__icontains=query)

#     return render(
#         request,
#         "jobs/home.html",
#         {"jobs": jobs, "query": query}
#     )


# def job_detail(request, job_id):
#     job = get_object_or_404(Job, id=job_id)
#     return render(request, "jobs/job_detail.html", {"job": job})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Job, Application, SavedJob
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Job
def home(request):
    query = request.GET.get("q", "").strip()
    job_type = request.GET.get("job_type", "").strip()
    category = request.GET.get("category", "").strip()
    sort_by = request.GET.get("sort", "newest")
    salary_sort = request.GET.get("salary_sort", "")

    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        )

    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)

    if category:
        jobs = jobs.filter(category__iexact=category)

    if sort_by == "oldest":
        jobs = jobs.order_by("id")
    else:
        jobs = jobs.order_by("-id")

    if salary_sort == "high":
        jobs = jobs.order_by("-salary")
    elif salary_sort == "low":
        jobs = jobs.order_by("salary")

    paginator = Paginator(jobs, 3)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)



    return render(request, "jobs/home.html", {
        "jobs": jobs,
        "query": query,
        "selected_type": job_type,
        "sort_by": sort_by,
        "salary_sort": salary_sort,
        "selected_category": category,
        
    })
@login_required(login_url="login")
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    saved, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )

    return redirect("candidate_dashboard")
@login_required(login_url="login")
def remove_saved_job(request, saved_id):
    saved_job = get_object_or_404(
        SavedJob,
        id=saved_id,
        user=request.user
    )

    saved_job.delete()

    return redirect("candidate_dashboard")

@login_required(login_url="login")
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    already_applied = Application.objects.filter(
        user=request.user,
        job=job
    ).exists()

    return render(request, "jobs/job_detail.html", {
        "job": job,
        "already_applied": already_applied
    })


def apply_job(request, job_id):
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            request.get_full_path(),
            login_url="login"
        )

    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not full_name or not email or not phone:
            messages.error(request, "Please fill in all fields.")
            return render(request, "jobs/apply.html", {"job": job})

        if len(phone) > 15:
            messages.error(request, "Phone number is too long.")
            return render(request, "jobs/apply.html", {"job": job})

        already_applied = Application.objects.filter(
            user=request.user,
            job=job
        ).exists()

        if already_applied:
            messages.error(request, "You have already applied for this job.")
            return render(request, "jobs/apply.html", {"job": job})

        Application.objects.create(
            user=request.user,
            job=job,
            full_name=full_name,
            email=email,
            phone=phone
        )

        return redirect("application_success")

    return render(request, "jobs/apply.html", {"job": job})


def application_success(request):
    return render(request, "jobs/success.html")


@staff_member_required(login_url="login")
def recruiter_dashboard(request):
    applications = Application.objects.select_related("job").all()
    search_query = request.GET.get("q", "").strip()

    if search_query:
        applications = applications.filter(
            full_name__icontains=search_query
        ) | Application.objects.select_related("job").filter(
            email__icontains=search_query
        ) | Application.objects.select_related("job").filter(
            job__title__icontains=search_query
        )

    total_applications = Application.objects.count()

    return render(request, "jobs/recruiter_dashboard.html", {
        "applications": applications.distinct(),
        "total_applications": total_applications,
        "search_query": search_query,
    })


@staff_member_required(login_url="login")
def update_application_status(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=application_id)
        new_status = request.POST.get("status")

        allowed_statuses = ["Pending", "Shortlisted", "Rejected"]

        if new_status in allowed_statuses:
            application.status = new_status
            application.save(update_fields=["status"])
            messages.success(request, "Application status updated.")
        else:
            messages.error(request, "Invalid application status.")

    return redirect("recruiter_dashboard")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "jobs/register.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "jobs/login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def candidate_dashboard(request):
    applications = Application.objects.filter(
        user=request.user
    ).select_related("job")

    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related("job")

    return render(request, "jobs/candidate_dashboard.html", {
        "applications": applications,
        "saved_jobs": saved_jobs
    })
@login_required(login_url="login")
def update_profile(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        return redirect("candidate_dashboard")

    return render(request, "jobs/update_profile.html")
@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return redirect("candidate_dashboard")

        return render(request, "jobs/change_password.html", {
            "error": "Old password is incorrect."
        })

    return render(request, "jobs/change_password.html")
def password_reset_request(request):
    return PasswordResetView.as_view(
        template_name="jobs/password_reset.html",
        email_template_name="jobs/password_reset_email.html",
        extra_email_context={"protocol": "http"},
        success_url="/password-reset/done/"
    )(request)


def password_reset_done(request):
    return PasswordResetDoneView.as_view(
        template_name="jobs/password_reset_done.html"
    )(request)


def password_reset_confirm(request, uidb64, token):
    return PasswordResetConfirmView.as_view(
        template_name="jobs/password_reset_confirm.html",
        success_url="/reset/done/"
    )(request, uidb64=uidb64, token=token)


def password_reset_complete(request):
    return PasswordResetCompleteView.as_view(
        template_name="jobs/password_reset_complete.html"
    )(request)
def forgot_username(request):
    message = ""

    if request.method == "POST":
        email = request.POST.get("email")
        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if user:
            send_mail(
                "Your JobSphere Username",
                f"Your username is: {user.username}",
                "noreply@jobsphere.com",
                [email],
            )

        message = "If this email is registered, username details have been sent."

    return render(request, "jobs/forgot_username.html", {
        "message": message
    })