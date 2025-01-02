# QScaler-SDK
qscaler-sdk is a python package to use with QScaler for an easy server-worker setup using the QScaler autoscaler 

## Overview
Worker python SDK for Qscale, able to setup a graceful shutdown method and a work method.

## How It Works
* The worker will watch the qworker crd given by `QWORKER_NAME` 
* once detected change in desired replicas and current, if diff is negative. it will remove its owner ref and start a graceful shutdown procedure
* other wise will continue looping forever, each `MESSAGE_TIMEOUT` check for diff then run work 

## Setup
### EnvVars:
* `QWORKER_NAME: qworker crd name`
* `MESSAGE_TIMEOUT: broker msg wait timeout, relevant for redis broker`
* `HOSTNAME: podname, autofilled by k8s`
* `K8S_API_GROUP: qworker api group; default "quickube.com"`
* `K8S_API_VERSION: qworker api version; default "v1alpha1"`
 
