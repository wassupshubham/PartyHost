from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

# Expense Schemas
class ExpenseCreate(BaseModel):
    description: str
    amount: float
    paid_by_id: int
    group_id: int

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: float
    paid_by_id: int
    payer: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

# Group Schemas
class GroupCreate(BaseModel):
    name: str
    created_by: int

class GroupResponse(BaseModel):
    id: int
    name: str
    expenses: List[ExpenseResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)