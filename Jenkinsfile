pipeline {

    agent any

    environment {
        RABBITMQ_HOST = 'daniel-rabbitmq'
        RABBITMQ_USER = 'guest'
        RABBITMQ_PASSWORD = credentials('rabbitmq-password')
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = credentials('postgres-password')
        POSTGRES_DB = 'thesis_upload'
    }

    stages {
        stage('Checkout') {
            steps {
                // Get the latest code from source control
                checkout scm
            }
        }

        stage('Packaging/Pushing Docker Images') {
            steps {
                script {
                    def services = [
                        'postgresql',
                        'rest',
                        'client',
                        'chapter_summarization',
                        'chapter_title',
                        'format_check',
                        'page_count',
                        'table_of_content',
                        'word_frequency',
                    ]

                    for (service in services) {
                        // Build and push Docker image for each service
                        docker.build("daniel135dang/${service}:${BUILD_NUMBER}", "./${service}")
                        withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
                            docker.image("daniel135dang/${service}:${BUILD_NUMBER}").push()
                        }
                    }
                }
            }
        }

        stage('Deploy RabbitMQ to DEV') {
            steps {
                echo 'Deploying RabbitMQ and cleaning up'
                sh 'docker image pull rabbitmq:3-management'
                sh 'docker network create dev || echo "Network already exists"'
                sh 'docker container stop daniel-rabbitmq || echo "Container does not exist"'
                sh 'echo y | docker container prune'

                sh '''
                    docker run --name daniel-rabbitmq --rm \
                    --network dev \
                    -p 5672:5672 \
                    -p 15672:15672 \
                    -e RABBITMQ_DEFAULT_USER=${RABBITMQ_USER} \
                    -e RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD} \
                    -d rabbitmq:3-management
                '''

                // Wait for RabbitMQ to initialize
                sh 'sleep 20'
            }
        }

        stage('Deploy Microservices to DEV') {
            steps {
                script {
                    def services = [
                        'postgresql',
                        'rest',
                        'client',
                        'chapter_summarization',
                        'chapter_title',
                        'format_check',
                        'page_count',
                        'table_of_content',
                        'word_frequency',
                    ]

                    sh 'docker network create dev-network || true'

                    for (service in services) {
                        // Remove existing container with the same name
                        sh "docker rm -f ${service}-dev || true"

                        // Deploy each service to DEV environment in separate Docker containers
                        if (service == 'postgresql') {
                            sh "docker run -d --name ${service}-dev --network dev-network --env POSTGRES_USER=${POSTGRES_USER} --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} --env POSTGRES_DB=${POSTGRES_DB} -v postgresql-data:/var/lib/postgresql/data daniel135dang/${service}:${BUILD_NUMBER}"
                        } else {
                            sh "docker run -d --name ${service}-dev --network dev-network --env RABBITMQ_HOST=postgresql-dev --env RABBITMQ_USER=${RABBITMQ_USER} --env RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD} --env POSTGRES_USER=${POSTGRES_USER} --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} --env POSTGRES_DB=${POSTGRES_DB} daniel135dang/${service}:${BUILD_NUMBER}"
                        }
                    }
                }
            }
        }
     
        stage('Cleanup') {
            steps {
                script {
                    def services = [
                        'postgresql',
                        'rest',
                        'chapter_summarization',
                        'chapter_title',
                        'client',
                        'format_check',
                        'page_count',
                        'table_of_content',
                        'word_frequency',
                    ]

                    for (service in services) {
                        sh "docker stop ${service}-dev"
                        sh "docker rm ${service}-dev"
                    }
                }
            }
        }
    }
    
    post {
        // Clean after build
        always {
            cleanWs()
        }
    }
}