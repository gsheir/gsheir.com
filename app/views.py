from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"


class AboutMeView(TemplateView):
    template_name = "about_me/home.html"


class CVView(TemplateView):
    template_name = "about_me/cv.html"


class BlogHomeView(TemplateView):
    template_name = "blog/home.html"


class BlogFantasyFootballView(TemplateView):
    template_name = "blog/fantasy_football.html"


class BlogCoachingView(TemplateView):
    template_name = "blog/coaching.html"


class BlogArsenalPressPart1View(TemplateView):
    template_name = "blog/arsenal_press_part_1.html"


class BlogArsenalPressPart2View(TemplateView):
    template_name = "blog/arsenal_press_part_2.html"


class BlogArsenalCornersPart1View(TemplateView):
    template_name = "blog/arsenal_corners_part_1.html"


class BlogArsenalCornersPart2View(TemplateView):
    template_name = "blog/arsenal_corners_part_2.html"
