pipeline {
    agent { kubernetes
        {
            label 'master'
            image 'python:3.8.5-alpine3.11'
        }
    }
    stages {
        stage('Build'){
            steps {
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
            }
        }
        stage('Test') {
            steps {
                sh 'python -m unittest'
            }
        }
    }
}