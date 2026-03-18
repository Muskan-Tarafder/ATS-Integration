from django.shortcuts import render,redirect
from .forms import *
import requests

import requests
from django.shortcuts import render
from .forms import ApplicationForm

API_BASE = "http://localhost:3000/dev"

def portal(request, job_id=None):
    current_skip = int(request.GET.get('skip', 0))
    limit = 10
    
    context = {
        'view': 'jobs',
        'current_skip': current_skip,
        'next_skip': current_skip + limit,
        'prev_skip': max(0, current_skip - limit),
    }
    
    # VIEW APPLICATIONS
    if request.GET.get('action') == 'view' and job_id:
        res = requests.get(f"{API_BASE}/applications", params={'job_id': job_id})
        context.update({'view': 'applicants', 'apps': res.json(), 'job_id': job_id})

    # CANDIDATE DATA ENTRY
    elif job_id:
        form = ApplicationForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            payload = {**form.cleaned_data, 'job_id': job_id}
            res = requests.post(f"{API_BASE}/candidates", json=payload)
            context.update({'view': 'success', 'res': res.json()})
        else:
            context.update({'view': 'apply', 'form': form, 'job_id': job_id})

    # JOB LIST 
    else:
        params = {'limit': limit, 'skip': current_skip}
        res = requests.get(f"{API_BASE}/jobs", params=params)
        
        jobs = res.json() if res.status_code == 200 else []
        context.update({
            'jobs': jobs,
            'has_jobs': len(jobs) > 0,
            'is_last_page': len(jobs) < limit 
        })
    return render(request, 'portal.html', context)