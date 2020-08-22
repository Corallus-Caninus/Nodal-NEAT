podTemplate(containers: [
    containerTemplate(name: 'python', image: 'python:3.8.5-alpine3.12', ttyEnabled: true, command: 'cat'),
]) {
    node(POD_LABEL) {
        container('python') {
            stage('Build') {
                //TODO: this is bloat. might as well use larger alpine image
                //TODO: move this into docker image. Jenkins doesnt have
                //      layered multistage build.
                sh 'apk add --update alpine-sdk'
                sh 'apk add zlib'
                sh 'pip install graphviz'
                sh 'pip install matplotlib'
            }
        }
        container('python') {
            stage('Test') {
                sh 'python -m unittest'
            }
        }
    }
}