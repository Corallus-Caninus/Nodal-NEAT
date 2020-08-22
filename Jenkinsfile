podTemplate(containers: [
    containerTemplate(name: 'python', image: 'python:3.8.5-slim-buster', ttyEnabled: true, command: 'cat'),
]) {
    //TODO: scale out unittests on several pods. some will be for complexification evaluation.
    node(POD_LABEL) {
        container('python') {
            stage('Build') {
                //TODO: this is bloat. might as well use larger alpine image
                //TODO: move this into docker image. Jenkins doesnt have
                //      layered multistage build.
                //git 'https://github.com/Corallus-Caninus/Nodal_NEAT.git' .
                sh 'apt update'
                sh 'apt install git -y'
                sh 'git clone https://github.com/Corallus-Caninus/Nodal_NEAT.git Nodal_NEAT'
                sh 'apt install build-essential -y'
                //TODO: this should be handled in setup.py
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
                sh 'pip install ./Nodal_NEAT'
            }
        }
        container('python') {
            stage('Test') {
                sh 'python -m unittest ./Nodal_NEAT'
            }
        }
    }
}