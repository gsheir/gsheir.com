from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    # Root blank page
    path("", views.HomeView.as_view(), name="home"),
    # About me page
    path("about_me/", views.AboutMeView.as_view(), name="about_me"),
    # Blog
    path("blog/", views.BlogHomeView.as_view(), name="blog_home"),
    path(
        "blog/fantasy_football/",
        views.BlogFantasyFootballView.as_view(),
        name="blog_fantasy_football",
    ),
    # Game functionality under weuro2025_game path
    path("weuro2025_game/", views.GameHomeView.as_view(), name="game_home"),
    path(
        "weuro2025_game/login/",
        auth_views.LoginView.as_view(template_name="game/login.html"),
        name="login",
    ),
    path("weuro2025_game/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("weuro2025_game/register/", views.RegisterView.as_view(), name="register"),
    path(
        "weuro2025_game/league/<uuid:league_id>/",
        views.LeagueView.as_view(),
        name="league",
    ),
    path(
        "weuro2025_game/league/<uuid:league_id>/select/",
        views.SelectionView.as_view(),
        name="selection",
    ),
    path(
        "weuro2025_game/create-league/",
        views.CreateLeagueView.as_view(),
        name="create_league",
    ),
    path(
        "weuro2025_game/join-league/",
        views.JoinLeagueView.as_view(),
        name="join_league",
    ),
    # API endpoints
    path(
        "weuro2025_game/api/players/",
        views.PlayerListAPIView.as_view(),
        name="api_players",
    ),
    path(
        "weuro2025_game/api/provisional-selection/",
        views.ProvisionalSelectionAPIView.as_view(),
        name="api_provisional_selection",
    ),
]
