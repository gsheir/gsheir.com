from django import forms

from .models import League


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["name", "max_participants"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter league name"}
            ),
            "max_participants": forms.NumberInput(
                attrs={"class": "form-control", "min": 2, "max": 20}
            ),
        }


class JoinLeagueForm(forms.Form):
    code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter league code",
                "style": "text-transform: uppercase;",
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].upper()
        return code
