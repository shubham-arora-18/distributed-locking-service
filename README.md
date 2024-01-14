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
  ./scripts/local/run_service.sh
  ```

### 4. Accessing Apis Documentation

After the service is successfully running. Open up this url on an internet browser:

[http://localhost:8000/docs](http://localhost:8000/docs)

## How to Format code!
If you have setup the project as instructed above, your code should get auto-formatted before you commit. Still you can use the script below to manually format the code as well.
```sh
./scripts/local/format.sh
```


## Test the code!

```sh
./scripts/local/test.sh
```
