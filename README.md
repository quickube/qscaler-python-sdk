# Gamba
Gamba is a python package to use with QScaler for an easy server-worker setup using the QScaler autoscaler 

## Overview
some stuff to be written here...

## Problem Statement
some stuff to be written here...

## How It Works
worker/client [example here](./examples)
* **Client**: will send jobs to work queue waiting for worker to resolve them
* **Worker**: take jobs from queue and will gracefully die when requested


## Setup
# ENV-VARS:
### Storage
* `STORAGE: currently supporting only redis`
* `STORAGE_HOST: storage client host`
* `STORAGE_PORT: storage client port`
* `STORAGE_PASSWORD: storage client password`
* `STORAGE_DB: storage type db (only for redis)`
### broker
* `BROKER: currently supporting only redis`
* `BROKER_HOST: queue broker host`
* `BROKER_PORT: queue broker port`
* `BROKER_PASSWORD: queue broker password`
* `BROKER_DB: queue broker db (only for redis)`
 
