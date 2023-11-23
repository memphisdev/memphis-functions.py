def gitBranch = env.BRANCH_NAME
def gitURL = "git@github.com:Memphisdev/memphis.py.git"
def repoUrlPrefix = "memphisos"

node ("small-ec2-fleet") {
  git credentialsId: 'main-github', url: gitURL, branch: gitBranch
	
  if (env.BRANCH_NAME ==~ /(master)/) { 
    versionTag = readFile "./version-beta.conf"
  }
  else {
    versionTag = readFile "./version.conf"
  }
	
  try{
    
    stage('Install twine') {
      sh """
        pip3 install twine
        python3 -m pip install urllib3==1.26.6
      """
    }
    
    stage('Deploy to pypi') {
			if (env.BRANCH_NAME ==~ /(master)/) {
				sh """
				  sed -i -r "s/memphis-py/memphis-py-beta/g" setup.py
			  """
			}
		  sh """
			  sed -i -r "s/version=\\"[0-9].[0-9].[0-9]/version=\\"$versionTag/g" setup.py
        sed -i -r "s/[0-9].[0-9].[0-9].tar.gz/$versionTag\\.tar.gz/g" setup.py
				python3 setup.py sdist
			"""
			withCredentials([usernamePassword(credentialsId: 'python_sdk', usernameVariable: 'USR', passwordVariable: 'PSW')]) {
        sh '/home/ec2-user/.local/bin/twine upload -u $USR -p $PSW dist/*'
      }
		}
	  
		if (env.BRANCH_NAME ==~ /(latest)/) {
      stage('Checkout to version branch'){
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


    notifySuccessful()

  } catch (e) {
      currentBuild.result = "FAILED"
      cleanWs()
      notifyFailed()
      throw e
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
