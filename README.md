# Distributed Locking Service
Distributed locking service is an intuitive REST based backend service, that enables synchronization of all the distributed processes in your network via simple HTTP calls.
Different processes can attain shared read and shared write locks. Every process acquires a lock with a certain timeout.
After the timeout, the process automatically releases the lock and adjusts the state of the lock accordingly.
This service has been implemented with Python and Fastapi. GCP's Datastore is used as the backend to store the state of the locks.


## Apis
1. **POST /v1/distributed_lock/{lock_id}(is_exclusive)**: Creates a lock in the db. The lock could be write exclusive(details below) or write shared.
2. **GET /v1/distributed_lock/{lock_id}**: Gets the lock from the db. To analyse the current state of the lock and the processes involved.
3. **PUT /v1/distributed_lock/{lock_id}/read-process/{process_id}(timeout_seconds)**: Adds the process to a certain lock as a reader in the list of readers.
4. **PUT /v1/distributed_lock/{lock_id}/write-process/{process_id}(timeout_seconds)**:Adds the process to a certain lock as a writer in a list of writers.This further has 2 use cases:
   1. If the write lock is write exclusive, meaning only one process can acquire the write lock at a time.
   2. If the write lock supports shared writes, meaning meaning multiple processes can acquire the lock to write. Note: This relies on the dev’s discretion to use this only when the underlying processes are modifying separate resources and there is no chance for a race condition on any underlying resources.
5. **DELETE /v1/distributed_lock/{lock_id}/read-process/{process_id}**: Deletes the read process from the lock and manages the state of the lock accordingly.
6. **DELETE /v1/distributed_lock/{lock_id}/write-process/{process_id}**: Deletes the write process from the lock and manages the state of the lock accordingly.

To test these apis out, you can simply deploy the service with steps below and access the api docs at [http://localhost:8000/docs](http://localhost:8000/docs).
It should look like this:

![APIs Screenshot 1](https://github.com/shubham-arora-18/distributed-locking-service/blob/main/api_screenshot1.png?raw=true)
![APIs Screenshot 2](https://github.com/shubham-arora-18/distributed-locking-service/blob/main/api_screenshot2.png?raw=true)
![APIs Screenshot 3](https://github.com/shubham-arora-18/distributed-locking-service/blob/main/api_screenshot3.png?raw=true)
## How to setup!

### 1. Setting up isolated virtual env for this project

- Install the version of python as mentioned in this repo.

    ```sh
    pyenv install $(cat .python-version)
    ```


- Create a virtual env to run the code locally.
    ```sh
    python -m venv .venv
    ```

    This will create a directory `.venv` with python binaries and then you will be able to install packages for that isolated environment.


- Next, activate the environment.

    ```sh
    source .venv/bin/activate
    ```

- To check that it worked correctly.

    ```sh
    which python pip
    ```

    This will create a directory `.venv` with python binaries and then you will be able to install packages for that isolated environment.

### 2. Installing dependencies with Flit

This project uses `flit` to manage our project's dependencies.

- Install dependencies, including flit.

    ```sh
    ./scripts/local/install_dependencies.sh
    pyenv rehash
    ```

### 3. Running code locally

We run this code locally using the uvicorn server.

  ```sh
  ./scripts/local/run_service_locally.sh
  ```

### 4. Accessing Apis Documentation

After the service is successfully running. Open up this url on an internet browser:

[http://localhost:8000/v1/docs](http://localhost:8000/docs)

## How to Format code!
If you have setup the project as instructed above, your code should get auto-formatted before you commit. Still you can use the script below to manually format the code as well.
```sh
./scripts/local/format.sh
```


## Test the code!

```sh
./scripts/local/test.sh
```
