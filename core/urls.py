from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path("", views.home, name="home"), 
    path("booking/",views.booking, name="booking"),
    path("ethiopia/",views.ethiopia, name="ethiopia"),
    path("nigeria/",views.nigeria, name="nigeria"),
    path("kenya/",views.kenya, name="kenya"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="core/password_reset_form.html",
        email_template_name="core/password_reset_email.html",
        subject_template_name="core/password_reset_subject.txt",
        success_url=reverse_lazy("password_reset_done"),
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="core/password_reset_done.html"
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="core/password_reset_confirm.html",
        success_url=reverse_lazy("password_reset_complete"),
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="core/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("whatsapp/", views.whatsapp, name="whatsapp"),
    path("mentorship/", views.mentorship, name="mentorship"),
    path("library/", views.library, name="library"),
    path("gallery2/", views.gallery2, name="gallery2"),

]
    
   

