from django import forms


class AppointmentRecommendationForm(forms.Form):

    age = forms.IntegerField(min_value=1)

    gender = forms.ChoiceField(
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ]
    )

    symptoms = forms.CharField(
        widget=forms.Textarea
    )

    duration = forms.CharField()

    severity = forms.ChoiceField(
        choices=[
            ("Mild", "Mild"),
            ("Moderate", "Moderate"),
            ("Severe", "Severe"),
        ]
    )