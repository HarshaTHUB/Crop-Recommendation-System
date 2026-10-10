import pickle
from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CropRecommendationForm, LoginForm, SignUpForm
from .models import CropHistory


# Load the model from this app's folder, independent of the current working directory.
MODEL_PATH = Path(__file__).resolve().parent / "RandomForest.pkl"
with MODEL_PATH.open("rb") as model_file:
    model = pickle.load(model_file)


def index(request):
    return render(request, "Recomender/index.html")


def about(request):
    return render(request, "Recomender/about_us.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "Recomender/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("index")
            form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "Recomender/login.html", {"form": form})


@login_required
def recommend_crop(request):
    if request.method == "POST":
        form = CropRecommendationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            user_data = [
                instance.N,
                instance.P,
                instance.K,
                instance.temperature,
                instance.humidity,
                instance.ph,
                instance.rainfall,
            ]
            instance.recommended_crop = model.predict([user_data])[0]
            instance.save()
            return redirect("history")
    else:
        form = CropRecommendationForm()
    return render(request, "Recomender/recommend_crop.html", {"form": form})


@login_required
def history(request):
    recommendations = CropHistory.objects.filter(user=request.user)
    return render(
        request,
        "Recomender/history.html",
        {"recommendations": recommendations},
    )


@login_required
def user_logout(request):
    logout(request)
    return redirect("index")
