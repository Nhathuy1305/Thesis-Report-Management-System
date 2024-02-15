pipeline {

    agent any

    tools {
        jdk 'jdk17'
        nodejs 'node21'
    }

    environment {
        RELEASE = '1.0.0'
        SCANNER_HOME = tool 'sonar-scanner'
        IMAGE_TAG = "${RELEASE_VERSION}-${env.BUILD_NUMBER}"
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

        stage("Sonarqube Analysis") {
            steps {
                withSonarQubeEnv('SonarQube-Server') {
                    sh '''$SCANNER_HOME/bin/sonar-scanner -Dsonar.projectName=Thesis-Report-Management-CI \
                    -Dsonar.projectKey=Thesis-Report-Management-CI'''
                }
            }
        }

        stage("Quality Gate") {
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'SonarQube-Token'
                }
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
                        'grammar',
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
                        'grammar',
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
                        'grammar',
                    ]

                    for (service in services) {
                        sh "docker rmi daniel135dang/${service}:${IMAGE_TAG}"
                        sh "docker rmi daniel135dang/${service}:latest"
                    }
                }
            }
        }

        // stage('Trigger CD Pipeline') {
        //     steps {
        //         script {
        //                 sh "curl -v -k --user danielmaster:${JENKINS_API_TOKEN} -X POST -H 'cache-control: no-cache' -H 'content-type: application/x-www-form-urlencoded' --data 'IMAGE_TAG=${IMAGE_TAG}' 'ec2-13-250-58-123.ap-southeast-1.compute.amazonaws.com:8080/job/thesis-report-management-cd/buildWithParameters?token=thesis-token'"
        //         }
        //     }
        // }
    }
    
    post {
        always {
           emailext attachLog: true,
               subject: "'${currentBuild.result}'",
               body: "Project: ${env.JOB_NAME}<br/>" +
                   "Build Number: ${env.BUILD_NUMBER}<br/>" +
                   "URL: ${env.BUILD_URL}<br/>",
               to: 'dnhuy.ityu@gmail.com',                              
               attachmentsPattern: 'trivyfs.txt,trivyimage.txt'
        }
    }
}