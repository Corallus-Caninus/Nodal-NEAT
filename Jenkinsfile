pipeline {
    agent{
        kubernetes { }
    }
    stages {
        stage('Build'){
            container('python') {
                steps {
                    sh 'pip install graphviz'
                    sh 'pip install matplotlib'
                }
            }
        }
        stage('Test') {
            container('python') {
                steps {
                    sh 'python -m unittest'
                }
            }
        }
    }
}