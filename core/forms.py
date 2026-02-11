# core/forms.py
from django import forms
from .models import CandidatureManifestation


class CandidatureManifestationForm(forms.ModelForm):
    """Formulaire Front Office : postuler à une manifestation (statut À postuler)."""
    nom_entreprise = forms.CharField(max_length=200, required=True)
    email_contact = forms.EmailField(required=True)

    class Meta:
        model = CandidatureManifestation
        fields = (
            'nom_entreprise', 'email_contact', 'telephone_contact', 'message',
            'nombre_personnes', 'produits_entreprise', 'domaine_activite',
            'a_rccm', 'a_code_nif', 'type_entreprise', 'responsable_entreprise',
            'date_creation_entreprise', 'nombre_manifestations_participees',
            'peut_se_financer', 'siege_social', 'certifications'
        )
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'entreprise *"}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email du contact *'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Message (optionnel)'}),
            'nombre_personnes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de personnes', 'min': 1}),
            'produits_entreprise': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Liste des produits de votre entreprise'}),
            'domaine_activite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domaine d\'activité'}),
            'a_rccm': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'a_code_nif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SARL, SA, EURL, etc.'}),
            'responsable_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du responsable'}),
            'date_creation_entreprise': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre_manifestations_participees': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de manifestations', 'min': 0}),
            'peut_se_financer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'siege_social': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse du siège social'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Liste des certifications obtenues'}),
        }
        labels = {
            'nom_entreprise': "Nom de l'entreprise",
            'email_contact': 'Email du contact',
            'telephone_contact': 'Téléphone',
            'message': 'Message (optionnel)',
            'nombre_personnes': "Nombre de personnes dans l'entreprise",
            'produits_entreprise': 'Produits de l\'entreprise',
            'domaine_activite': 'Domaine d\'activité',
            'a_rccm': 'Avez-vous un RCCM ?',
            'a_code_nif': 'Avez-vous un code NIF à jour ?',
            'type_entreprise': 'Type d\'entreprise',
            'responsable_entreprise': 'Responsable de l\'entreprise',
            'date_creation_entreprise': 'Date de création de l\'entreprise',
            'nombre_manifestations_participees': 'À combien de manifestations commerciales avez-vous déjà participé ?',
            'peut_se_financer': 'Pouvez-vous vous financer ?',
            'siege_social': 'Siège social de l\'entreprise',
            'certifications': 'Certifications de l\'entreprise',
        }
