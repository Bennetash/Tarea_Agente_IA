"""
Servicio de Embeddings - Modelo GenAI basado en embeddings
Implementa recuperación semántica usando sentence-transformers
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging
import os

class EmbeddingService:
    """Servicio para generar embeddings y realizar búsqueda semántica"""
    
    def __init__(self):
        """Inicializar el servicio de embeddings"""
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        try:
            # Cargar modelo de sentence-transformers
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Modelo de embeddings cargado: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Error cargando modelo de embeddings: {e}")
    
    def is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.model is not None
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Generar embedding para un texto
        
        Args:
            text: Texto a codificar
            
        Returns:
            Vector de embedding
        """
        if not self.model:
            raise RuntimeError("Modelo de embeddings no disponible")
        
        try:
            # Generar embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"Error generando embedding: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generar embeddings para múltiples textos
        
        Args:
            texts: Lista de textos a codificar
            
        Returns:
            Matriz de embeddings
        """
        if not self.model:
            raise RuntimeError("Modelo de embeddings no disponible")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generando embeddings en lote: {e}")
            raise
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcular similitud coseno entre dos textos
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            
        Returns:
            Similitud coseno (0-1)
        """
        try:
            # Generar embeddings
            emb1 = self.encode_text(text1)
            emb2 = self.encode_text(text2)
            
            # Calcular similitud coseno
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            # Asegurar que esté en rango [0, 1]
            similarity = max(0, min(1, (similarity + 1) / 2))
            
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Error calculando similitud: {e}")
            return 0.0
    
    def find_most_similar(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Encontrar documentos más similares a una consulta
        
        Args:
            query: Consulta de búsqueda
            documents: Lista de documentos con embeddings
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de documentos ordenados por similitud
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.encode_text(query)
            
            # Calcular similitudes
            similarities = []
            for doc in documents:
                if 'embedding' in doc:
                    doc_embedding = np.array(doc['embedding'])
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    similarities.append((similarity, doc))
                else:
                    # Si no tiene embedding, generarlo
                    doc_text = doc.get('content', '') + ' ' + doc.get('title', '')
                    similarity = self.calculate_similarity(query, doc_text)
                    similarities.append((similarity, doc))
            
            # Ordenar por similitud descendente
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Retornar top_k documentos con score de similitud
            results = []
            for similarity, doc in similarities[:top_k]:
                result_doc = doc.copy()
                result_doc['similarity_score'] = float(similarity)
                results.append(result_doc)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    def calculate_confidence(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> float:
        """
        Calcular confianza basada en la similitud de documentos recuperados
        
        Args:
            query: Consulta original
            retrieved_docs: Documentos recuperados
            
        Returns:
            Score de confianza (0-1)
        """
        if not retrieved_docs:
            return 0.0
        
        try:
            # Calcular similitud promedio con documentos recuperados
            total_similarity = 0.0
            count = 0
            
            for doc in retrieved_docs:
                if 'similarity_score' in doc:
                    total_similarity += doc['similarity_score']
                    count += 1
                else:
                    # Calcular similitud si no está disponible
                    doc_text = doc.get('content', '') + ' ' + doc.get('title', '')
                    similarity = self.calculate_similarity(query, doc_text)
                    total_similarity += similarity
                    count += 1
            
            if count == 0:
                return 0.0
            
            avg_similarity = total_similarity / count
            
            # Ajustar confianza basada en número de documentos y similitud promedio
            confidence = avg_similarity * min(1.0, len(retrieved_docs) / 3.0)
            
            return float(confidence)
            
        except Exception as e:
            self.logger.error(f"Error calculando confianza: {e}")
            return 0.0
    
    def create_document_embeddings(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Crear embeddings para una lista de documentos
        
        Args:
            documents: Lista de documentos con 'title' y 'content'
            
        Returns:
            Lista de documentos con embeddings agregados
        """
        try:
            # Preparar textos para embedding
            texts = []
            for doc in documents:
                text = f"{doc.get('title', '')} {doc.get('content', '')}"
                texts.append(text)
            
            # Generar embeddings en lote
            embeddings = self.encode_batch(texts)
            
            # Agregar embeddings a documentos
            enriched_docs = []
            for i, doc in enumerate(documents):
                enriched_doc = doc.copy()
                enriched_doc['embedding'] = embeddings[i].tolist()
                enriched_docs.append(enriched_doc)
            
            return enriched_docs
            
        except Exception as e:
            self.logger.error(f"Error creando embeddings de documentos: {e}")
            return documents
    
    def get_embedding_dimension(self) -> int:
        """Obtener dimensión de los embeddings"""
        if not self.model:
            return 0
        
        try:
            # Generar embedding de prueba para obtener dimensión
            test_embedding = self.encode_text("test")
            return len(test_embedding)
        except Exception as e:
            self.logger.error(f"Error obteniendo dimensión: {e}")
            return 0

