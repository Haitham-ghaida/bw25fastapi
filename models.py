from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional

class Credentials(BaseModel):
    username: str
    password: str


class EcoinventImportDetails(BaseModel):
    version: str
    system_model: str
    
    
class LCARequest(BaseModel):
    demands: List[Dict[str, float]]
    impact_categories: Optional[List[List[str]]] = Field(default_factory=list)
    lcia_method: Optional[str] = None


class LCAResult(BaseModel):
    results: Dict[str, Dict[str, float]]  # To structure the results


class LCAInput(BaseModel):
    demands: List[Dict[tuple, float]]
    impact_categories: List[Tuple[str, str, str]]
