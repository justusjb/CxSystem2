"""cx_bui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Third-party
# from django.contrib import admin
from django.urls import include, path
import requests
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def github_callback(request):
    """Handle GitHub OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state', '')
    
    if not code:
        return HttpResponseRedirect('/?error=no_code')
    
    # Exchange code for token
    token_url = "https://github.com/login/oauth/access_token"
    
    # Read config to get client_id and client_secret
    import yaml
    from pathlib import Path
    import os
    
    cx_folder = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent
    yaml_path = cx_folder.joinpath('.cxconfig.yaml')
    
    try:
        with open(yaml_path.as_posix(), 'r') as file:
            oauth_config = yaml.load(file, Loader=yaml.FullLoader)
        
        client_id = oauth_config['oauth2']['client-id']
        client_secret = oauth_config['oauth2']['client-secret']
    except:
        return HttpResponseRedirect('/?error=config_error')
    
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }
    
    headers = {'Accept': 'application/json'}
    
    response = requests.post(token_url, data=data, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            # Redirect to main page with token in URL fragment
            return HttpResponseRedirect(f'/?access_token={access_token}&state={state}')
    
    return HttpResponseRedirect('/?error=token_exchange_failed')


urlpatterns = [
    path('', include('editor.urls')),
    path('callback', github_callback, name='github_callback'),
    # path('admin/', admin.site.urls),
]
