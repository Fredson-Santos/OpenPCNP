import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class OrgaoResponse(BaseModel):
    id: uuid.UUID
    cnpj: Optional[str] = None
    nome: str
    esfera: Optional[str] = None
    uf: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class OrgaoAutocompleteResponse(BaseModel):
    id: uuid.UUID
    nome: str

    model_config = ConfigDict(from_attributes=True)

class OrgaosResponse(BaseModel):
    data: List[OrgaoResponse]