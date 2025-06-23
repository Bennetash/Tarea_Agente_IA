"""
Agente de IA Conversacional - Sistema Principal
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

# Importar módulos personalizados
from app.genai_service import GenAIService
from app.embedding_service import EmbeddingService
from app.knowledge_base import KnowledgeBase
from app.prompt_templates import PromptTemplates
from app.ml_classifier import MLClassifier

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="Agente de IA Conversacional",
    description="Sistema de IA para responder preguntas usando GenAI y recuperación semántica",
    version="1.0.0"
)

# Configurar CORS para permitir acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar servicios
genai_service = GenAIService()
embedding_service = EmbeddingService()
knowledge_base = KnowledgeBase()
prompt_templates = PromptTemplates()
ml_classifier = MLClassifier()

# Modelos Pydantic para las APIs
class QuestionRequest(BaseModel):
    question: str
    context: str = ""

class QuestionResponse(BaseModel):
    answer: str
    confidence: float
    sources: list
    classification: str

class KnowledgeItem(BaseModel):
    title: str
    content: str
    category: str

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar la aplicación"""
    print("Iniciando Agente de IA Conversacional...")
    
    # Inicializar base de conocimiento
    await knowledge_base.initialize()
    
    # Cargar modelo de ML
    ml_classifier.load_model()
    
    print("Servicios inicializados correctamente")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Página principal de la aplicación"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "services": {
            "genai": genai_service.is_available(),
            "embedding": embedding_service.is_available(),
            "knowledge_base": knowledge_base.is_available(),
            "ml_classifier": ml_classifier.is_available()
        }
    }

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Endpoint principal para hacer preguntas al agente de IA
    
    Proceso:
    1. Clasificar la pregunta usando ML
    2. Buscar información relevante usando embeddings
    3. Generar respuesta usando GenAI con prompt template
    """
    try:
        # Clasificar la pregunta
        classification = ml_classifier.classify_question(request.question)
        
        # Buscar información relevante en la base de conocimiento
        relevant_docs = await knowledge_base.search_similar(
            request.question, 
            top_k=3
        )
        
        # Preparar el contexto
        context = "\n".join([doc["content"] for doc in relevant_docs])
        if request.context:
            context += f"\n\nContexto adicional: {request.context}"
        
        # Seleccionar template de prompt basado en la clasificación
        prompt = prompt_templates.get_prompt(
            classification, 
            request.question, 
            context
        )
        
        # Generar respuesta usando GenAI
        answer = await genai_service.generate_response(prompt)
        
        # Calcular confianza basada en la similitud semántica
        confidence = embedding_service.calculate_confidence(
            request.question, 
            relevant_docs
        )
        
        return QuestionResponse(
            answer=answer,
            confidence=confidence,
            sources=[doc["title"] for doc in relevant_docs],
            classification=classification
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando pregunta: {str(e)}")

@app.post("/api/knowledge")
async def add_knowledge(item: KnowledgeItem):
    """Agregar nuevo elemento a la base de conocimiento"""
    try:
        result = await knowledge_base.add_item(
            title=item.title,
            content=item.content,
            category=item.category
        )
        return {"message": "Conocimiento agregado exitosamente", "id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando conocimiento: {str(e)}")

@app.get("/api/knowledge")
async def get_knowledge():
    """Obtener todos los elementos de la base de conocimiento"""
    try:
        items = await knowledge_base.get_all_items()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conocimiento: {str(e)}")

@app.get("/api/prompts")
async def get_prompts():
    """Obtener todos los templates de prompts disponibles"""
    return {"prompts": prompt_templates.get_all_templates()}

@app.post("/api/classify")
async def classify_text(request: dict):
    """Clasificar texto usando el modelo de ML"""
    try:
        text = request.get("text", "")
        classification = ml_classifier.classify_question(text)
        confidence = ml_classifier.get_classification_confidence(text)
        
        return {
            "classification": classification,
            "confidence": confidence,
            "available_classes": ml_classifier.get_classes()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clasificando texto: {str(e)}")

@app.get("/api/embeddings/similarity")
async def calculate_similarity(text1: str, text2: str):
    """Calcular similitud semántica entre dos textos"""
    try:
        similarity = embedding_service.calculate_similarity(text1, text2)
        return {"similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando similitud: {str(e)}")

if __name__ == "__main__":
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🌐 Iniciando servidor en http://{host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

