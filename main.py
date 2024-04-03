from fastapi import FastAPI, HTTPException
import requests
import bw2data as bd
import bw2calc as bc
import bw2io as bi
from ecoinvent_interface import (
    Settings,
    EcoinventRelease,
    permanent_setting,
)
from models import Credentials, EcoinventImportDetails, LCARequest, LCAResult, LCAInput
from utils import convert_results_format


app = FastAPI()


@app.post("/api/v1/project/")
async def create_project(project_name: str):
    """
    Create a new project.

    Args:
        project_name (str): The name of the project to create.

    Returns:
        dict: A dictionary containing the name of the created project.

    Raises:
        HTTPException: If the project already exists.

    Example:
        curl "http://localhost:8000/api/version_number(v1)/projects" -X POST -d 'project_name=my_project'
    """
    if project_name in bd.projects:
        raise HTTPException(status_code=400, detail="Project already exists.")
    bd.projects.create_project(project_name)
    return {"project": project_name}


@app.post("/api/v1/set_ecoinvent_credentials/")
async def set_ecoinvent_credentials(credentials: Credentials):
    """
    Sets the Ecoinvent credentials for a user.

    Args:
        credentials (Credentials): The Ecoinvent credentials to set.

    Returns:
        dict: A dictionary with a success message.

    Example:
        curl -X POST -H "Content-Type: application/json" -d '{"username": "MyUserName","password": "MyPassWord"}' "http://localhost:8000/api/vX/set_ecoinvent_credentials/"
    """
    permanent_setting("username", credentials.username)
    permanent_setting("password", credentials.password)
    return {"message": "Ecoinvent credentials set successfully."}


@app.get("/api/v1/release/versions")
async def list_release_versions():
    """
    Retrieve the list of available Ecoinvent release versions.

    Returns:
        dict: A dictionary containing the list of release versions.

    Note:
        This function requires the Ecoinvent credentials to be set.

    Example:
        curl "http://localhost:8000/api/vX/release/versions"
    """
    my_settings = Settings()
    try:
        release = EcoinventRelease(my_settings)
        versions = release.list_versions()
        return {"versions": versions}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized. Please set the correct username and password.",
            )
        else:
            raise HTTPException(
                status_code=500, detail="An error occurred while fetching the versions."
            )


@app.get("/api/v1/release/versions/{version}/system_models")
async def list_system_models(version):
    """
    Retrieve the list of system models.

    Returns:
        dict: A dictionary containing the list of system models.

    Example:
        curl "http://localhost:8000/api/vX/release/versions/{version}/system_models"
    """
    my_settings = Settings()
    try:
        release = EcoinventRelease(my_settings)
        return {"system_models": release.list_system_models(version)}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/project/{project_name}/import_ecoinvent/")
async def import_ecoinvent(project_name: str, import_details: EcoinventImportDetails):
    """
    Import an Ecoinvent release into a project.

    If it seems like its taking too long, its because it does take a long time to import the data.

    Args:
        project_name (str): The name of the project to import the release into.
        import_details (EcoinventImportDetails): The details of the Ecoinvent release to import, including version and system model.

    Returns:
        dict: A dictionary containing the name of the project and the version of the release imported.

    Raises:
        HTTPException: If the version or system model is not found.

    Example:
        curl -X POST "http://localhost:8000/api/v1/project/my_project/import_ecoinvent/" -H "Content-Type: application/json" -d '{"version": "3.7.1", "system_model": "consequential"}'
    """
    bd.projects.set_current(project_name)
    # Simulated logic for checking version and system model
    # Let's assume `EcoinventRelease` and `Settings` are defined elsewhere in your application
    my_settings = Settings()
    release = EcoinventRelease(my_settings)
    if import_details.version not in release.list_versions():
        raise HTTPException(status_code=404, detail="Version not found.")
    if import_details.system_model not in release.list_system_models(
        import_details.version
    ):
        raise HTTPException(status_code=404, detail="System model not found.")

    # Simulated import logic
    bi.import_ecoinvent_release(
        version=import_details.version, system_model=import_details.system_model
    )

    # Placeholder response
    return {
        "message": "Ecoinvent credentials set successfully.",
        "project": project_name,
        "version": import_details.version,
        "system_model": import_details.system_model,
    }


