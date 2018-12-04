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
        sh 'cat config/omnia.ini'
        sh 'python master.py -p omnia -v 02.01.04-DEVEL.3716.5bebe5e3 -b ./build -m full > out.txt'
        script{
          buildPath = readFile('out.txt').trim()
        }
        echo "${buildPath}"
      }
    }
    stage('Testing'){
      steps{
      echo "not yet defined"
      }
    }
    stage('Report'){
      steps{
      echo "not yet defined"
      }
    }
    stage('Merging'){
      steps{
      echo "not yet defined"
      }
    }
  }
}
