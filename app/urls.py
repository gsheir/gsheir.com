from django.urls import path

from . import views

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about_me/", views.AboutMeView.as_view(), name="about_me"),
    path("cv/", views.CVView.as_view(), name="cv"),
    path("blog/", views.BlogHomeView.as_view(), name="blog_home"),
    path(
        "blog/fantasy_football/",
        views.BlogFantasyFootballView.as_view(),
        name="blog_fantasy_football",
    ),
    path(
        "blog/coaching/",
        views.BlogCoachingView.as_view(),
        name="blog_coaching",
    ),
    path(
        "blog/arsenal_press_part_1/",
        views.BlogArsenalPressPart1View.as_view(),
        name="blog_arsenal_press_part_1",
    ),
    path(
        "blog/arsenal_press_part_2/",
        views.BlogArsenalPressPart2View.as_view(),
        name="blog_arsenal_press_part_2",
    ),
    path(
        "blog/arsenal_corners_part_1/",
        views.BlogArsenalCornersPart1View.as_view(),
        name="blog_arsenal_corners_part_1",
    ),
    path(
        "blog/arsenal_corners_part_2/",
        views.BlogArsenalCornersPart2View.as_view(),
        name="blog_arsenal_corners_part_2",
    ),
]
