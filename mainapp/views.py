from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import AdminLoginForm, BlogForm, CommentForm
from .models import Blog, Comment, Logininfo


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "Please log in as an admin to continue.")
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapped_view


def migrate_legacy_admin(request, username, password):
    try:
        legacy_user = Logininfo.objects.get(username=username, password=password)
    except Logininfo.DoesNotExist:
        return None

    if legacy_user.usertype.lower() != "admin":
        return None

    user_model = get_user_model()
    if user_model.objects.filter(username=username).exists():
        return None

    user_model.objects.create_user(
        username=username,
        password=password,
        is_staff=True,
        is_superuser=False,
    )
    return authenticate(request, username=username, password=password)


def index(request):
    blogs = Blog.objects.all()
    return render(request, "index.html", {"blogs": blogs})


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admindash")

    form = AdminLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is None:
            user = migrate_legacy_admin(request, username, password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("admindash")

        messages.error(request, "Invalid admin username or password.")

    return render(request, "login.html", {"form": form})


@admin_required
def admindash(request):
    blog_count = Blog.objects.count()
    total_views = Blog.objects.aggregate(total_views=Sum("views"))["total_views"] or 0
    comment_count = Comment.objects.count()
    admin_count = get_user_model().objects.filter(is_staff=True).count()
    recent_blogs = Blog.objects.all()[:5]

    context = {
        "blog_count": blog_count,
        "total_views": total_views,
        "comment_count": comment_count,
        "admin_count": admin_count,
        "recent_blogs": recent_blogs,
    }
    return render(request, "admindash.html", context)


@admin_required
def addblog(request):
    form = BlogForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blog added successfully.")
        return redirect("viewsblog")

    return render(request, "addblog.html", {"form": form})


@admin_required
def viewsblog(request):
    blogs = Blog.objects.all()
    return render(request, "viewsblog.html", {"blogs": blogs})


@admin_required
@require_POST
def delview(request, id):
    blog = get_object_or_404(Blog, id=id)
    blog.delete()
    messages.success(request, "Blog deleted successfully.")
    return redirect("viewsblog")


@admin_required
def editblog(request, id):
    blog = get_object_or_404(Blog, id=id)
    form = BlogForm(request.POST or None, request.FILES or None, instance=blog)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blog updated successfully.")
        return redirect("viewsblog")

    return render(request, "editblog.html", {"form": form, "blog": blog})


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully.")
    return redirect("login")


def readblog(request, id):
    blog = get_object_or_404(Blog, id=id)
    comment_form = CommentForm(request.POST or None)

    if request.method == "POST":
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.save()
            messages.success(request, "Thanks for sharing your comment.")
            comment_url = f"{reverse('readblog', args=[blog.id])}?commented=1"
            return redirect(comment_url)
        messages.error(request, "Please correct the comment form below.")
    elif request.GET.get("commented") != "1":
        Blog.objects.filter(id=blog.id).update(views=F("views") + 1)
        blog.refresh_from_db()

    comments = Comment.objects.filter(blog=blog)
    context = {
        "blog": blog,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "readblog.html", context)
