const apiBaseUrl = '/';

// Function to create a deployment
async function createDeployment() {
    const name = document.getElementById('app-name').value;
    const dns_name = document.getElementById('dns-name').value;
    const repo = document.getElementById('repo-url').value;
    const branch = document.getElementById('branch').value;
    const code_dir = document.getElementById('code-dir').value;
    const base_image = document.getElementById('base-image').value;
    const replicas = parseInt(document.getElementById('replicas').value); // Replicas
    const memory_limit = parseInt(document.getElementById('memory-limit').value); // Memory limit
    const cpu_limit = parseInt(document.getElementById('cpu-limit').value); // CPU limit

    if (!name || !dns_name || !repo || !branch || !code_dir || !base_image || !replicas || !memory_limit || !cpu_limit) {
        alert("All fields are required.");
        return;
    }

    const deploymentData = {
        name: name,
        dns_name: dns_name,
        repo: repo,
        branch: branch,
        code_dir: code_dir,
        base_image: base_image,
        replicas: replicas,
        memory_limit: `${memory_limit}Mi`, // Memory limit in MiB
        cpu_limit: `${cpu_limit}m` // CPU limit in Millicores
    };

    try {
        const response = await fetch(apiBaseUrl + 'deployments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(deploymentData)
        });

        if (response.ok) {
            alert('Deployment created!');
            fetchDeployments();  // Refresh the list after creating
        } else {
            const errorData = await response.json();
            alert('Error creating deployment: ' + JSON.stringify(errorData));
        }
    } catch (error) {
        alert("Error creating deployment: " + error.message);
    }
}

// Function to fetch and display deployments
async function fetchDeployments() {
    try {
        const response = await fetch(apiBaseUrl + 'deployments/');
        if (!response.ok) throw new Error("Failed to fetch deployments");

        const data = await response.json();

        // Zugriff auf das deployments-Array im API-Antwortobjekt
        if (!data.deployments || !Array.isArray(data.deployments)) {
            throw new Error("Invalid response format");
        }

        const deploymentsContainer = document.getElementById('deployments');
        deploymentsContainer.innerHTML = '';  // Clear the container

        // Durchlaufe die Deployments und füge sie zur HTML-Struktur hinzu
        data.deployments.forEach(deployment => {
            const div = document.createElement('div');
            div.className = 'deployment-item';
            div.innerHTML = `
                <strong>Name:</strong> ${deployment.name} <br>
                <strong>DNS Name:</strong> ${deployment.dns_name} <br>
                <strong>Repo:</strong> ${deployment.repo} <br>
                <strong>Branch:</strong> ${deployment.branch} <br>
                <strong>Code Directory:</strong> ${deployment.code_dir} <br>
                <strong>Base Image:</strong> ${deployment.base_image} <br>
                <strong>Replicas:</strong> ${deployment.replicas} <br>
                <strong>CPU Limit:</strong> ${deployment.cpu_limit} <br>
                <strong>Memory Limit:</strong> ${deployment.memory_limit} <br>
                <button onclick="deleteDeployment('${deployment.dns_name}')">Delete</button>
                <button onclick="restartDeployment('${deployment.dns_name}')">Restart</button>
            `;
            deploymentsContainer.appendChild(div);
        });
    } catch (error) {
        alert("Error fetching deployments: " + error.message);
    }
}


// Function to delete a deployment
async function deleteDeployment(name) {
    try {
        await fetch(apiBaseUrl + `deployments/${name}`, { method: 'DELETE' });
        fetchDeployments();
    } catch (error) {
        alert("Error deleting deployment: " + error.message);
    }
}

// Function to restart a deployment
async function restartDeployment(name) {
    try {
        await fetch(apiBaseUrl + `deployments/${name}/restart`, { method: 'POST' });
        fetchDeployments();
    } catch (error) {
        alert("Error restarting deployment: " + error.message);
    }
}

// Fetch deployments on page load
window.onload = fetchDeployments;
