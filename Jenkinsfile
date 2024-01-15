pipeline {

    agent {label 'Jenkins-Agent'}

    environment {
        RELEASE_VERSION = '1.0.0'
        IMAGE_TAG = "${RELEASE_VERSION}-${env.BUILD_NUMBER}"
        RABBITMQ_HOST = 'daniel-rabbitmq'
        RABBITMQ_USER = 'guest'
        RABBITMQ_PASSWORD = credentials('rabbitmq-password')
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = credentials('postgres-password')
        POSTGRES_DB = 'thesis_upload'
        JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN")
    }

    stages {

        stage('Cleanup Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout from SCM') {
            steps {
                git branch: 'master', credentialsId: 'github', url: 'https://github.com/Nhathuy1305/Thesis-Report-Management-System'
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

        stage('Build & Push Docker Images') {
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
                        def imageName = "daniel135dang/${service}"

                        def builtImage = docker.build(imageName, "./${service}")

                        withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
                            builtImage.tag("${IMAGE_TAG}")

                            docker.image("${imageName}:${IMAGE_TAG}").push()

                            builtImage.tag("latest")
                            docker.image("${imageName}:latest").push()
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
                        sh ("docker run -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image daniel135dang/${service}:latest --no-progress --scanners vuln  --exit-code 0 --severity HIGH,CRITICAL --format table")
                    }
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
     
        stage('Cleanup Artifacts') {
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
                        sh "docker rmi daniel135dang/${service}:${IMAGE_TAG}"
                        sh "docker rmi danieldang/${service}:latest"
                    }
                }
            }
        }

        stage('Trigger CD Pipeline') {
            steps {
                script {
                        sh "curl -v -k --user danielmaster:${JENKINS_API_TOKEN} -X POST -H 'cache-control: no-cache' -H 'content-type: application/x-www-form-urlencoded' --data 'IMAGE_TAG=${IMAGE_TAG}' 'ec2-13-250-58-123.ap-southeast-1.compute.amazonaws.com:8080/job/thesis-report-management-cd/buildWithParameters?token=thesis-token'"
                }
            }
        }
    }
    
    post {
       failure {
             emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                      subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Failed", 
                      mimeType: 'text/html',to: "huyngnht1305@gmail.com"
      }
      success {
            emailext body: '''${SCRIPT, template="groovy-html.template"}''', 
                     subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - Successful", 
                     mimeType: 'text/html',to: "huyngnht1305@gmail.com"
      }      
   }
}