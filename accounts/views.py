from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect("home")  # Redirect to homepage (update as needed)
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Redirect to homepage (update as needed)
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")  # Redirect to login page after logout


def verify(request):
    if request.method == "GET":
        list(get_messages(request))

    # If the user is already verified, show success message
    if request.user.profile.is_verified:
        return render(request, "accounts/verify.html", {"success": True})

    if request.method == "POST":
        answer = request.POST.get("answer")
        if answer == "ParkEasy":
            request.user.profile.is_verified = True
            request.user.profile.save()
            messages.success(
                request, "Congratulations, you are verified and can now post spots!"
            )
            # Render the page with success flag instead of redirecting
            return render(request, "accounts/verify.html", {"success": True})
        else:
            messages.error(
                request, "Incorrect answer, verification failed. Please try again."
            )

    # If GET or POST with errors, render the form as normal
    return render(request, "accounts/verify.html")