@app.get("/api/v1/projects/")
async def list_projects():
    """
    Retrieves a list of projects.

    Returns:
        A dictionary containing the list of projects.

    Example:
       curl "http://localhost:8000/api/version_number(v1)/projects"
    """
    projects_list = list(bd.projects)
    clean_projects_list = [project.name for project in projects_list]
    return {"projects": clean_projects_list}


@app.get("/api/v1/projects/{project_name}/database")
async def list_project_databases(project_name: str):
    """
    Retrieve the list of databases for a given project.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: A dictionary containing the list of databases.

    Raises:
        HTTPException: If the project is not found.

    Example Usage:
        curl "http://localhost:8000/api/version_number(v1)/projects/my_project/database"
    """
    if project_name in bd.projects:
        if bd.projects.current != project_name:
            bd.projects.set_current(project_name)
        return {"databases": list(bd.databases)}
    else:
        raise HTTPException(status_code=404, detail="Project not found.")


@app.get("/api/v1/projects/{project_name}/database/{database_name}/activity/search")
async def search_activities(project_name: str, database_name: str, search_term: str):
    """
    Search for activities in a specific project and database based on a given search term.

    Args:
        project_name (str): The name of the project.
        database_name (str): The name of the database.
        search_term (str): The search term to match against activity names.

    Returns:
        dict: A dictionary containing the search results in the following format:
            {
                "results": [
                    {
                        "code": <activity_code>,
                        "name": <activity_name>
                        "location": <activity_location>,
                    },
                    ...
                ]
            }

    Raises:
        HTTPException: If the specified project is not found.

    Examples:
        Using curl:

        1. Search for activities in project "my_project" and database "my_database" with the search term "example":
            curl "http://localhost:8000/api/version_number(v1)/projects/my_project/databases/my_database/activities/search?search_term=example"
        2. Search for activities in project "my_project" and database "my_database" with the search term "market for steel, low-alloyed":
            curl "http://localhost:8000/api/version_number(v1)/projects/my_project/databases/my_database/activities/search?search_term=market%20for%20steel,%20low-alloyed"
    """
    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    if bd.projects.current != project_name:
        bd.projects.set_current(project_name)
    if database_name not in bd.databases:
        raise HTTPException(status_code=404, detail="Database not found.")
    db = bd.Database(database_name)
    results = db.search(search_term)
    formatted_results = [
        {
            "code": activity["code"],
            "name": activity["name"],
            "location": activity["location"],
        }
        for activity in results
    ]
    return {"results": formatted_results}


@app.get(
    "/api/v1/projects/{project_name}/database/{database_name}/activity/{activity_code}"
)
async def get_activity_by_code(
    project_name: str, database_name: str, activity_code: str
):
    """
    Retrieve activity information by activity code.

    Args:
        project_name (str): The name of the project.
        database_name (str): The name of the database.
        activity_code (str): The code of the activity.

    Returns:
        dict: A dictionary containing the activity information.

    Raises:
        HTTPException: If the project or activity is not found.

    Examples:
        curl -X GET "http://localhost:8000/api/version_number(v1)/projects/my_project/databases/my_database/activities/123"
    """
    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    if bd.projects.current != project_name:
        bd.projects.set_current(project_name)
    if database_name not in bd.databases:
        raise HTTPException(status_code=404, detail="Database not found.")
    db = bd.Database(database_name)
    try:
        activity = db.get(activity_code)
        activity_data = {"code": activity["code"], "name": activity["name"]}
        return {"activity": activity_data}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found.")


