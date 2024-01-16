pipeline {

    agent {label 'Jenkins-Agent'}

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

        stage('Update the Deployment Tags') {
            steps {
                script {
                    def services = [
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
                        sh """
                            cd kubernetes
                            cat ${service}-deployment.yaml
                            sed -i 's|daniel135dang/${service}:.*|daniel135dang/${service}:${IMAGE_TAG}|g' ${service}-deployment.yaml
                            cat ${service}-deployment.yaml
                        """
                    }
                }
            }
        }

        stage('Push the changed deployment file to Git') {
            steps {
                script {
                    def services = [
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
                        sh """
                            cd kubernetes
                            git config --global user.name "Nhathuy1305"
                            git config --global user.email "ITITIU20043@student.hcmiu.edu.vn"
                            git add ${service}-deployment.yaml
                            git commit -m "Updated Deployment Manifest"
                        """
                        withCredentials([gitUsernamePassword(credentialsId: 'github', gitToolName: 'Default')]) {
                            sh "git push https://github.com/Nhathuy1305/Thesis-Report-Management-Syste, master"
                        }
                    }
                }
            }
        }
    }
}