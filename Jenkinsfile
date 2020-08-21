pipeline {
    agent { docker
        {
            label 'master'
            image 'python:3.8.5-alpine3.11'
        }
    }
    stages {
        stage('build'){
            steps {
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
            }
        }
        stage('test') {
            steps {
                sh 'python -m unittest'
            }
        }
    }
}