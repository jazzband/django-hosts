from django.http import HttpResponseRedirect, HttpResponseBadRequest

from .forms import RedirectForm

def redirect(request):
    form = RedirectForm(request.GET)

    if not form.is_valid():
        return HttpResponseBadRequest(repr(form.errors))

    response = HttpResponseRedirect(form.cleaned_data['path'])
    response.set_cookie('_domain', form.cleaned_data['domain'])
    response.status_code = 307 # Re-submit POST requests

    return response
