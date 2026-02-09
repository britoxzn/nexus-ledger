from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext # <--- Importando a ferramenta de segurança
from ..database import get_db
from ..models import User
from .. import schemas

router = APIRouter(prefix="/users", tags=["Users"])

# Configuração da Criptografia (O mesmo segredo do main.py)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verifica se já existe alguém com esse email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # 2. Criptografa a senha antes de salvar
    hashed_password = pwd_context.hash(user.password)
    
    # 3. Cria o usuário com a senha segura
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        tenant_id=user.tenant_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user