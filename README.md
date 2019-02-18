This repo is a portable, re-runnable, snapshot of the analytics investigation Related Works did for Octopart. It's mostly python, pandas, matplotlib, and Jupyter.

# Setup
The only software you need to install is [Docker](https://www.docker.com/).

## Build the Container
The `./build` script will build a container called `primary_notebooks2`:
```
± ./build
+ docker build --tag primary_notebooks2 .
Sending build context to Docker daemon  52.22MB
Step 1/13 : FROM 'jupyter/datascience-notebook'
 ---> 93936cc74dd8
Step 2/13 : USER root
 ---> Using cache
 ---> ace15739f1ea
...
```

## Store Secrets in the `env` file.
Passwords and other secrets are transmitted to the container via a git-ignored  `env` file in the project root. You'll need to create one with the following entries:
```
DB_HOST=<redshift_dns_name>
DB_USER=<redshift_user>
DB_PASSWORD=<redshift_password>
DEBUG_API_USER=<debug_api_http_user>
DEBUG_API_PASSWORD=<debug_api_http_password>
```
Make sure to to restrict it's permissions:
```
± chmod 600 env
```


## Run the Jupyter Server
Now you should be able to run the Jupyter server:
```
± ./run
...
[I 18:20:53.553 NotebookApp] The Jupyter Notebook is running at:
[I 18:20:53.553 NotebookApp] http://0.0.0.0:8888/
```
You should be able to open your browser and hit [localhost:8888](http://localhost:8888/tree?).


# Scripts

There are a number of convenient scripts at the root of the repository:

* `./build` builds the container.
* `./run` runs the notebook server.
* `./shell` will give you a bash shell in the container.
* `./ipython` will give you an IPython shell in the container with the appropriate python path.
* `./test` will run all the tests.
* `./format` will sort imports and format all of the code using [black](https://github.com/ambv/black).
* `./check-types` will validate type hints using [mypy](http://mypy-lang.org/).


# Directory Structure

* `notebooks` is where all the Jupyter Notebooks live. This tends to be the entry-point for analysis.
* `analysis` is where the core analysis logic lives. Jupyter notebook can quickly become a mess so I tend to put all logic in separate python modules.
* `lib` is where re-usable library code, like functions to pull DataFrames from Redshift, live.
* `sql` is where all the sql files live.
* `tests` is where all the tests live, in a directory-structure that mirrors the outer repo.
* `static_data` is for storing small static datasets, like the list of categories.
* `data` is a git-ignored directory for storing large input/output files, typically CSVs.
* `.disk_cache` is a git-ignored directory for caching the results of complex computations and SQL queries.

