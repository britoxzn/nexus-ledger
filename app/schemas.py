from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

# --- SCHEMAS DA EMPRESA (TENANT) ---
class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SCHEMAS DO USUÁRIO (USER) ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    tenant_id: int

class User(UserBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

# --- SCHEMAS DE TRANSAÇÃO (TRANSACTION) ---
class TransactionBase(BaseModel):
    title: str
    amount: float
    type: str
    category: str  # <--- NOVIDADE AQUI
    date: date

class TransactionCreate(TransactionBase):
    pass 

class Transaction(TransactionBase):
    id: int
    tenant_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True