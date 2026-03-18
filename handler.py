import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('SAP_API_KEY')
base_url = os.getenv('SAP_API_URL')

# Standard CORS Headers
HEADERS_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": True,
    "Content-Type": "application/json"
}

def get_jobs(event, context):
    # GET parameters come from queryStringParameters, not body
    params = event.get('queryStringParameters') or {}
    limit = params.get("limit", 10)
    skip = params.get("skip", 0)
    
    url = f'{base_url}/JobRequisition?$format=json&$top={limit}&$skip={skip}'
    headers = {'APIKey': api_key, "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        sap_jobs = data.get('d', {}).get('results', [])

        unified_jobs = []
        for job in sap_jobs:
            sap_status = job.get("internalStatus", "").upper()
            if any(x in sap_status for x in ["OPEN", "PRE-APPROVED"]):
                status = "OPEN"
            elif "DRAFT" in sap_status:
                status = "DRAFT"
            else:
                status = "CLOSED"

            unified_jobs.append({
                'id': job.get('jobReqId'),
                "title": job.get("templateName", "Untitled Position"),
                "location": job.get("customString4", "Remote"),
                'status': status,
                'external_url': f"https://api.sap.com/api/RCM_JobReq/resource",
            })
        
        return {
            'statusCode': 200,
            'headers': HEADERS_CORS,
            'body': json.dumps(unified_jobs)
        }
    except Exception as e:
        return {'statusCode': 500, 'headers': HEADERS_CORS, 'body': json.dumps({'error': str(e)})}

def post_candidate(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        full_name = body.get("name", "New Candidate")
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else "User"
        
        headers = {
            "APIKey": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # STEP 1: Create Candidate
        candidate_payload = {
            "firstName": first_name,
            "lastName": last_name,
            "primaryEmail": body.get("email"),
            "contactEmail": body.get("email"),
            "cellPhone": body.get("phone"),
            "country": "IN", 
            "city": "Bengaluru",
            "shareProfile": "1",
            "agreeToPrivacyStatement": "true" 
        }
        
        cand_res = requests.post(f"{base_url}/Candidate", headers=headers, json=candidate_payload)
        
        if cand_res.status_code != 201:
            return {"statusCode": cand_res.status_code, "headers": HEADERS_CORS, "body": cand_res.text}

        candidate_id = cand_res.json()['d']['candidateId']

        # STEP 2: Link to Job
        app_payload = {
            "jobReqId": str(body.get("job_id")),
            "candidateId": str(candidate_id),
            "status": "New",
            "source": "Other",
            "countryCode": "IN",
            "contactEmail": body.get("email"),
            "firstName": first_name,
            "lastName": last_name,
            "formerEmployee": False
        }

        headers["DataServiceVersion"] = "2.0" 
        app_res = requests.post(f"{base_url}/JobApplication", headers=headers, json=app_payload)

        # Handle the Sandbox 403 gracefully
        if app_res.status_code == 403:
            return {
                "statusCode": 201,
                "headers": HEADERS_CORS,
                "body": json.dumps({
                    "message": "Candidate created (ID: {}). Note: Job link restricted by Sandbox permissions.".format(candidate_id),
                    "candidate_id": candidate_id,
                    "warning": "COE0020_FORBIDDEN"
                })
            }

        return {
            "statusCode": 201,
            "headers": HEADERS_CORS,
            "body": json.dumps({"message": "Application successful", "candidate_id": candidate_id})
        }

    except Exception as e:
        return {"statusCode": 500, "headers": HEADERS_CORS, "body": json.dumps({"error": str(e)})}

def get_job_applications(event, context):
    params = event.get('queryStringParameters') or {}
    job_id = params.get('job_id')

    if not job_id:
        return {'statusCode': 400, 'headers': HEADERS_CORS, 'body': json.dumps({'error': 'Missing job_id'})}
    
    # Correct SAP filter format for Long types
    url = f"{base_url}/JobApplication?$filter=jobReqId eq {job_id}L&$expand=candidate&$format=json"
    headers = {'APIKey': api_key, 'Accept': 'application/json'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sap_apps = response.json().get('d', {}).get('results', [])

        unified_apps = []
        status_map = {
            "OPEN": "APPLIED",
            "NOT APPLIED": "APPLIED",
            "INTERVIEW": "SCREENING",
            "HIRED": "HIRED",
            "REJECTED": "REJECTED"
        }

        for app in sap_apps:
            cand = app.get('candidate', {})
            unified_apps.append({
                'application_id': app.get('applicationId'),
                'candidate_name': f"{cand.get('firstName','')} {cand.get('lastName','')}".strip(),
                'candidate_email': cand.get('primaryEmail'),
                'status': status_map.get(app.get("status", "").upper(), "APPLIED")
            })

        return {'statusCode': 200, 'headers': HEADERS_CORS, 'body': json.dumps(unified_apps)}
    except Exception as e:
        return {'statusCode': 500, 'headers': HEADERS_CORS, 'body': json.dumps({'error': str(e)})}