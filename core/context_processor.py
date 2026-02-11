from core import models as aguipex_models
from django.db.models import Min, Max
from django.contrib import messages

def default(request):
    partenaires = aguipex_models.Partenaire.objects.filter(status="publier").order_by('-created_at')    
    programmes = aguipex_models.Programme.objects.filter(status="publier").order_by("-created_at")


    return {
        'partenaires':partenaires,
        'programmes':programmes,
    }