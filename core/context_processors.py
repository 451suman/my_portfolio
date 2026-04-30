from portfolio.models import SocialLink


def social_links(request):
    """
    Context processor to provide social links to all templates
    """
    try:
        social_links = SocialLink.objects.filter(is_active=True).order_by("display_order")
        return {"social_links": social_links}
    except Exception:
        return {"social_links": []}
