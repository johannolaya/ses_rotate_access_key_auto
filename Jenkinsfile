pipeline {
    parameters {
        string(defaultValue: 'sender@email.com', name: 'SENDER_TEST', trim: true)
        string(defaultValue: 'recipient@email.com', name: 'RECIPIENT_TEST', trim: true)
    }

    stages {
        stage('Install Dependencies') {
            steps {
                dir('ses-key-rotation') {
                    sh "pip install -r requirements.txt"                                            
                }
            }
        }
        stage('SES-Rotate-Access-key') {
            steps {
                dir('ses-key-rotation') {
                    sh "python3 main.py --sender-test ${params.SENDER_TEST} --recipient-test ${params.RECIPIENT_TEST}"
                }
            }
        }
    }
}