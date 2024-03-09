pipeline {

    agent any

    tools {
        jdk 'jdk17'
        nodejs 'node21'
    }

    environment {
        RELEASE_VERSION = '1.0.0'
        SCANNER_HOME = tool 'sonar-scanner'
        IMAGE_TAG = "${RELEASE_VERSION}-${env.BUILD_NUMBER}"
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

        // stage("Sonarqube Analysis") {
        //     steps {
        //         withSonarQubeEnv('SonarQube-Server') {
        //             sh """
        //             ${SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectName=Thesis-Report-Management-CI \
        //             -Dsonar.projectKey=Thesis-Report-Management-CI
        //             """
        //         }
        //     }
        // }

        // stage("Quality Gate") {
        //     steps {
        //         script {
        //             waitForQualityGate abortPipeline: false, credentialsId: 'SonarQube-Token'
        //         }
        //     }
        // }

        // stage('TRIVY FS SCAN') {
        //     steps {
        //         sh "trivy fs . > trivyfs.txt"
        //      }
        //  }

        // stage('Build & Push Docker Images') {
        //     steps {
        //         script {
        //             // Get a list of all directories in the current workspace
        //             def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
        //             // Split the output into a list of directories
        //             def services = output.split("\n").collect { it.replace("./", "") }

        //             // List of directories to exclude
        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.']

        //             for (service in services) {

        //                 // Skip the current iteration if the service is in the exclude list
        //                 if (excludeServices.contains(service)) {
        //                     continue
        //                 }
                        
        //                 def imageName = "daniel135dang/${service}"

        //                 def builtImage = docker.build(imageName, "./${service}")

        //                 withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
        //                     builtImage.tag("${IMAGE_TAG}")

        //                     docker.image("${imageName}:${IMAGE_TAG}").push()

        //                     builtImage.tag("latest")
        //                     docker.image("${imageName}:latest").push()
        //                 }
        //             }
        //         }
        //     }
        // }

        // stage('Trivy Scan') {
        //     steps {
        //         script {
        //             def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
        //             def services = output.split("\n").collect { it.replace("./", "") }

        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.']

        //             for (service in services) {
        //                 if (excludeServices.contains(service)) {
        //                     continue
        //                 }

        //                 sh ("""
        //                     docker run \
        //                     -v /var/run/docker.sock:/var/run/docker.sock \
        //                     aquasec/trivy \
        //                     image daniel135dang/${service}:${IMAGE_TAG} \
        //                     --no-progress \
        //                     --scanners vuln \
        //                     --exit-code 0 \
        //                     --severity HIGH,CRITICAL \
        //                     --format table
        //                 """)
        //             }
        //         }
        //     }
        // }

     
        stage('Cleanup Artifacts') {
            steps {
                script {
                    def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
                    def services = output.split("\n").collect { it.replace("./", "") }

                    def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.']

                    for (service in services) {
                        if (excludeServices.contains(service)) {
                            continue
                        }
                        
                        sh "docker rmi daniel135dang/${service}:${IMAGE_TAG}"
                        sh "docker rmi daniel135dang/${service}:latest"
                    }
                }
            }
        }

        stage('Update CD Repository') {
            steps {
                script {
                    withCredentials([gitUsernamePassword(credentialsId: 'github', gitToolName: 'Default')]) {
                        sh "git clone https://github.com/Nhathuy1305/Thesis-Report-Management-System-CD.git cd-job"
                    }

                    dir("cd-job") {
                        sh "git pull origin master"
                    }
                    
                    def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
                    def services = output.split("\n").collect { it.replace("./", "") }

                    def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.']

                    sh "echo '' > services.txt"

                    for (service in services) {
                        if (excludeServices.contains(service)) {
                            continue
                        }
                        
                        sh "echo '${service}' >> services.txt"
                    }

                    sh """
                        git config --global user.email "ITITIU20043@student.hcmiu.edu.vn"
                        git config --global user.name "Nhathuy1305"
                        git add services.txt
                        git commit -m "Update services.txt"
                    """
                    withCredentials([gitUsernamePassword(credentialsId: 'github', gitToolName: 'Default')]) {
                        sh "git push https://github.com/Nhathuy1305/Thesis-Report-Management-System-CD.git master"
                    }
                }
            }
        }

        stage('Trigger CD Pipeline') {
            steps {
                script {
                    sh """
                        curl -v -k --user danielmaster:${JENKINS_API_TOKEN} \
                        -X POST -H 'cache-control: no-cache' \
                        -H 'content-type: application/x-www-form-urlencoded' \
                        --data 'IMAGE_TAG=${IMAGE_TAG}' \
                        'http://localhost:8080/job/thesis-report-management-cd/buildWithParameters?token=gitops-token'
                    """                
                }
            }
        }
    }
    
    post {
        always {
            node('') {
                script {
                    sh "rm -rf cd-job"
                }
            }
            
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