@app.get(
    "/api/v1/projects/{project_name}/database/{database_name}/activity/{activity_code}/exchanges"
)
async def get_activity_exchanges(
    project_name: str, database_name: str, activity_code: str
):
    """
    Retrieve exchanges for a given activity.

    Args:
        project_name (str): The name of the project.
        database_name (str): The name of the database.
        activity_code (str): The code of the activity.

    Returns:
        dict: A dictionary containing the exchanges for the activity.

    Raises:
        HTTPException: If the project or activity is not found.

    Examples:
        curl -X GET "http://localhost:8000/api/version_number(v1)/projects/my_project/databases/my_database/activities/123/exchanges"
    """
    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    if bd.projects.current != project_name:
        bd.projects.set_current(project_name)
    if database_name not in bd.databases:
        raise HTTPException(status_code=404, detail="Database not found.")
    db = bd.Database(database_name)
    try:
        activity = db.get(activity_code)
        exchanges = [
            {
                "input": exchange.input,
                "amount": exchange["amount"],
                "type": exchange["type"],
            }
            for exchange in activity.exchanges()
        ]
        print(activity)
        return {"exchanges": exchanges}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found.")


@app.get("/api/v1/projects/{project_name}/lcia_methods")
async def get_lcia_methods(project_name: str):
    """
    Retrieve the list of methods in a project.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: A dictionary containing the list of methods.

    Raises:
        HTTPException: If the project is not found.

    Examples:
        curl "http://localhost:8000/api/version_number(v1)/projects/my_project/lcia_methods"
    """
    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    if bd.projects.current != project_name:
        bd.projects.set_current(project_name)
    methods = [method[0] for method in bd.methods]
    methods = list(set(methods))
    return {"methods": methods}


@app.get("/api/v1/projects/{project_name}/lcia_methods/{lcia_method}/impact_categories")
async def get_impact_categories(project_name: str, lcia_method: str):
    """
    Retrieve the list of impact categories for a given LCIA method.

    Args:
        project_name (str): The name of the project.
        lcia_method (str): The name of the LCIA method.

    Returns:
        dict: A dictionary containing the list of impact categories.

    Raises:
        HTTPException: If the project or LCIA method is not found.

    Examples:
        curl "http://localhost:8000/api/version_number(v1)/projects/my_project/lcia_methods/my_lcia_method/impact_categories"
        for example:
        curl "http://localhost:8000/api/v1/project/Project_name/lcia_methods/EF%20v3.0/impact_categories"
            This gives me
    """
    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    if bd.projects.current != project_name:
        bd.projects.set_current(project_name)
    impact_categories = [method[1] for method in bd.methods if lcia_method == method[0]]
    if not impact_categories:
        raise HTTPException(status_code=404, detail="LCIA method not found.")

    return {"impact_categories": impact_categories}


def staticLCA(inputs: LCAInput) -> LCAResult:
    """
    This method performs static LCA calculations for a list of demands and a list of methods.
    By static we mean that uncertainty distributions are not taken into account.

    Parameters
    ----------
    demands : list
        A list of demands, where each demand is a dictionary of the form:
        {
            activity name: amount
        }
    methods : list
        A list of methods, where each method is a tuple of strings of the form:
        ("foo", "bar", "baz")

    Returns
    -------
    dict
        A dictionary containing the results of static LCA calculations, where the keys are tuples of the form:
        (activity name, location, code, database)
        and the values are lists of floats containing the LCA results for each method.

        it will look like this:
        {('market for steel, low-alloyed',
        'GLO',
        'a81ce0e882f1b0ef617462fc8e7472e4',
        'ecoinvent391cutoff'): {('IPCC 2021',
        'climate change',
        'GWP 100a, incl. H and bio CO2'): 2.070411514997294},
    """
    methods = inputs.impact_categories
    demands = inputs.demands
    # make sure at least one method is provided.
    if len(methods) == 0:
        raise ValueError(
            "No methods were specified. Please specify at least one method to perform LCA calculations"
        )
    # assert that methods are lists of tuples.
    assert (
        isinstance(methods, list)
        and isinstance(methods[0], tuple)
        and isinstance(methods[0][0], str)
    ), "Methods must be a list of tuples of strings"

    # Create all demands with a comprehension
    all_demands = {k: 1 for demand in demands for k in demand}
    # Initialize LCA object, the parameter use_distributions is false by default so no need to include it.
    lca = bc.LCA(demand=all_demands, method=methods[0])
    lca.lci()

    # Create a dict of characterization matrices
    C_matrices = {}

    for method in methods:
        lca.switch_method(method)
        C_matrices[method] = lca.characterization_matrix.copy()

    # Create container for results
    results = {}
    # Adding a progress bar for iterating through demands
    for demand in demands:
        # Updating the progress bar description
        act = bd.get_activity(list(demand.keys())[0])
        results[str(act)] = {method: None for method in methods}

        # Convert to integer ids
        int_demand = {act.id: value for _, value in demand.items()}
        lca.lci(int_demand)
        for method in methods:
            lca.switch_method(method)
            results[str(act)][method] = (C_matrices[method] * lca.inventory).sum()
    print(results, "#" * 100)
    return convert_results_format(results)


