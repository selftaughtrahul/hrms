from .models import CompanyConfig


def company_info(request):
    """
    Context processor that injects the Company Configuration for the current
    tenant into every Django template automatically.
    For unauthenticated users or superusers without a tenant, returns None.
    """
    config = None
    try:
        tenant = getattr(request, 'tenant', None)
        if tenant:
            config = CompanyConfig.load_for_tenant(tenant)
    except Exception:
        config = None

    return {
        'company': config,
        'current_tenant': getattr(request, 'tenant', None),
    }
