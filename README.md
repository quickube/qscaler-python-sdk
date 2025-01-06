# QScaler-SDK

Python SDK for integration with QScaler, a Kubernetes-native queue worker autoscaler.

## Overview

QScaler-SDK enables efficient scaling of queue workers in a Kubernetes environment. It works by monitoring changes in the `QWORKER_NAME` Custom Resource Definition (CRD) managed by the QScaler controller. 

### Key Features
- Automatically detects changes in desired replica counts or pod specifications.
- Gracefully shuts down when necessary to ensure smooth scaling and resource optimization.
- Continuously loops to process tasks unless a change is detected.

## How It Works

1. **Monitor Changes**: The worker watches the `QWORKER_NAME` CRD for updates.
2. **Trigger Actions**: 
   - If a change in the desired replica count or pod specification hash is detected:
     - The worker removes its owner reference.
     - Initiates a graceful shutdown process.
   - If no changes are detected, the worker:
     - Continues running indefinitely.
     - Periodically checks for differences at intervals defined by `MESSAGE_TIMEOUT`.
3. **Task Processing**: During each loop, the worker processes tasks unless a termination condition is met.

## Setup

To use QScaler-SDK, configure the following environment variables:

### Environment Variables

| Variable           | Description                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------|
| `QWORKER_NAME`     | Name of the QWorker CRD to monitor.                                                          |
| `PULLING_INTERVAL` | Interval (in seconds) for checking the QWorker CRD status when no tasks are running.          |
| `POD_SPEC_HASH`    | Hash of the current pod specification. Used to detect changes in the CRD and trigger shutdown.|
| `HOSTNAME`         | Name of the pod, automatically set by Kubernetes.                                            |

## Example

A complete example is provided in the `example` folder, including the following files:

### [`worker.py`](./example/worker.py)
### [`qworker.yaml`](./example/qworker.yaml)