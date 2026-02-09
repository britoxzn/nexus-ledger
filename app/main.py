from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware # <--- NOVO IMPORT AQUI
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from .database import engine, Base, get_db
from .models import User
from . import schemas
from .routes import tenants, users, transactions

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SECRET_KEY = "Lu84634689" # Sua chave secreta
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Função para criar o Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- INICIALIZAÇÃO DA API ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Ledger API")

# --- CONFIGURAÇÃO DE CORS (ADICIONADO AGORA) ---
# Isso libera o acesso para o seu Front-end poder chamar a API
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Libera geral (ideal para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"], # Libera todos os métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Libera todos os cabeçalhos
)

# Conectando as rotas
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"message": "Nexus Ledger API is organized and running!"}

# --- ROTA DE LOGIN ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # O Swagger manda o email dentro de um campo chamado 'username'
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verifica senha (usando a criptografia nova pbkdf2)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="E-mail ou senha incorretos"
        )
    
    # Gera o Token
    access_token = create_access_token(data={"sub": user.email, "tenant_id": user.tenant_id})
    return {"access_token": access_token, "token_type": "bearer"}