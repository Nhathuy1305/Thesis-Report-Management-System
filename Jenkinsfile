pipeline {

    agent {label 'Jenkins-Agent'}

    environment {
        RABBITMQ_HOST = 'daniel-rabbitmq'
        RABBITMQ_USER = 'guest'
        RABBITMQ_PASSWORD = credentials('rabbitmq-password')
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = credentials('postgres-password')
        POSTGRES_DB = 'thesis_upload'
        SONARQUBE_SCANNER_HOME = tool 'sonarqube-scanner'
    }

    stages {

        stage('Cleanup Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout from SCM') {
            steps {
                git branch: 'master', credentialsId: 'github', url: 'https://github.com/Nhathuy1305/Thesis-Report-Management-System.git'
            }
        }

        ///// Dang co loi, khong tim thay file requirements.txt

        // stage('Build and Test') {
        //     steps {
        //         sh 'sudo apt-get update && sudo apt-get install -y python3-pip'

        //         script {
        //             def python_services = [
        //                 'chapter_summarization',
        //                 'chapter_title',
        //                 'format_check',
        //                 'page_count',
        //                 'table_of_content',
        //                 'word_frequency',
        //                 'citation',
        //                 'table_figure_detection',
        //             ]

        //             def node_services = [
        //                 'client',
        //                 'rest',
        //             ]

        //             for (service in python_services) {
        //                 sh "cd ${service}"
        //                 sh "pip install -r requirements.txt"

        //                 if (service == 'chapter_summarization') {
        //                     sh "python3 -m nltk.downloader punkt"
        //                 }
                        
        //                 sh "python3 test.py"
        //             }

        //             for (service in node_services) {
        //                 sh "cd ${service} && npm install && npm test"
        //             }
        //         }
        //     }
        // }


        stage('SonarQube Analysis') {
            def scannerHome = tool 'SonarScanner';
            withSonarQubeEnv() {
                sh "${scannerHome}/bin/sonar-scanner"
            }
        }


        stage("Quality Gate"){
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'jenkins-sonarqube-token'
                }	
            }
        }

        stage('Building and Pushing Docker Images') {
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
                        'citation',
                        'table_figure_detection',
                    ]

                    for (service in services) {
                        // Build and push Docker image for each service
                        docker.build("daniel135dang/${service}:latest", "./${service}")
                        withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
                            docker.image("daniel135dang/${service}:latest").push()
                        }
                    }
                }
            }
        }

        stage('Trivy Scan') {
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
                        'citation',
                        'table_figure_detection',
                    ]

                    for (service in services) {
                        sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v \${PWD}:/root/ aquasec/trivy:0.18.3 image --severity HIGH,CRITICAL daniel135dang/${service}:latest"                    }
                }
            }
        }

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

        // stage('Deploy Microservices to DEV') {
        //     steps {
        //         script {
        //             def services = [
        //                 'postgresql',
        //                 'rest',
        //                 'client',
        //                 'chapter_summarization',
        //                 'chapter_title',
        //                 'format_check',
        //                 'page_count',
        //                 'table_of_content',
        //                 'word_frequency',
        //                 'citation',
        //                 'table_figure_detection',
        //             ]

        //             sh 'docker network create dev-network || true'

        //             for (service in services) {
        //                 // Remove existing container with the same name
        //                 sh "docker rm -f ${service}-dev || true"
        //                 // Deploy each service to DEV environment in separate Docker containers
        //                 if (service == 'postgresql') {
        //                     sh "docker run -d --name ${service}-dev --network dev-network --env POSTGRES_USER=${POSTGRES_USER} --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} --env POSTGRES_DB=${POSTGRES_DB} -v postgresql-data:/var/lib/postgresql/data daniel135dang/${service}:latest"
        //                 } else {
        //                     sh "docker run -d --name ${service}-dev --network dev-network --env RABBITMQ_HOST=${RABBITMQ_HOST} --env RABBITMQ_USER=${RABBITMQ_USER} --env RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD} --env POSTGRES_USER=${POSTGRES_USER} --env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} --env POSTGRES_DB=${POSTGRES_DB} daniel135dang/${service}:latest"
        //                 }
        //             }
        //         }
        //     }
        // }
     
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
                        'citation',
                        'table_figure_detection',
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