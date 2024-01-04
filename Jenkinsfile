def versionTag
pipeline {
  environment {
    gitBranch = "${env.BRANCH_NAME}"
    gitURL = "git@github.com:Memphisdev/memphis-functions.py.git"
    repoUrlPrefix = "memphisos"
  }

  agent {
    label 'memphis-jenkins-small-fleet-agent'
  }

  stages {
    stage ('Connect GIT repository') {
      steps {
        git credentialsId: 'main-github', url: "git@github.com:Memphisdev/memphis-functions.py.git", branch: "${env.gitBranch}" 
      }
    }

    stage('Define version - BETA') {
      when {branch 'change-jenkins-agent'}
      steps {
        script {
          versionTag = readFile('./version-beta.conf')
          sh """
            sed -i -r "s/\\"memphis-functions/\\"memphis-functions-beta/g" setup.py
          """
        }
      }
    }
    stage('Define version - LATEST') {
      when {branch 'latest'}
      steps {
        script {
          versionTag = readFile('./version.conf')
        }
      }
    }

    stage('Install twine') {
      steps {
        sh """
          pip3 install twine
          python3 -m pip install urllib3==1.26.6
        """
      }
    }

    stage('Deploy to PyPi') {
      steps {
        sh """
			    sed -i -r "s/version=\\"[0-9].[0-9].[0-9]/version=\\"$versionTag/g" setup.py
          sed -i -r "s/[0-9].[0-9].[0-9].tar.gz/$versionTag\\.tar.gz/g" setup.py
			  	python3 setup.py sdist
			  """
			  withCredentials([usernamePassword(credentialsId: 'python_sdk', usernameVariable: 'USR', passwordVariable: 'PSW')]) {
          sh """
            ~/.local/bin/twine upload -u $USR -p $PSW dist/*
          """
        }
      }
    }

    stage('Checkout to version branch') {
      when {branch 'latest'}
      steps {
        sh """
	        sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo -y
          sudo dnf install gh -y
        """
        withCredentials([sshUserPrivateKey(keyFileVariable:'check',credentialsId: 'main-github')]) {
          sh """
            GIT_SSH_COMMAND='ssh -i $check' git checkout -b $versionTag
            GIT_SSH_COMMAND='ssh -i $check' git push --set-upstream origin $versionTag
	        """
        }
        withCredentials([string(credentialsId: 'gh_token', variable: 'GH_TOKEN')]) {
          sh """
					  gh release create $versionTag --generate-notes
					"""
        }
      }
    }
  }
  post {
    always {
      cleanWs()
    }
    success {
      notifySuccessful()
    }
    failure {
      notifyFailed()
    }
  }
}
  



def notifySuccessful() {
  emailext (
      subject: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
      body: """<p>SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
        <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
      recipientProviders: [[$class: 'DevelopersRecipientProvider']]
    )
}

def notifyFailed() {
  emailext (
      subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
      body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
        <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
      recipientProviders: [[$class: 'DevelopersRecipientProvider']]
    )
}