@app.post("/api/v1/projects/{project_name}/database/{database_name}/lca")
async def run_lca(project_name: str, database_name: str, body: LCARequest):
    """
    Run life cycle assessment (LCA) calculations for a given project, database, and set of demands.

    Args:
        project_name (str): The name of the project.
        database_name (str): The name of the database.
        body (LCARequest): The request body containing the demands for the LCA calculations.

    Returns:
        dict: The results of the LCA calculations.

    Raises:
        HTTPException: If the project or database is not found, or if an activity is not found in the database.
    
    Note:
        This function assumes that the `staticLCA` function can process the input provided in the `LCARequest` object.
        
        in the body of the request, you can provide either the `lcia_method` or the `impact_categories` but not both.
        if you provide the `lcia_method`, the function will look for the method in the list of methods and use it.
        if you provide the `impact_categories`, the function will look for each method in the list of methods and use it.

    Example curl:
        curl -X POST -H "Content-Type: application/json" -d '{
            "demands": [
                {"activity1_code": 10},
                {"activity2_code": 5}
            ],
            "lcia_method": "method1"
        }' http://localhost:8000/run_lca?project_name=my_project&database_name=my_database
        or
        curl -X POST "http://localhost:8000/api/v1/projects/my_project/database/ecoinvent-3.9-cutoff/lca" \   8.9s  Wed 17:27
         -H "Content-Type: application/json" \
         -d '{
         "demands": [{"67607aa7b3530fe7fbd3a6de8ae58527": 2.0}, {"cf58e5107752177423205ce5e78d16f4": 1}],
         "lcia_method": "EF v3.1 EN15804"
     }'
       or
       curl -X POST "http://localhost:8000/api/v1/projects/my_project/database/ecoinvent-3.9-cutoff/lca" \  115ms  Wed 17:25
         -H "Content-Type: application/json" \
         -d '{
         "demands": [{"67607aa7b3530fe7fbd3a6de8ae58527": 2.0}, {"cf58e5107752177423205ce5e78d16f4": 1}],
         "impact_categories": [["EF v3.1 EN15804", "climate change", "global warming potential (GWP100)"]]
     }'
    """

    if project_name not in bd.projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    bd.projects.set_current(project_name)

    if database_name not in bd.databases:
        raise HTTPException(status_code=404, detail="Database not found.")

    # Fetch the database
    db = bd.Database(database_name)

    for demand in body.demands:
        for key in demand:
            try:
                db.get(key)
            except:
                raise HTTPException(
                    status_code=404, detail=f"Activity {key} not found."
                )

    demands = []
    for demand in body.demands:
        demands.append({(database_name, key): amount for key, amount in demand.items()})

    impact_categories = []
    if body.lcia_method:
        impact_categories = [
            method for method in bd.methods if body.lcia_method == method[0]
        ]
    elif body.impact_categories:
        for method_list in body.impact_categories:
            method_tuple = tuple(method_list)  # Convert list to tuple
            if method_tuple not in bd.methods:
                raise HTTPException(
                    status_code=404, detail="Impact category not found."
                )
            impact_categories.append(method_tuple)
    else:
        raise HTTPException(
            status_code=400,
            detail="No impact categories provided or lcia method provided.",
        )

    # Perform the LCA calculations
    results = staticLCA(
        LCAInput(demands=demands, impact_categories=impact_categories)
    )  # Assuming staticLCA can process this input

    return results
