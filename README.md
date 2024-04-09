# bw25fastapi

FastAPI application designed to facilitate life cycle assessment (LCA) calculations using the Brightway2 framework.
    Project Management: Create and manage LCA projects.
    Ecoinvent Integration: Set Ecoinvent credentials, import Ecoinvent releases, and list available release versions and system models.
    LCA Calculations: Perform static LCA calculations by specifying demands and impact categories or LCIA methods.

# Installing

There are several ways to get bw25fastapi up and running. You can build it yourself, run it locally, or use the Docker image.

## Build It Yourself
Clone the Repository:
```python
git clone https://github.com/Haitham-ghaida/bw25fastapi.git
cd bw25fastapi
```
### Set up a Virtual Environment (Optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### Install Dependencies:
```bash
pip install -r requirements.txt
```
### Run the Application:
```bash
uvicorn main:app --reload
```
The application will be available at http://localhost:8000.

## Build the Docker Image

Instead of running the application directly on your local machine, you can easily containerize bw25fastapi using Docker. This approach ensures that the application runs consistently across different environments.

Just clone the git repo like the previous option, then cd into that dir
run:
```bash
docker build -t bw25fastapi:latest .
```

This command builds a Docker image named bw25fastapi tagged as latest.

### Run the Docker Container

After building the image, you can run bw25fastapi inside a Docker container.
```bash
docker run -d -p 8000:8000 bw25fastapi:latest
```
You can change the local port to whatever you want in case you are using it for something else for example `5000:8000` if you want port 5000

### Access the Application

With the container running, you can access the FastAPI documentation and test the API directly from your web browser by navigating to http://localhost:8000/docs.

## Use the Docker Image
```bash
docker pull haithamthabet/bw25fastapi:latest
```
then run it
```bash
docker run -d --name bw25fastapi -p 8000:8000 haithamthabet/bw25fastapi:latest
```

This command runs the application in a Docker container named bw25fastapi and makes it accessible on port 8000.

## Using your host's brightway projects and databases.

if you would like the container to use the host's brightway directory then you need to run the container like this:
```bash
docker run docker run -d --name bw25fastapi -p 8000:8000 -v /path/to/your/brightway/dir:/root/.local/share/Brightway3 haithamthabet/bw25fastapi:latest
```

you can refer to the [brightway docs](https://docs.brightway.dev/en/latest/content/faq/data_management.html#where-is-my-data-saved) to find what is the directory for your system. it's different for mac, windows, linux.

you can also run:
```python
bw2data.projects.dir
```
to find your directory

# Getting started

Here are some examples using curl

## Projects

You can see what projects you have by:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/projects/' \
  -H 'accept: application/json'
```

to create a project:
```bash
curl -X POST "http://localhost:8000/api/v1/project/?project_name=my_new_project"
```

## Ecoinvent import

We use the [ecoinvent_interface](https://github.com/brightway-lca/ecoinvent_interface) to import ecoinvent databases

to use it first you need to have a vaild ecoinvent account with access to some databases. you can store your login details with this:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/set_ecoinvent_credentials/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "your_ecoinvent_username",
  "password": "your_ecoinvent_password"
}'
```

afterwards you can import any database available for you using:

Note that this will take some time, i haven't implemented a way to check the progress so you just need to wait.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/project/my_new_project/import_ecoinvent/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "version": "3.8",
  "system_model": "cutoff"
}'
```

## Databases

to see what databases are available in a project.

```bash
curl -X GET "http://localhost:8000/api/v1/projects/{project_name}/database" \
     -H "accept: application/json"
```

to search through the database

```bash
curl -X GET "http://localhost:8000/api/v1/projects/{project_name}/database/{database_name}/activity/search?search_term={search_term}" \
     -H "accept: application/json"
```

to see exchanges of an activity

```bash
curl -X GET "http://localhost:8000/api/v1/projects/{project_name}/database/{database_name}/activity/{activity_code}/exchanges" \
     -H "accept: application/json"
```

## Methods

To see what LCIA methods are available:

```bash
curl -X GET "http://localhost:8000/api/v1/projects/{project_name}/lcia_methods" \
     -H "accept: application/json"
```

to see impact categories of a method

```bash
curl -X GET "http://localhost:8000/api/v1/projects/{project_name}/lcia_methods/{lcia_method}/impact_categories" \
     -H "accept: application/json"
```

## LCA

to run an LCA given a specfic lcia method

```bash
curl -X POST "http://localhost:8000/api/v1/projects/{project_name}/database/{database_name}/lca" \
     -H "Content-Type: application/json" \
     -d '{
         "demands": [{"{activity1_code}": 1.0}, {"{activity2_code}": 2.0}],
         "lcia_method": "{lcia_method_name}"
     }'
```

or you can simply provide a list of impact categories that you want:

```bash
       curl -X POST "http://localhost:8000/api/v1/projects/my_project/database/ecoinvent-3.9-cutoff/lca" \  
         -H "Content-Type: application/json" \
         -d '{
         "demands": [{"67607aa7b3530fe7fbd3a6de8ae58527": 2.0}, {"cf58e5107752177423205ce5e78d16f4": 1}],
         "impact_categories": [["EF v3.1 EN15804", "climate change", "global warming potential (GWP100)"]]
     }'
```

# Contributing

Contributions to bw25fastapi are welcome! Please feel free to submit pull requests or create issues for bugs, questions, and feature requests.

# todo
- [ ] Add response from fastapi
- [ ] Add caching
- [ ] Create methods to add/write databases
- [ ] also general functionality, delete/edit db, project, activity, exchange.
- [ ] ideas?

Feel free to reach out at [haitham.ghaida@uhasselt.be](mailto:haitham.ghaida@uhasselt.be).

# License
This project is licensed under BSD-3-Clause license - see the [LICENSE](LICENSE) file for details.
