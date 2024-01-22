# Distributed Locking Service
Distributed locking service is an intuitive REST based backend service, that enables synchronization of all the distributed processes in your network via simple HTTP calls.
Different processes can attain shared read and shared write locks. Every process acquires a lock with a certain timeout.
After the timeout, the process automatically releases the lock and adjusts the state of the lock accordingly.
This service has been implemented with Python and Fastapi. GCP's Datastore is used as the backend to store the state of the locks.


## APIs

1. **POST /v1/distributed_lock/{lock_id}(is_exclusive)**
   - Creates a lock in the database. The lock can be either write-exclusive (details below) or write-shared.

2. **GET /v1/distributed_lock/{lock_id}**
   - Retrieves information about the lock from the database to analyze the current state of the lock and the associated processes.

3. **PUT /v1/distributed_lock/{lock_id}/read-process/{process_id}(timeout_seconds)**
   - Adds a process to a specified lock as a reader in the list of readers.

4. **PUT /v1/distributed_lock/{lock_id}/read-process/{process_id}/refresh(timeout_seconds)**
   - Refreshes the timeout for the already added read process.

5. **PUT /v1/distributed_lock/{lock_id}/write-process/{process_id}(timeout_seconds)**
   - Adds the process to a specified lock as a writer in a list of writers. This supports two use cases:
     1. If the write lock is write-exclusive, meaning only one process can acquire the write lock at a time.
     2. If the write lock supports shared writes, meaning multiple processes can acquire the lock to write. Note: This relies on the developer's discretion to use this only when the underlying processes are modifying separate resources and there is no chance for a race condition on any underlying resources.

6. **PUT /v1/distributed_lock/{lock_id}/write-process/{process_id}/refresh(timeout_seconds)**
   - Refreshes the timeout for the already added write process.

7. **DELETE /v1/distributed_lock/{lock_id}/read-process/{process_id}**
   - Deletes the read process from the lock and manages the state of the lock accordingly.

8. **DELETE /v1/distributed_lock/{lock_id}/write-process/{process_id}**
   - Deletes the write process from the lock and manages the state of the lock accordingly.

To test these APIs, deploy the service using the provided steps and access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

It should look like this:

![APIs Screenshot 1](https://github.com/shubham-arora-18/distributed-locking-service/blob/main/api_screenshot_1.png?raw=true)
![APIs Screenshot 2](https://github.com/shubham-arora-18/distributed-locking-service/blob/main/api_screenshot_2.png?raw=true)
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
