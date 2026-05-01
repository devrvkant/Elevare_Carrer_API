# Career Prediction API

A simple Flask API that predicts careers using a TF-IDF + Random Forest pipeline.

## Endpoints

- `GET /` health message
- `POST /predict` with JSON body:
  ```json
  {
    "course": "B.Tech",
    "specialization": "Computer Science",
    "interests": "AI, ML",
    "skills": "Python, Data Analysis"
  }
  ```

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_DEBUG=1
python app.py
```

## Deploy to Azure App Service (Linux)

1. Login and set subscription

```bash
az login
az account set --subscription <SUBSCRIPTION_ID>
```

2. Create resource group and App Service Plan

```bash
RG=elevare-ml-rg
LOC=westeurope
PLAN=elevare-ml-plan
APP=elevare-ml-api-$RANDOM

az group create --name $RG --location $LOC
az appservice plan create --name $PLAN --resource-group $RG --sku B1 --is-linux
```

3. Create the Web App

```bash
az webapp create \
  --resource-group $RG \
  --plan $PLAN \
  --name $APP \
  --runtime "PYTHON|3.11"
```

4. Configure startup command (uses gunicorn via Procfile by default). Ensure `PORT` binding:

```bash
az webapp config appsettings set \
  --resource-group $RG \
  --name $APP \
  --settings WEBSITES_PORT=8000
```

Note: Azure sets `$PORT` automatically; Procfile uses `$PORT`. WEBSITES_PORT is a safe default.

5. Deploy code

- Using Zip Deploy:

```bash
zip -r deploy.zip . -x '*.venv*' -x '*.git*' -x '__pycache__/*'
az webapp deployment source config-zip --resource-group $RG --name $APP --src deploy.zip
```

- Or with `az webapp up` (simpler):

```bash
az webapp up --runtime "PYTHON:3.11" --sku B1 --name $APP --location $LOC
```

6. Test

```bash
curl https://$APP.azurewebsites.net/

curl -X POST https://$APP.azurewebsites.net/predict \
  -H 'Content-Type: application/json' \
  -d '{"course":"B.Tech","specialization":"CS","interests":"AI","skills":"Python"}'
```

## Notes

- Large model files are loaded from the app directory via absolute path joins.
- For higher performance, consider enabling Always On and scaling the plan.
- For CI/CD, connect GitHub Actions to the Web App and build a publish workflow.
