import json
import logging
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import CarMake, CarModel
from .restapis import analyze_review_sentiments, get_request, post_review
from .populate import initiate

logger = logging.getLogger(__name__)


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _backend_error(exc):
    logger.warning("Backend service request failed: %s", exc)
    return JsonResponse({"status": 502, "error": "The dealership service is temporarily unavailable."}, status=502)


@csrf_exempt
@require_POST
def login_user(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "Invalid JSON"}, status=400)
    username = str(data.get("userName", data.get("username", ""))).strip()
    password = str(data.get("password", ""))
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"userName": username, "status": "Invalid credentials"}, status=401)
    login(request, user)
    return JsonResponse({
        "userName": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "status": "Authenticated",
    })


@require_GET
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})

@csrf_exempt
@require_POST
def registration(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "Invalid JSON"}, status=400)
    username = str(data.get("userName", data.get("username", ""))).strip()
    password = str(data.get("password", ""))
    email = str(data.get("email", "")).strip()
    first_name = str(data.get("firstName", data.get("first_name", ""))).strip()
    last_name = str(data.get("lastName", data.get("last_name", ""))).strip()
    if not username or not password or not email:
        return JsonResponse({"error": "Username, email, and password are required."}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "Password must contain at least 8 characters."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "That username is already registered."}, status=409)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "That email is already registered."}, status=409)
    user = User.objects.create_user(
        username=username, password=password, email=email,
        first_name=first_name, last_name=last_name,
    )
    return JsonResponse({"status": "Registered", "userName": user.username}, status=201)


@require_GET
def get_dealerships(request):
    try:
        dealers = get_request("fetchDealers")
        return JsonResponse({"status": 200, "dealers": dealers})
    except Exception as exc:
        return _backend_error(exc)


@require_GET
def get_dealers_by_state(request, state):
    try:
        dealers = get_request(f"fetchDealers/{state}")
        return JsonResponse({"status": 200, "dealers": dealers})
    except Exception as exc:
        return _backend_error(exc)


@require_GET
def get_dealer_details(request, dealer_id):
    try:
        dealer = get_request(f"fetchDealer/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": [dealer]})
    except Exception as exc:
        logger.warning("Could not fetch dealer %s: %s", dealer_id, exc)
        return JsonResponse({"status": 404, "dealer": [], "error": "Dealership not found."}, status=404)


@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
        for item in reviews:
            item["sentiment"] = analyze_review_sentiments(item.get("review", ""))
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as exc:
        return _backend_error(exc)


@csrf_exempt
@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 401, "error": "Please log in before posting a review."}, status=401)
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": 400, "error": "Invalid JSON."}, status=400)
    required = ("dealership", "review", "purchase_date", "car_make", "car_model", "car_year")
    if any(data.get(field) in (None, "") for field in required):
        return JsonResponse({"status": 400, "error": "Please complete every review field."}, status=400)
    if not str(data.get("review", "")).strip():
        return JsonResponse({"status": 400, "error": "Review text cannot be empty."}, status=400)
    payload = dict(data)
    payload["name"] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    try:
        payload["dealership"] = int(payload["dealership"])
        payload["car_year"] = int(payload["car_year"])
        result = post_review(payload)
        result["sentiment"] = analyze_review_sentiments(payload["review"])
        return JsonResponse({"status": 200, "review": result}, status=201)
    except Exception as exc:
        return _backend_error(exc)


@require_GET
def get_cars(request):
    try:
        cars = get_request("fetchCars")
        unique = {}
        for car in cars:
            key = (car.get("make", ""), car.get("model", ""))
            unique[key] = {"CarMake": key[0], "CarModel": key[1]}
        return JsonResponse({"status": 200, "CarModels": list(unique.values())})
    except Exception as exc:
        return _backend_error(exc)


@require_GET
def get_all_car_makes(request):
    if not CarMake.objects.exists():
        initiate()
    makes = CarMake.objects.prefetch_related("models").all()
    return JsonResponse({
        "status": 200,
        "CarMakes": [
            {"id": make.id, "CarMake": make.name, "CarModels": [
                {"id": model.id, "CarModel": model.name, "Type": model.type, "Year": model.year}
                for model in make.models.all()
            ]}
            for make in makes
        ]
    })


def home(request):
    frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000").rstrip("/")
    return render(request, "Home.html", {"frontend_url": frontend_url})


def dealers_home(request):
    return redirect(os.getenv("FRONTEND_URL", "http://127.0.0.1:3000").rstrip("/") + "/dealers")


def about(request):
    return render(request, "About.html")


def contact(request):
    return render(request, "Contact.html")
