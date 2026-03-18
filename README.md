# ATS Integration

## How to Create a Free Trial / Sandbox
For this project, I utilize the SAP Business Accelerator Hub Sandbox.

1. Go to the SAP Business Accelerator Hub.

2. Register for a free SAP Universal ID.

3. Search for "SAP SuccessFactor Recruiting" and select the "Recruiting - Job Requisition" OData v2 API.

4. Navigate to the "Try Out" tab.

5. Select "SAP Sandbox" as the configured environment.

The Sandbox uses the base URL: https://sandbox.api.sap.com/successfactors/odata/v2.

## How to Generate API Key / Token

- Log in to the SAP Business Accelerator Hub.

- Click on your profile icon in the top right corner and go to Settings.

- Under the API Business Hub section, click Show API Key.

- Copy the key. It must be sent in the APIKey header for every request to the Sandbox.

## How to Run the Service Locally

Prerequisites
Node.js & npm (for Serverless Framework)

Python 3.9+

PostgreSQL (Local or Cloud)

1. Setup Backend (Serverless)
``` bash

npm install -g serverless
npm install serverless-offline

# SAP_API_KEY=your_key_here
# SAP_API_URL=https://sandbox.api.sap.com/successfactors/odata/v2

npx serverless offline
# The backend will be available at http://localhost:3000/dev.
```
2. Setup Frontend (Django)

``` bash
pip install -r requirements.txt

# Database Migration
python manage.py migrate

# Run Frontend
python manage.py runserver
# Visit http://127.0.0.1:8000/ to view the Portal.
```

## Example API Calls

1. GET /jobs

Query Params:
- limit: 10 (default)
- skip: 0 (for pagination)

Example Response:

```bash 
JSON
[
  {
    "id": "3",
    "title": "Standard Job Requisition",
    "location": "3612",
    "status": "OPEN",
    "external_url": "https://sandbox.api.sap.com/..."
  }
]
```
2. POST /candidates

Body (JSON):
```bash
JSON
{
  "name": "Abhinav M",
  "email": "abhinav@example.com",
  "phone": "9876543210",
  "resume_url": "https://drive.google.com/resume",
  "job_id": "3"
}
```
3. GET /applications

Query Params:
- job_id: 3 (Required)

Example Response:
```bash
JSON
[
  {
    "application_id": "1245",
    "candidate_name": "Vijay M",
    "status": "APPLIED"
  }
]
```

## Technical Note: Sandbox Restrictions
During testing, the following was observed regarding the SAP Public Sandbox:

- Candidate Creation: Fully functional. Successfully created Candidate ID 6642.

- Job Application Link: The JobApplication entity in the public sandbox returns a 403 Forbidden (COE0020) error due to "Insufficient field-level permissions."

- Solution implemented: The microservice handles this gracefully by confirming candidate creation and logging the restriction, ensuring the user experience is not interrupted.

## Author
- Muskan Tarafder
