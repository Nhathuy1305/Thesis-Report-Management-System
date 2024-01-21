pipeline {

    // agent {label 'Jenkins-Agent'}

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
                        sh "docker rmi daniel135dang/${service}:latest"
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