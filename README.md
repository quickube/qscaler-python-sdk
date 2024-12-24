# QScaler-SDK
qscaler-sdk is a python package to use with QScaler for an easy server-worker setup using the QScaler autoscaler 

## Overview
some stuff to be written here...

## Problem Statement
some stuff to be written here...

## How It Works
* **Client**: will send jobs to work queue waiting for worker to resolve them
* **Worker**: take jobs from queue and will gracefully die when requested
<br/>worker/client example [here](./examples)


## Setup
# ENV-VARS:
### broker
* `BROKER: currently supporting only redis`
* `BROKER_HOST: queue broker host`
* `BROKER_PORT: queue broker port`
* `BROKER_PASSWORD: queue broker password`
* `BROKER_DB: queue broker db (only for redis)`
 
