pipeline {
  agent none
  stages {
    stage('LoadingModule') {
      agent {
        docker {
          image 'naveen462/pyenv6:first'
        }
      }
      steps {
        sh 'python master.py -p omnia -v 02.01.04-DEVEL.3716.5bebe5e3 -b ./build -m full'
      }
    }
    stage('Testing'){
      echo "not yet defined"
    }
    stage('Report'){
      echo "not yet defined
    }
    stage('Merging'){
      echo "not yet defined"
    }
  }
}
