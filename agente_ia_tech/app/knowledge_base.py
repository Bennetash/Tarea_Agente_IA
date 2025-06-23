"""
Base de Conocimiento - Gestión de datos con SQLite
Implementa almacenamiento y búsqueda de información organizacional
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

class KnowledgeBase:
    """Gestión de la base de conocimiento organizacional"""
    
    def __init__(self):
        """Inicializar la base de conocimiento"""
        self.db_path = os.getenv("DATABASE_PATH", "./knowledge_base.db")
        self.logger = logging.getLogger(__name__)
        self.connection = None
    
    async def initialize(self):
        """Inicializar la base de datos y crear tablas"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Crear tablas
            await self._create_tables()
            
            # Poblar con datos iniciales si está vacía
            await self._populate_initial_data()
            
            self.logger.info("Base de conocimiento inicializada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de conocimiento: {e}")
            raise
    
    def is_available(self) -> bool:
        """Verificar si la base de conocimiento está disponible"""
        return self.connection is not None
    
    async def _create_tables(self):
        """Crear tablas de la base de datos"""
        cursor = self.connection.cursor()
        
        # Tabla de documentos de conocimiento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de consultas y respuestas (para aprendizaje)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                confidence REAL,
                sources TEXT,
                classification TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de categorías
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    async def _populate_initial_data(self):
        """Poblar la base de datos con datos iniciales"""
        cursor = self.connection.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM knowledge_items")
        count = cursor.fetchone()[0]
        
        if count > 0:
            return  # Ya hay datos
        
        # Categorías iniciales
        categories = [
            ("Recursos Humanos", "Políticas, beneficios y procedimientos de RRHH"),
            ("Tecnología", "Sistemas, software y soporte técnico"),
            ("Procesos", "Procedimientos operativos y flujos de trabajo"),
            ("Políticas", "Políticas organizacionales y cumplimiento"),
            ("General", "Información general de la organización")
        ]
        
        for name, description in categories:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
        
        # Elementos de conocimiento iniciales
        knowledge_items = [
            {
                "title": "Política de Vacaciones",
                "content": """La política de vacaciones de la organización establece:

• Los empleados tienen derecho a 15 días hábiles de vacaciones anuales
• Las vacaciones se acumulan mensualmente (1.25 días por mes)
• Se requiere solicitud con 2 semanas de anticipación
• Máximo 5 días consecutivos sin aprobación especial
• Las vacaciones no utilizadas se pueden acumular hasta 30 días
• El pago de vacaciones se realiza antes del período de descanso

Para solicitar vacaciones, usar el sistema de RRHH o contactar directamente al departamento.""",
                "category": "Recursos Humanos"
            },
            {
                "title": "Acceso a Sistemas Tecnológicos",
                "content": """Procedimiento para acceso a sistemas:

1. **Solicitud inicial**: Completar formulario de acceso en el portal de TI
2. **Aprobación**: El supervisor debe aprobar la solicitud
3. **Configuración**: TI configura accesos en 24-48 horas
4. **Credenciales**: Se envían por correo seguro
5. **Capacitación**: Sesión obligatoria de seguridad informática

Sistemas disponibles:
• CRM (Salesforce)
• ERP (SAP)
• Office 365
• Sistema de gestión documental
• VPN para trabajo remoto

Contacto: soporte@empresa.com o ext. 1234""",
                "category": "Tecnología"
            },
            {
                "title": "Proceso de Onboarding",
                "content": """El proceso de incorporación de nuevos empleados incluye:

**Semana 1:**
• Orientación general de la empresa
• Configuración de equipos y accesos
• Reunión con supervisor directo
• Asignación de mentor/buddy

**Semana 2:**
• Capacitación específica del rol
• Presentación con el equipo
• Revisión de objetivos y expectativas

**Mes 1:**
• Evaluación de progreso
• Feedback y ajustes
• Planificación de desarrollo

**Documentos requeridos:**
• Contrato firmado
• Documentos de identidad
• Información bancaria
• Certificados académicos

Responsable: Departamento de RRHH""",
                "category": "Recursos Humanos"
            },
            {
                "title": "Política de Trabajo Remoto",
                "content": """Lineamientos para trabajo remoto:

**Elegibilidad:**
• Empleados con más de 6 meses en la empresa
• Roles compatibles con trabajo remoto
• Evaluación de desempeño satisfactoria

**Modalidades:**
• Híbrido: 2-3 días remotos por semana
• Remoto completo: Casos especiales con aprobación
• Remoto temporal: Situaciones específicas

**Requisitos técnicos:**
• Conexión a internet estable (min. 10 Mbps)
• Espacio de trabajo adecuado
• Equipo proporcionado por la empresa
• Acceso VPN configurado

**Responsabilidades:**
• Mantener horarios acordados
• Participar en reuniones virtuales
• Reportar progreso regularmente
• Cumplir con políticas de seguridad""",
                "category": "Políticas"
            },
            {
                "title": "Procedimiento de Solicitud de Compras",
                "content": """Proceso para solicitudes de compra:

**Paso 1: Identificación de necesidad**
• Definir especificaciones técnicas
• Justificar la necesidad
• Estimar presupuesto

**Paso 2: Solicitud formal**
• Completar formulario de solicitud
• Obtener cotizaciones (3 mínimo para >$1000)
• Aprobación del supervisor

**Paso 3: Aprobación financiera**
• Hasta $500: Supervisor directo
• $500-$2000: Gerente de área
• >$2000: Dirección general

**Paso 4: Procesamiento**
• Compras gestiona con proveedores
• Seguimiento de orden de compra
• Recepción y verificación

**Tiempo estimado:** 5-10 días hábiles
**Contacto:** compras@empresa.com""",
                "category": "Procesos"
            },
            {
                "title": "Información General de la Empresa",
                "content": """Datos generales de la organización:

**Misión:** Proporcionar soluciones innovadoras que transformen la manera en que nuestros clientes operan y crecen.

**Visión:** Ser líderes en nuestro sector, reconocidos por la excelencia, innovación y compromiso con nuestros stakeholders.

**Valores:**
• Integridad en todas nuestras acciones
• Innovación constante
• Excelencia en el servicio
• Responsabilidad social
• Trabajo en equipo

**Estructura organizacional:**
• Dirección General
• Gerencia de Operaciones
• Gerencia Comercial
• Gerencia de RRHH
• Gerencia de TI

**Horarios de oficina:**
• Lunes a Viernes: 8:00 AM - 6:00 PM
• Horario flexible: Core time 10:00 AM - 3:00 PM

**Ubicación:** Av. Principal 123, Ciudad, País
**Teléfono:** +1 (555) 123-4567""",
                "category": "General"
            }
        ]
        
        for item in knowledge_items:
            cursor.execute(
                "INSERT INTO knowledge_items (title, content, category) VALUES (?, ?, ?)",
                (item["title"], item["content"], item["category"])
            )
        
        self.connection.commit()
        self.logger.info("Datos iniciales cargados en la base de conocimiento")
    
    async def add_item(self, title: str, content: str, category: str, embedding: Optional[List[float]] = None) -> int:
        """Agregar nuevo elemento a la base de conocimiento"""
        cursor = self.connection.cursor()
        
        embedding_json = json.dumps(embedding) if embedding else None
        
        cursor.execute("""
            INSERT INTO knowledge_items (title, content, category, embedding, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, category, embedding_json, datetime.now()))
        
        self.connection.commit()
        return cursor.lastrowid
    
    async def get_all_items(self) -> List[Dict[str, Any]]:
        """Obtener todos los elementos de la base de conocimiento"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM knowledge_items ORDER BY updated_at DESC")
        
        items = []
        for row in cursor.fetchall():
            item = dict(row)
            if item['embedding']:
                item['embedding'] = json.loads(item['embedding'])
            items.append(item)
        
        return items
    
    async def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Obtener elementos por categoría"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_items WHERE category = ? ORDER BY updated_at DESC",
            (category,)
        )
        
        items = []
        for row in cursor.fetchall():
            item = dict(row)
            if item['embedding']:
                item['embedding'] = json.loads(item['embedding'])
            items.append(item)
        
        return items
    
    async def search_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Buscar elementos similares usando búsqueda de texto simple
        (En implementación real se usarían embeddings)
        """
        cursor = self.connection.cursor()
        
        # Búsqueda simple por palabras clave
        search_terms = query.lower().split()
        
        # Construir consulta SQL para búsqueda de texto
        search_conditions = []
        params = []
        
        for term in search_terms:
            search_conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%"])
        
        sql = f"""
            SELECT *, 
                   (CASE 
                    WHEN LOWER(title) LIKE ? THEN 3
                    WHEN LOWER(content) LIKE ? THEN 2
                    ELSE 1
                   END) as relevance_score
            FROM knowledge_items 
            WHERE {' OR '.join(search_conditions)}
            ORDER BY relevance_score DESC, updated_at DESC
            LIMIT ?
        """
        
        # Agregar parámetros para el scoring
        final_params = [f"%{query.lower()}%", f"%{query.lower()}%"] + params + [top_k]
        
        cursor.execute(sql, final_params)
        
        items = []
        for row in cursor.fetchall():
            item = dict(row)
            if item['embedding']:
                item['embedding'] = json.loads(item['embedding'])
            # Simular score de similitud
            item['similarity_score'] = min(1.0, item['relevance_score'] / 3.0)
            items.append(item)
        
        return items
    
    async def update_embeddings(self, item_id: int, embedding: List[float]):
        """Actualizar embedding de un elemento"""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE knowledge_items SET embedding = ?, updated_at = ? WHERE id = ?",
            (json.dumps(embedding), datetime.now(), item_id)
        )
        self.connection.commit()
    
    async def log_query(self, question: str, answer: str, confidence: float, 
                       sources: List[str], classification: str):
        """Registrar consulta para análisis y mejora"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO query_history (question, answer, confidence, sources, classification)
            VALUES (?, ?, ?, ?, ?)
        """, (question, answer, confidence, json.dumps(sources), classification))
        
        self.connection.commit()
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        
        return [dict(row) for row in cursor.fetchall()]
    
    async def get_query_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de consultas"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        history = []
        for row in cursor.fetchall():
            item = dict(row)
            if item['sources']:
                item['sources'] = json.loads(item['sources'])
            history.append(item)
        
        return history

