"""
Clasificador de Machine Learning - Módulo adicional ML
Implementa clasificación de consultas usando scikit-learn
"""

import pickle
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import logging
import joblib

class MLClassifier:
    """Clasificador de Machine Learning para categorizar consultas"""
    
    def __init__(self):
        """Inicializar el clasificador"""
        self.model_path = "./models/question_classifier.pkl"
        self.vectorizer_path = "./models/vectorizer.pkl"
        self.pipeline = None
        self.classes = []
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de modelos si no existe
        os.makedirs("./models", exist_ok=True)
    
    def is_available(self) -> bool:
        """Verificar si el modelo está disponible"""
        return self.pipeline is not None
    
    def load_model(self):
        """Cargar modelo entrenado o crear uno nuevo"""
        try:
            if os.path.exists(self.model_path):
                # Cargar modelo existente
                self.pipeline = joblib.load(self.model_path)
                self.classes = self.pipeline.classes_.tolist()
                self.logger.info("Modelo de clasificación cargado exitosamente")
            else:
                # Crear y entrenar nuevo modelo
                self._create_and_train_model()
                
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            # Crear modelo básico como fallback
            self._create_basic_model()
    
    def _create_and_train_model(self):
        """Crear y entrenar un nuevo modelo de clasificación"""
        try:
            # Datos de entrenamiento sintéticos
            training_data = self._generate_training_data()
            
            # Preparar datos
            texts = [item["text"] for item in training_data]
            labels = [item["label"] for item in training_data]
            
            # Crear pipeline
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    stop_words=None,  # Mantener palabras en español
                    ngram_range=(1, 2),
                    lowercase=True
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Entrenar modelo
            self.pipeline.fit(X_train, y_train)
            self.classes = self.pipeline.classes_.tolist()
            
            # Evaluar modelo
            y_pred = self.pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.logger.info(f"Modelo entrenado con precisión: {accuracy:.3f}")
            
            # Guardar modelo
            joblib.dump(self.pipeline, self.model_path)
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelo: {e}")
            self._create_basic_model()
    
    def _generate_training_data(self) -> List[Dict[str, str]]:
        """Generar datos de entrenamiento sintéticos"""
        return [
            # Recursos Humanos
            {"text": "¿Cuántos días de vacaciones tengo?", "label": "recursos_humanos"},
            {"text": "¿Cómo solicito permiso médico?", "label": "recursos_humanos"},
            {"text": "¿Cuál es la política de trabajo remoto?", "label": "recursos_humanos"},
            {"text": "¿Dónde encuentro mi recibo de sueldo?", "label": "recursos_humanos"},
            {"text": "¿Cómo cambio mis datos personales?", "label": "recursos_humanos"},
            {"text": "¿Qué beneficios tengo como empleado?", "label": "recursos_humanos"},
            {"text": "¿Cuál es el proceso de evaluación de desempeño?", "label": "recursos_humanos"},
            {"text": "¿Cómo solicito capacitación?", "label": "recursos_humanos"},
            {"text": "¿Cuál es la política de horarios flexibles?", "label": "recursos_humanos"},
            {"text": "¿Cómo reporto un problema de acoso laboral?", "label": "recursos_humanos"},
            
            # Tecnología
            {"text": "¿Cómo accedo al sistema CRM?", "label": "tecnologia"},
            {"text": "¿Cómo configuro mi correo electrónico?", "label": "tecnologia"},
            {"text": "¿Cómo conecto a la VPN?", "label": "tecnologia"},
            {"text": "¿Dónde descargo el software de la empresa?", "label": "tecnologia"},
            {"text": "¿Cómo reseteo mi contraseña?", "label": "tecnologia"},
            {"text": "¿Qué hacer si mi computadora no enciende?", "label": "tecnologia"},
            {"text": "¿Cómo accedo al sistema ERP?", "label": "tecnologia"},
            {"text": "¿Cómo instalo las aplicaciones necesarias?", "label": "tecnologia"},
            {"text": "¿Cómo reporto un problema técnico?", "label": "tecnologia"},
            {"text": "¿Cuáles son los requisitos de seguridad informática?", "label": "tecnologia"},
            
            # Procesos
            {"text": "¿Cómo solicito una compra?", "label": "procesos"},
            {"text": "¿Cuál es el proceso de aprobación de gastos?", "label": "procesos"},
            {"text": "¿Cómo reporto un incidente?", "label": "procesos"},
            {"text": "¿Cuál es el procedimiento de onboarding?", "label": "procesos"},
            {"text": "¿Cómo escalo un problema?", "label": "procesos"},
            {"text": "¿Cuál es el flujo de trabajo para proyectos?", "label": "procesos"},
            {"text": "¿Cómo solicito acceso a un sistema?", "label": "procesos"},
            {"text": "¿Cuál es el proceso de facturación?", "label": "procesos"},
            {"text": "¿Cómo manejo las quejas de clientes?", "label": "procesos"},
            {"text": "¿Cuál es el procedimiento de emergencia?", "label": "procesos"},
            
            # Políticas
            {"text": "¿Cuál es la política de confidencialidad?", "label": "politicas"},
            {"text": "¿Qué dice la política de uso de internet?", "label": "politicas"},
            {"text": "¿Cuáles son las normas de vestimenta?", "label": "politicas"},
            {"text": "¿Cuál es la política de viajes?", "label": "politicas"},
            {"text": "¿Qué dice la política de conflicto de intereses?", "label": "politicas"},
            {"text": "¿Cuál es la política de redes sociales?", "label": "politicas"},
            {"text": "¿Qué normas de seguridad debo seguir?", "label": "politicas"},
            {"text": "¿Cuál es la política de diversidad e inclusión?", "label": "politicas"},
            {"text": "¿Qué dice la política de sostenibilidad?", "label": "politicas"},
            {"text": "¿Cuáles son las políticas de cumplimiento?", "label": "politicas"},
            
            # General
            {"text": "¿Cuál es la misión de la empresa?", "label": "general"},
            {"text": "¿Dónde están ubicadas las oficinas?", "label": "general"},
            {"text": "¿Cuál es la historia de la empresa?", "label": "general"},
            {"text": "¿Quiénes son los directivos?", "label": "general"},
            {"text": "¿Cuáles son los valores de la empresa?", "label": "general"},
            {"text": "¿En qué sectores opera la empresa?", "label": "general"},
            {"text": "¿Cuántos empleados tiene la empresa?", "label": "general"},
            {"text": "¿Cuál es la estructura organizacional?", "label": "general"},
            {"text": "¿Cómo contacto a diferentes departamentos?", "label": "general"},
            {"text": "¿Cuáles son los horarios de oficina?", "label": "general"}
        ]
    
    def _create_basic_model(self):
        """Crear modelo básico de clasificación por palabras clave"""
        self.classes = ["recursos_humanos", "tecnologia", "procesos", "politicas", "general"]
        self.pipeline = None  # Usar clasificación por reglas
        self.logger.info("Modelo básico de clasificación por reglas creado")
    
    def classify_question(self, question: str) -> str:
        """
        Clasificar una pregunta en una categoría
        
        Args:
            question: Pregunta a clasificar
            
        Returns:
            Categoría predicha
        """
        try:
            if self.pipeline:
                # Usar modelo entrenado
                prediction = self.pipeline.predict([question])[0]
                return prediction
            else:
                # Usar clasificación por reglas
                return self._classify_by_rules(question)
                
        except Exception as e:
            self.logger.error(f"Error clasificando pregunta: {e}")
            return "general"
    
    def _classify_by_rules(self, question: str) -> str:
        """Clasificación básica por palabras clave"""
        question_lower = question.lower()
        
        # Palabras clave por categoría
        keywords = {
            "recursos_humanos": [
                "vacaciones", "permiso", "sueldo", "salario", "beneficios", "rrhh",
                "recursos humanos", "evaluación", "desempeño", "capacitación",
                "horario", "trabajo remoto", "licencia", "contrato"
            ],
            "tecnologia": [
                "sistema", "software", "computadora", "internet", "correo",
                "email", "contraseña", "password", "vpn", "crm", "erp",
                "aplicación", "programa", "técnico", "soporte", "instalación"
            ],
            "procesos": [
                "proceso", "procedimiento", "solicitud", "aprobación", "flujo",
                "workflow", "compra", "gasto", "facturación", "onboarding",
                "escalamiento", "incidente", "reporte"
            ],
            "politicas": [
                "política", "norma", "regla", "cumplimiento", "confidencialidad",
                "seguridad", "vestimenta", "viajes", "conflicto", "diversidad",
                "sostenibilidad", "código de conducta"
            ],
            "general": [
                "empresa", "organización", "misión", "visión", "valores",
                "historia", "directivos", "oficina", "ubicación", "contacto",
                "estructura", "departamento"
            ]
        }
        
        # Contar coincidencias por categoría
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in question_lower)
            scores[category] = score
        
        # Retornar categoría con mayor score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return "general"
    
    def get_classification_confidence(self, question: str) -> float:
        """
        Obtener confianza de la clasificación
        
        Args:
            question: Pregunta a evaluar
            
        Returns:
            Score de confianza (0-1)
        """
        try:
            if self.pipeline:
                # Usar probabilidades del modelo
                probabilities = self.pipeline.predict_proba([question])[0]
                return float(max(probabilities))
            else:
                # Confianza básica por reglas
                return 0.7  # Confianza fija para clasificación por reglas
                
        except Exception as e:
            self.logger.error(f"Error calculando confianza: {e}")
            return 0.5
    
    def get_classes(self) -> List[str]:
        """Obtener lista de clases disponibles"""
        return self.classes.copy()
    
    def retrain_model(self, new_data: List[Dict[str, str]]):
        """
        Reentrenar modelo con nuevos datos
        
        Args:
            new_data: Lista de diccionarios con 'text' y 'label'
        """
        try:
            if not new_data:
                return
            
            # Combinar con datos existentes
            existing_data = self._generate_training_data()
            all_data = existing_data + new_data
            
            # Preparar datos
            texts = [item["text"] for item in all_data]
            labels = [item["label"] for item in all_data]
            
            # Reentrenar pipeline
            if self.pipeline:
                self.pipeline.fit(texts, labels)
            else:
                self._create_and_train_model()
            
            # Guardar modelo actualizado
            if self.pipeline:
                joblib.dump(self.pipeline, self.model_path)
            
            self.logger.info(f"Modelo reentrenado con {len(new_data)} nuevos ejemplos")
            
        except Exception as e:
            self.logger.error(f"Error reentrenando modelo: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        return {
            "model_available": self.pipeline is not None,
            "model_path": self.model_path,
            "classes": self.classes,
            "model_type": "MultinomialNB" if self.pipeline else "Rule-based"
        }

