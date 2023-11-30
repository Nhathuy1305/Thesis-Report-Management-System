pipeline {

    agent any

    environment {
        GOOGLE_CREDENTIALS = credentials('google-credentials')
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
                // Get the latest code from your source control
                checkout scm
            }
        }

        stage('Packaging/Pushing image') {
            steps {
                withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
                    sh 'docker build -t daniel135dang/thesis_manage .'
                    sh 'docker push daniel135dang/thesis_manage'
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                echo 'Deploying with Docker Compose'
                sh 'docker-compose up -d'
            }
        }

        // stage('Deploy PostgreSQL to DEV') {
        //     steps {
        //         echo 'Deploying PostgreSQL and cleaning up'
        //         sh 'docker image pull postgres:latest'
        //         sh 'docker network create dev || echo "Network already exists"'
        //         sh 'docker container stop daniel-postgres || echo "Container does not exist"'
        //         sh 'echo y | docker container prune'
        //         sh 'docker volume rm daniel-postgres-data || echo "No volume to remove"'

        //         sh '''
        //             docker run --name daniel-postgres --rm \
        //             --network dev \
        //             -v daniel-postgres-data:/var/lib/postgresql/data \
        //             -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
        //             -e POSTGRES_USER=${POSTGRES_USER} \
        //             -e POSTGRES_DB=${POSTGRES_DB} \
        //             -d postgres:latest
        //         '''
        //         sh 'sleep 20'

        //         sh 'docker exec -i daniel-postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f ./postgresql/init.sql'
        //     }
        // }
        
        // stage('Deploy RabbitMQ to DEV') {
        //     steps {
        //         echo 'Deploying RabbitMQ and cleaning up'
        //         sh 'docker image pull rabbitmq:3-management'
        //         sh 'docker network create dev || echo "Network already exists"'
        //         sh 'docker container stop daniel-rabbitmq || echo "Container does not exist"'
        //         sh 'echo y | docker container prune'

        //         sh '''
        //             docker run --name daniel-rabbitmq --rm \
        //             --network dev \
        //             -p 5672:5672 \
        //             -p 15672:15672 \
        //             -e RABBITMQ_DEFAULT_USER=${RABBITMQ_USER} \
        //             -e RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD} \
        //             -d rabbitmq:3-management
        //         '''

        //         // Wait for RabbitMQ to initialize
        //         sh 'sleep 20'
        //     }
        // }

        // stage('Upload to GCP Cloud Storage') {
        //     steps {
        //         // Upload artifacts to GCP Cloud Storage
        //         script {
        //             sh "gsutil cp -r ./requirements gs://${GCP_BUCKET_NAME}/"
        //         }
        //     }
        // }

        stage('Deploy Application to DEV') {
            steps {
                echo 'Deploying and cleaning'
                sh 'docker image pull daniel135dang/thesis_manage'
                sh 'docker container stop daniel-thesis || echo "this container does not exist" '
                sh 'docker network create dev || echo "this network exists"'
                sh 'echo y | docker container prune '

                sh 'docker container run -d --rm --name daniel-thesis -p 8081:8080 --network dev daniel135dang/thesis_manage'
            }
        }
 
    }
    
    post {
        // Clean after build
        always {
            sh "docker-compose -f ./docker-compose.yml down"
            cleanWs()
        }
    }
}