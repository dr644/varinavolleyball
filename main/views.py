from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm, PostForm, WorkoutForm
from .models import Post, WorkoutLog, Player
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .models import Profile

def home(request):
    return render(request, 'main/home.html')

def schedule(request):
    return render(request, 'main/schedule.html')

def roster(request, level=None):
    # Get level from URL or querystring, default to Varsity
    level = level or request.GET.get("level", "Varsity")

    sort_field = request.GET.get("sort", "number")
    direction = request.GET.get("dir", "asc")

    # Filter by level
    players = Player.objects.filter(level=level)

    # Handle year sorting separately
    if sort_field == "year":
        year_order = {"Freshman": 1, "Sophomore": 2, "Junior": 3, "Senior": 4}
        players = sorted(
            players,
            key=lambda p: year_order.get(p.year, 99),
            reverse=(direction == "desc"),
        )
    else:
        order_by = f"-{sort_field}" if direction == "desc" else sort_field
        players = players.order_by(order_by)

    # Determine next sort direction
    next_dir = "desc" if direction == "asc" else "asc"

    context = {
        "players": players,
        "sort_field": sort_field,
        "direction": direction,
        "next_dir": next_dir,
        "level": level,  # ensures toggle stays highlighted correctly
    }

    return render(request, "main/roster.html", context)



def statistics(request):
    sort_field = request.GET.get("sort", "number")
    direction = request.GET.get("dir", "asc")
    level = request.GET.get("level", "Varsity")  # Default view

    # Base queryset filtered by Varsity or JV
    stats = list(Player.objects.filter(level=level))

    # Compute kill percentage for everyone (always)
    for s in stats:
        if s.attacks and s.attacks > 0:
            s.kill_percentage = round((s.kills / s.attacks) * 100, 1)
        else:
            s.kill_percentage = 0.0

    # Handle sorting (including computed kill_percentage)
    if sort_field == "kill_percentage":
        stats.sort(key=lambda x: x.kill_percentage, reverse=(direction == "desc"))
    else:
        reverse = direction == "desc"
        stats.sort(key=lambda x: getattr(x, sort_field, 0) or 0, reverse=reverse)

    next_dir = "desc" if direction == "asc" else "asc"

    context = {
        "stats": stats,
        "sort_field": sort_field,
        "direction": direction,
        "next_dir": next_dir,
        "level": level,  # Pass current team level to template
    }
    return render(request, "main/statistics.html", context)



def login_view(request):
    # If user was redirected here from @login_required
    if 'next' in request.GET:
        messages.warning(request, "You must be logged in to access that page.")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Respect ?next= so user returns where they came from
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    # Keep ?next= so form submits correctly
    return render(request, "main/login.html", {"next": request.GET.get("next", "")})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request=request)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = True
            user.set_password(form.cleaned_data["password"])
            user.save()

            role = form.cleaned_data["role"]
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            # success: clear the CAPTCHA so a new one is generated next time
            request.session.pop("captcha_sum",  None)
            request.session.pop("captcha_text", None)

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
    else:
        form = RegisterForm(request=request)

    return render(request, "main/register.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='CurrentPlayers').exists())
def team(request):
    workouts = WorkoutLog.objects.filter(player=request.user).order_by('-date')
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.player = request.user
            workout.save()
            return redirect('team')
    else:
        form = WorkoutForm()
    return render(request, 'main/team.html', {'form': form, 'workouts': workouts})
