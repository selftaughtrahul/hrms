from .models import CompanyConfig

def company_info(request):
    """
    Context processor that injects the Master Configuration (Company Name/Logo) 
    into every Django template automatically.
    """
    try:
        config = CompanyConfig.load()
    except Exception:
        config = None

    return {
        'company': config
    }
