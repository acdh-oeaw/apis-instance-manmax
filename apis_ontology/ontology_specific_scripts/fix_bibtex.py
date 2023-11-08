from apis_bibsonomy.models import Reference
from apis_bibsonomy.utils import get_bibtex_from_url

cache = {}

def fix_bibtex():
    for ref in Reference.objects.all():
        if ref.bibs_url in cache:
            print(f"Using cached bibtex for {ref.bibs_url}")
            ref.bibtex = cache[ref.bibs_url]
        else:
            print(f"Getting bibtex for {ref.bibs_url}")
            bibtex = get_bibtex_from_url(ref.bibs_url)
            cache[ref.bibs_url] = bibtex
            ref.bibtex = bibtex
        ref.save()


def run(*args, **options):
    
    fix_bibtex()

    
