pipeline {
    agent{
        kubernetes { }
    }
    stages {
        container('python'){
        stage('Build'){
                steps {
                    sh 'pip install graphviz'
                    sh 'pip install matplotlib'
                    }
                }
            }
            stage('Test') {
                steps {
                    sh 'python -m unittest'
                }
            }
        }
    }
}