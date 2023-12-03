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

        stage('Deploy PostgreSQL to DEV') {
            steps {
                echo 'Deploying PostgreSQL and cleaning up'
                sh 'docker image pull postgres:latest'
                sh 'docker network create dev || echo "Network already exists"'
                sh 'docker container stop daniel-postgres || echo "Container does not exist"'
                sh 'echo y | docker container prune'
                sh 'docker volume rm daniel-postgres-data || echo "No volume to remove"'

                sh '''
                    docker run --name daniel-postgres --rm \
                    --network dev \
                    -v daniel-postgres-data:/var/lib/postgresql/data \
                    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
                    -e POSTGRES_USER=${POSTGRES_USER} \
                    -e POSTGRES_DB=${POSTGRES_DB} \
                    -d postgres:latest
                '''
                sh 'sleep 20'

                sh 'docker exec -i daniel-postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f postgresql/init.sql'
            }
        }

        stage('Deploy Microservices to DEV') {
            steps {
                script {
                    def services = [
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
                        // Deploy each service to DEV environment in separate Docker containers
                        sh "docker run -d --name ${service}-dev --env RABBITMQ_HOST=${RABBITMQ_HOST} --env RABBITMQ_USER=${RABBITMQ_USER} --env RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD} --env POSTGRES_USER=${POSTGRES_USER} --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} --env POSTGRES_DB=${POSTGRES_DB} daniel135dang/${service}:${BUILD_NUMBER}"
                    }
                }
            }
        }
     
        stage('Cleanup') {
            steps {
                script {
                    def services = [
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

                    sh "docker-compose -f docker-compose.dev.yml down"
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