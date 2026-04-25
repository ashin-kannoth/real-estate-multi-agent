from pydantic import BaseModel
from typing import Optional

class TaskRequest(BaseModel):
    task_id:  str
    skill_id: str
    input:    dict

class TaskResponse(BaseModel):
    task_id: str
    status:  str
    output:  dict

class Customer(BaseModel):
    name:               str
    email:              str
    phone:              str
    budget:             float
    preferred_location: str

class Property(BaseModel):
    title:         str
    location:      str
    price:         float
    area:          float
    bedrooms:      int
    property_type: str