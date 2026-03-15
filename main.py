from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Integer, Text
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import os

# ==========================================
# Configuração do Banco de Dados (MySQL)
# ==========================================
# Formato: mysql+pymysql://usuario:senha@host:porta/nome_do_banco
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:sua_senha@localhost:3306/social_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# Modelos do Banco de Dados (Entidades)
# ==========================================
class Post(Base):
    __tablename__ = "posts"

    # Mapped[tipo_python] = mapped_column(tipo_sqlalchemy, configurações)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Aqui está o segredo: passamos o nome exato no banco ("userId") como primeiro argumento
    user_id: Mapped[int] = mapped_column("userId", Integer, nullable=False) 
    
    likes: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

# ==========================================
# DTOs (Data Transfer Objects)
# ==========================================
class CreatePostDTO(BaseModel):
    userId: int
    content: str

class PostResponseDTO(BaseModel):
    id: int
    user_id: int
    likes: int
    content: str

    model_config = {"from_attributes": True}

# ==========================================
# Configuração da Aplicação e Variáveis Globais
# ==========================================
app = FastAPI(title="Social Network API")

# Nomes dos repositórios simulados para o endpoint /adapt/
NAMES = [
    "PostsRepository",
    "PostsRepository with strong replication", 
    "PostsRepository with weak replication",
    "PostsRepository with strong fragmentation", 
    "PostsRepository with weak fragmentation"
]
last_component_index = 0

# Injeção de dependência para a sessão do BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Endpoints (Rotas)
# ==========================================

@app.get("/")
def read_root():
    return "Hello!"

@app.get("/all", response_model=List[PostResponseDTO])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

@app.get("/feed/{user_id}", response_model=List[PostResponseDTO])
def get_user_feed(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    return posts

@app.get("/post/{post_id}", response_model=PostResponseDTO)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_post(post_dto: CreatePostDTO, db: Session = Depends(get_db)):
    new_post = Post(
        user_id=post_dto.userId,
        content=post_dto.content,
        likes=0
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Created"}

@app.post("/like/{post_id}", status_code=status.HTTP_200_OK)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.likes += 1
    db.commit()
    return {"message": f"Post on id {post_id} liked"}

@app.post("/adapt/{proxy_id}")
def adapt_repository(proxy_id: int):
    global last_component_index
    if proxy_id < 0 or proxy_id >= len(NAMES):
        raise HTTPException(status_code=400, detail="Invalid proxy ID")
    
    # Em Python/FastAPI, não trocamos componentes compilados em tempo real da mesma
    # forma que a linguagem original. Aqui apenas simulamos a mudança de estado.
    last_component_index = proxy_id
    
    return {"message": f"Repository changed to {NAMES[proxy_id]}"}