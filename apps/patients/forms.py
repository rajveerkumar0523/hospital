from django import forms

from .models import PatientProfile


class PatientProfileForm(forms.ModelForm):

    class Meta:
        model = PatientProfile

        fields = [
            "date_of_birth",
            "gender",
            "blood_group",
            "address",
            "emergency_contact",
            "allergies",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "gender": forms.Select(),

            "blood_group": forms.Select(),

            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter your complete address",
                }
            ),

            "emergency_contact": forms.TextInput(
                attrs={
                    "placeholder": "Emergency contact number",
                }
            ),

            "allergies": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Mention allergies, if any",
                }
            ),
        }