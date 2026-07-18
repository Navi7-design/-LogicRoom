from django.shortcuts import render, redirect
from django.contrib import messages


def register_view(request):
    from django.contrib.auth.forms import UserCreationForm

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f"🎉 Your account has been created successfully! Welcome, {user.username}!",
            )

            return redirect("login")

    else:
        form = UserCreationForm()

    context = {"form": form}

    return render(request, "register.html", context)


def login_view(request):
    from django.contrib.auth import authenticate, login as auth_login

    error = None

    if request.method == "POST":

        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            messages.success(
                request,
                f"✅Your successfully logged in! Welcome back, {user.username}!"
            )

            return redirect("index")

        else:
            error = "Invalid username or password!"

    context = {"error": error}

    return render(request, "login.html", context)