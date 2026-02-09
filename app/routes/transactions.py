from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Transaction, User
from .. import schemas
from ..dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# --- 1. DASHBOARD ---
@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.tenant_id == current_user.tenant_id
    ).all()
    
    total_entrada = sum(t.amount for t in transactions if t.type == "entrada")
    total_saida = sum(t.amount for t in transactions if t.type == "saida")
    saldo = total_entrada - total_saida
    
    return {
        "total_entrada": total_entrada,
        "total_saida": total_saida,
        "saldo": saldo
    }

# --- 2. CRIAR (POST) ---
# ... (imports continuam iguais)

@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_transaction = Transaction(
        title=transaction.title,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category, # <--- ADICIONE ESSA LINHA
        date=transaction.date,
        tenant_id=current_user.tenant_id
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# ... (o resto do arquivo continua igual)

# --- 3. LISTAR (GET) ---
@router.get("/", response_model=list[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()
    
    return transactions

# --- 4. DELETAR (DELETE) - NOVIDADE! 🗑️ ---
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Busca a transação pelo ID
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    # Se não existir, erro 404
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # SEGURANÇA: Se a transação não for da empresa do usuário, erro 403 (Proibido)
    if transaction.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para apagar isso")

    # Se passou por tudo, apaga!
    db.delete(transaction)
    db.commit()
    return None