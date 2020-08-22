podTemplate(containers: [
    containerTemplate(name: 'python', image: 'python:3.8.5-alpine3.12', ttyEnabled: true, command: 'cat'),
]) {
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