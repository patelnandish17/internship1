pipeline {
    agent any

    environment {
        // Load the env file credential with ID 'ENV'
        ENV_FILE = credentials('ENV')
    }

    stages {
        stage('Initialize Environment') {
            steps {
                echo 'Preparing workspace and copying environment variables...'
                // Copy the secret file credential to .env in the workspace root and Lang graph folder
                powershell 'Copy-Item -Path $env:ENV_FILE -Destination .env -Force'
                powershell 'Copy-Item -Path $env:ENV_FILE -Destination "Lang graph\\.env" -Force'
            }
        }

        stage('Front-end Pipeline') {
            steps {
                echo 'Building and testing frontend...'
                // Install dependencies
                powershell 'npm ci'
                // Run validations/tests
                powershell 'npm run test'
                // Build application
                powershell 'npm run build'
                // Docker image creation
                powershell 'docker compose build frontend'
            }
        }

        stage('Back-end Pipeline') {
            steps {
                echo 'Building and testing backend...'
                // Recreate and run backend venv, pip install and run tests
                powershell '''
                    if (Test-Path "Lang graph\\venv") {
                        Remove-Item -Path "Lang graph\\venv" -Recurse -Force
                    }
                    python -m venv "Lang graph\\venv"
                    & "Lang graph\\venv\\Scripts\\pip" install -r "Lang graph\\requirements.txt" --default-timeout=100
                    & "Lang graph\\venv\\Scripts\\pytest" "Lang graph\\tests\\test_api.py" -v
                '''
                // Docker image creation
                powershell 'docker compose build backend'
            }
        }

        stage('Agentic Orchestration Pipeline') {
            steps {
                echo 'Starting multi-agent orchestration service...'
                // Service initialization
                powershell 'docker compose up -d'
                // Verification check: poll the health endpoint
                powershell '''
                    Start-Sleep -Seconds 15
                    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
                    Write-Output "Backend health check response: $response"
                    if ($response.status -ne "ok") {
                        throw "Backend health check failed!"
                    }
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed. Verifying running containers...'
            powershell 'docker ps'
        }
    }
}
