podTemplate(containers: [
    containerTemplate(name: 'python', image: 'python:3.8.5-slim-buster', ttyEnabled: true, command: 'cat'),
]) {
    node(POD_LABEL) {
        container('python') {
            stage('Build') {
                //TODO: this is bloat. might as well use larger alpine image
                //TODO: move this into docker image. Jenkins doesnt have
                //      layered multistage build.
                sh 'ls'
                sh 'git clone https://github.com/Corallus-Caninus/Nodal_NEAT.git'
                sh 'cd Nodal_NEAT'
                sh 'apt update'
                sh 'apt install build-essential -y'
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
                sh 'pip install .'
            }
        }
        container('python') {
            stage('Test') {
                sh 'python -m unittest'
            }
        }
    }
}