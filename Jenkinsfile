pipeline {
    agent{
        kubernetes { }
    }
    stages {
        container('python') {
            stage('Build'){
                steps {
                    sh 'pip install graphviz'
                    sh 'pip install matplotlib'
                }
            }
        }
        container('python') {
            stage('Test') {
                steps {
                    sh 'python -m unittest'
                }
            }
        }
    }
}