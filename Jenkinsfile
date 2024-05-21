pipeline {

    agent any

    tools {
        jdk 'jdk17'
        nodejs 'node18'
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

        stage("Sonarqube Analysis") {
            steps {
                withSonarQubeEnv('SonarQube-Server') {
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectName=Thesis-Report-Management-CI \
                    -Dsonar.projectKey=Thesis-Report-Management-CI
                    """
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

        stage('Install Dependencies') {
            steps {
                dir('client') {
                    sh "npm install"
                }
            }
        }
        stage('TRIVY FS SCAN') {
            steps {
                sh "trivy fs . > trivyfs.txt"
             }
         }

        // stage('Build & Push Docker Images') {
        //     steps {
        //         script {
        //             // Get a list of all directories in the current workspace
        //             def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
        //             // Split the output into a list of directories
        //             def services = output.split("\n").collect { it.replace("./", "") }

        //             // List of directories to exclude
        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.', '.idea', '.scannerwork']

        //             for (service in services) {

        //                 // Skip the current iteration if the service is in the exclude list
        //                 if (excludeServices.contains(service)) {
        //                     continue
        //                 }

        //                 echo "Processing service: ${service}"
                        
        //                 def imageName = "daniel135dang/${service}"

        //                 def builtImage = docker.build(imageName, "./${service}")

        //                 withDockerRegistry(credentialsId: 'dockerhub', url: 'https://index.docker.io/v1/') {
        //                     builtImage.tag("${IMAGE_TAG}")

        //                     docker.image("${imageName}:${IMAGE_TAG}").push()

        //                     // builtImage.tag("latest")
        //                     // docker.image("${imageName}:latest").push()
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

        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.', '.idea', '.scannerwork']

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

        //                 sh ("""
        //                     docker run --rm \
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

     
        // stage('Cleanup Artifacts') {
        //     steps {
        //         script {
        //             def output = sh(script: "find . -maxdepth 1 -type d", returnStdout: true).trim()
                    
        //             def services = output.split("\n").collect { it.replace("./", "") }

        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.', '.idea', '.scannerwork']

        //             for (service in services) {
        //                 if (excludeServices.contains(service)) {
        //                     continue
        //                 }
                        
        //                 sh "docker rmi daniel135dang/${service}:${IMAGE_TAG}"
        //                 // sh "docker rmi daniel135dang/${service}:latest"
        //             }
        //         }
        //     }
        // }

        // stage('Update CD Repository') {
        //     steps {
        //         script {
        //             def ciRepo = 'https://github.com/Nhathuy1305/Thesis-Report-Management-System-CI'
        //             def cdRepo = 'https://github.com/Nhathuy1305/Thesis-Report-Management-System-CD'
        //             def credentialsId = 'github'
        //             def gitToolName = 'Default'
        //             def excludeServices = ['rabbitmq', 'readme_images', 'requirements', '.git', '.idea', '.scannerwork', '.gitignore', 'client', 'rest', 'postgresql']

        //             withCredentials([gitUsernamePassword(credentialsId: credentialsId, gitToolName: gitToolName)]) {
        //                 sh "git clone ${ciRepo} ci-job"
        //                 def ciServicesOutput = sh(script: "find ci-job/* -maxdepth 0 -type d", returnStdout: true).trim()
        //                 def ciServices = ciServicesOutput.split("\n").collect { it.replace("ci-job/", "") }.findAll { !excludeServices.contains(it) }

        //                 sh "git clone ${cdRepo} cd-job"
        //                 def cdServices = readFile('cd-job/service_update/services.txt').split("\n")
        //                 def removedServicesList = readFile('cd-job/service_update/service_removed.txt').split("\n")

        //                 // Compare the two lists of services
        //                 def newServices = ciServices.findAll { !cdServices.contains(it) }
        //                 def removedServices = cdServices.findAll { !ciServices.contains(it) }

        //                 // If there are differences, update services.txt and service_removed.txt, and commit the changes
        //                 if (newServices || removedServices) {
        //                     dir('cd-job/service_update') {
        //                         newServices.each { 
        //                             sh "echo '${it}' >> services.txt" 
        //                             if (removedServicesList.contains(it)) {
        //                                 sh "sed -i '/${it}/d' service_removed.txt" // Remove the service from service_removed.txt if it is added back
        //                             }
        //                         }
        //                         removedServices.each { 
        //                             sh "sed -i '/${it}/d' services.txt" 
        //                             sh "echo '${it}' >> service_removed.txt" // Write removed services to service_removed.txt
        //                         }

        //                         sh """
        //                             git status
        //                             git config --global user.email "ITITIU20043@student.hcmiu.edu.vn"
        //                             git config --global user.name "Nhathuy1305"
        //                             git add services.txt service_removed.txt
        //                             git commit -m "Update services.txt and service_removed.txt"
        //                             git push
        //                         """
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }

        // todo
        // CHO NAY NHO THAY DOI USER KHI CHUYEN SANG CLOUD
    //     stage('Trigger CD Pipeline') {
    //         steps {
    //             script {
    //                 sh """
    //                     curl -v -k --user daniel:${JENKINS_API_TOKEN} \
    //                     -X POST -H 'cache-control: no-cache' \
    //                     -H 'content-type: application/x-www-form-urlencoded' \
    //                     --data 'IMAGE_TAG=${IMAGE_TAG}' \
    //                     'http://localhost:8080/job/thesis-report-management-cd/buildWithParameters?token=gitops-token'
    //                 """                
    //             }
    //         }
    //     }
    // }
    
    // post {
    //     always {
    //         node('') {
    //             script {
    //                 sh "rm -rf cd-job"
    //                 sh "rm -rf ci-job"
    //                 }
    //             }
            
    //         emailext attachLog: true,
    //             subject: "'${currentBuild.result}'",
    //             body: "Project: ${env.JOB_NAME}<br/>" +
    //                 "Build Number: ${env.BUILD_NUMBER}<br/>" +
    //                 "URL: ${env.BUILD_URL}<br/>",
    //             to: 'dnhuy.ityu@gmail.com',                              
    //             attachmentsPattern: 'trivyfs.txt,trivyimage.txt'
    //     }
    }
}