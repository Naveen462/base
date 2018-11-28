pipeline {
  agent none
  stages {
    stage('Build') {
      agent {
        docker {
          image 'naveen462/pyenv6:first'
        }
      }
      steps {
        sh 'python master.py -p omnia -v 02.01.04-DEVEL.3716.5bebe5e3 -b ./build -m full'
      }
    }
    stage('Test') {
      agent {
        docker {
          image 'qnib/pytest'
        }

      }
      post {
        always {
          junit 'test-reports/results.xml'

        }

      }
      steps {
        sh 'py.test --verbose --junit-xml test-reports/results.xml sources/test_calc.py'
      }
    }
    stage('Deliver') {
      agent {
        docker {
          image 'cdrx/pyinstaller-linux:python2'
        }

      }
      post {
        success {
          archiveArtifacts 'dist/add2vals'

        }

      }
      steps {
        sh 'pyinstaller --onefile sources/add2vals.py'
      }
    }
  }
}
