# bw25fastapi

FastAPI application designed to facilitate life cycle assessment (LCA) calculations using the Brightway2 framework.
    Project Management: Create and manage LCA projects.
    Ecoinvent Integration: Set Ecoinvent credentials, import Ecoinvent releases, and list available release versions and system models.
    LCA Calculations: Perform static LCA calculations by specifying demands and impact categories or LCIA methods.

# Getting Started

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
docker build -t yourusername/bw25fastapi:latest .
```

This command builds a Docker image named bw25fastapi tagged as latest.

### Run the Docker Container

After building the image, you can run bw25fastapi inside a Docker container.
```bash
docker run -d --name bw25fastapi_container -p 8000:8000 yourusername/bw25fastapi:latest
```
you can change the local port to whatever you want incase you are using it for something else for example `5000:8000` if you want port 5000

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

# Contributing

Contributions to bw25fastapi are welcome! Please feel free to submit pull requests or create issues for bugs, questions, and feature requests.

# todo
- [ ] Add methods to create activities and add exchanges
- [ ] Create methods to add/write databases
- [ ] Other?

# License
This project is licensed under BSD-3-Clause license - see the LICENSE file for details.
