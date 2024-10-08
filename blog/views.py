from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .validation import Validation as v
from .models import User, Blog


def index(request):
    blogs = Blog.objects.all()
    context = {"blogs": blogs}
    return render(request, "blog/index.html", context)


def login(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "auth/login.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if (
            v.is_empty(full_name)
            or v.is_empty(email)
            or v.is_empty(password)
            or v.is_empty(confirm_password)
        ):
            messages.error(request, "All fields are required.")
            return render(request, "auth/register.html")

        if not v.match(password, confirm_password):
            messages.error(request, "Password does not match.")
            return render(request, "auth/register.html")
        if not v.is_valid_email(email):
            messages.error(request, "Invalid email.")
            return render(request, "auth/register.html")

        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already taken.")
                return render(request, "auth/register.html")
            user = User.objects.create_user(
                email=email, password=password, full_name=full_name
            )
            user.save()
            messages.success(
                request, "Account created successfully. Login to continue."
            )
            return redirect("login")
        except Exception as e:
            messages.error(request, "Something went wrong.")
            return render(request, "auth/register.html")

    return render(request, "auth/register.html")


@login_required(login_url="login")
def logout(request):
    auth_logout(request)
    return redirect("login")


@login_required(login_url="login")
def profile(request):
    blogs = Blog.objects.filter(user=request.user)
    return render(request, "blog/profile.html", {"blogs": blogs})


def add_blog(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        title = request.POST.get("title")
        content = request.POST.get("content")
        image = request.FILES.get("image")

        if v.is_empty(title) or v.is_empty(content) or not v.file_exists(image):
            messages.error(request, "All fields are required.")
            return render(request, "blog/add_blog.html")

        if not v.valid_file_size(image, 2):
            messages.error(request, "File size should be less than 2MB.")
            return render(request, "blog/add_blog.html")

        if not v.valid_file_extension(image, ["jpg", "jpeg", "png"]):
            messages.error(
                request, "Invalid file format. Only jpg, jpeg and png are allowed."
            )
            return render(request, "blog/add_blog.html")

        blog = Blog(
            title=title.strip(), content=content.strip(), image=image, user=request.user
        )
        blog.save()
        messages.success(request, "Blog added successfully.")

    return render(request, "blog/add_blog.html")


def delete_blog(request, id):
    blog = Blog.objects.get(id=id)
    if blog.user == request.user:
        blog.delete()
        messages.success(request, "Blog deleted successfully.")

    else:
        messages.error(request, "You are not authorized to delete this blog.")
        return redirect("/")
    return redirect("profile")

