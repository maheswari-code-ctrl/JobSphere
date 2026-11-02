from django.urls import path
from. import views
urlpatterns = [
    path("", views.home, name="home"),
    path("job/<int:job_id>/", views.job_detail, name="job_detail"),
    path("job/<int:job_id>/apply/", views.apply_job, name="apply_job"),
    path("application-success/", views.application_success, name="application_success"),
    path("recruiter-dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path(
    "password-reset/",
    views.password_reset_request,
    name="password_reset"
),
path(
    "password-reset/done/",
    views.password_reset_done,
    name="password_reset_done"
),
path(
    "reset/<uidb64>/<token>/",
    views.password_reset_confirm,
    name="password_reset_confirm"
),
path(
    "reset/done/",
    views.password_reset_complete,
    name="password_reset_complete"
),
    path("logout/", views.logout_user, name="logout"),
    path("candidate-dashboard/",views.candidate_dashboard,name="candidate_dashboard"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("save-job/<int:job_id>/", views.save_job, name="save_job"),
    path("remove-saved-job/<int:saved_id>/", views.remove_saved_job, name="remove_saved_job"),
    path("change-password/", views.change_password, name="change_password"),
    path("forgot-username/", views.forgot_username, name="forgot_username"),
    path(
        "update-status/<int:application_id>/",
        views.update_application_status,
        name="update_application_status"
    ),
]
