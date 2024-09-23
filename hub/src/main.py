from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.stapp_client import StappClient
from pydantic import BaseModel
import logging

app = FastAPI()



# Define a Pydantic model for the deployment data
class DeploymentData(BaseModel):
    name: str
    dns_name: str
    repo: str
    branch: str
    code_dir: str
    base_image: str
    replicas: int
    cpu_limit: str
    memory_limit: str


logging.basicConfig(level=logging.INFO)


# Serve the static directory for HTML and JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Instantiate the Kubernetes client
stapp_client = StappClient()


# Define a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root route to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("src/templates/index.html") as f:
        return HTMLResponse(content=f.read())

# API route to create a Streamlit app deployment
@app.post("/deployments/")
async def create_deployment(deployment: DeploymentData):
    logging.info(deployment)
    stapp_client.create_streamlit_app(name=deployment.name,
                                      dns_name=deployment.dns_name,
                                      repo=deployment.repo,
                                      branch=deployment.branch,
                                      code_dir=deployment.code_dir,
                                      base_image=deployment.base_image,
                                      replicas=deployment.replicas,
                                      cpu_limit=deployment.cpu_limit,
                                      memory_limit=deployment.memory_limit
                                      )
    return {"status": "Deployment created", "name": deployment.name}

# API route to list Streamlit apps
@app.get("/deployments/")
async def list_deployments():
    apps = stapp_client.list_streamlit_apps()
    return {"deployments": apps}

# API route to delete a Streamlit app deployment
@app.delete("/deployments/{dns_name}")
async def delete_deployment(dns_name: str):
    stapp_client.delete_streamlit_app(dns_name)
    return {"status": "Deployment deleted", "name": dns_name}

# API route to restart a Streamlit app by deleting its pod
@app.post("/deployments/{dns_name}/restart")
async def restart_deployment(dns_name: str):
    stapp_client.delete_pod_for_streamlit_app(dns_name)
    return {"status": "Deployment restarted", "name": dns_name}
