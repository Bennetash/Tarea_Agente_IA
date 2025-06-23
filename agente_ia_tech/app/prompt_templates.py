"""
Templates de Prompts - Prompts reutilizables para diferentes tipos de consultas
Implementa un sistema de templates para optimizar las respuestas del agente
"""

from typing import Dict, Any
import logging

class PromptTemplates:
    """Gestión de templates de prompts para diferentes tipos de consultas"""
    
    def __init__(self):
        """Inicializar templates de prompts"""
        self.logger = logging.getLogger(__name__)
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar todos los templates de prompts"""
        return {
            "general": {
                "name": "Consulta General",
                "description": "Template para consultas generales sobre la organización",
                "template": """Eres un asistente de IA especializado en ayudar a empleados con consultas organizacionales.

CONTEXTO ORGANIZACIONAL:
{context}

PREGUNTA DEL USUARIO: {question}

INSTRUCCIONES:
- Proporciona una respuesta clara, precisa y útil
- Basa tu respuesta en el contexto proporcionado
- Si no tienes información suficiente, indícalo claramente
- Mantén un tono profesional pero amigable
- Incluye pasos específicos cuando sea apropiado
- Si es necesario, sugiere contactar al departamento correspondiente

RESPUESTA:""",
                "max_tokens": 400
            },
            
            "recursos_humanos": {
                "name": "Recursos Humanos",
                "description": "Template para consultas de RRHH, beneficios y políticas laborales",
                "template": """Eres un especialista en Recursos Humanos que ayuda a empleados con consultas sobre políticas, beneficios y procedimientos.

INFORMACIÓN DE RRHH DISPONIBLE:
{context}

CONSULTA DEL EMPLEADO: {question}

INSTRUCCIONES:
- Proporciona información precisa sobre políticas y procedimientos de RRHH
- Incluye pasos específicos para procesos administrativos
- Menciona documentos o formularios requeridos
- Indica plazos y tiempos de procesamiento
- Si la consulta requiere atención personalizada, dirige al empleado al departamento de RRHH
- Mantén la confidencialidad y profesionalismo

RESPUESTA ESPECIALIZADA:""",
                "max_tokens": 450
            },
            
            "tecnologia": {
                "name": "Soporte Tecnológico",
                "description": "Template para consultas técnicas, sistemas y herramientas",
                "template": """Eres un especialista en soporte técnico que ayuda a empleados con consultas sobre sistemas, software y herramientas tecnológicas.

INFORMACIÓN TÉCNICA DISPONIBLE:
{context}

CONSULTA TÉCNICA: {question}

INSTRUCCIONES:
- Proporciona soluciones paso a paso para problemas técnicos
- Incluye requisitos técnicos y configuraciones necesarias
- Menciona alternativas si la solución principal no funciona
- Indica cuándo es necesario contactar al equipo de TI
- Incluye medidas de seguridad informática relevantes
- Usa lenguaje técnico apropiado pero comprensible

RESPUESTA TÉCNICA:""",
                "max_tokens": 400
            },
            
            "procesos": {
                "name": "Procesos Operativos",
                "description": "Template para consultas sobre procedimientos y flujos de trabajo",
                "template": """Eres un experto en procesos organizacionales que ayuda a empleados a entender y seguir procedimientos operativos.

INFORMACIÓN DE PROCESOS:
{context}

CONSULTA SOBRE PROCESO: {question}

INSTRUCCIONES:
- Explica el proceso paso a paso de manera clara
- Incluye responsables y tiempos estimados para cada etapa
- Menciona documentos, formularios o aprobaciones requeridas
- Indica puntos de control y validación
- Proporciona consejos para agilizar el proceso
- Señala errores comunes a evitar

GUÍA DE PROCESO:""",
                "max_tokens": 450
            },
            
            "politicas": {
                "name": "Políticas Organizacionales",
                "description": "Template para consultas sobre políticas, cumplimiento y normativas",
                "template": """Eres un especialista en políticas organizacionales que ayuda a empleados a entender y cumplir con las normativas de la empresa.

POLÍTICAS RELEVANTES:
{context}

CONSULTA SOBRE POLÍTICA: {question}

INSTRUCCIONES:
- Explica la política de manera clara y comprensible
- Incluye el propósito y beneficios de la política
- Detalla obligaciones y responsabilidades del empleado
- Menciona consecuencias del incumplimiento si es relevante
- Proporciona ejemplos prácticos de aplicación
- Indica a quién contactar para aclaraciones adicionales

EXPLICACIÓN DE POLÍTICA:""",
                "max_tokens": 400
            },
            
            "informacion": {
                "name": "Información General",
                "description": "Template para consultas sobre información general de la empresa",
                "template": """Eres un representante de la organización que proporciona información general sobre la empresa, su estructura y operaciones.

INFORMACIÓN ORGANIZACIONAL:
{context}

PREGUNTA SOBRE LA EMPRESA: {question}

INSTRUCCIONES:
- Proporciona información precisa y actualizada sobre la organización
- Incluye datos relevantes como estructura, ubicaciones, contactos
- Mantén un tono institucional pero accesible
- Destaca aspectos positivos de la cultura organizacional
- Proporciona contexto histórico si es relevante
- Dirige a recursos adicionales cuando sea apropiado

INFORMACIÓN INSTITUCIONAL:""",
                "max_tokens": 350
            },
            
            "escalamiento": {
                "name": "Escalamiento",
                "description": "Template para casos que requieren escalamiento a especialistas",
                "template": """La consulta del usuario requiere atención especializada que va más allá de la información disponible en la base de conocimiento.

CONSULTA ORIGINAL: {question}

CONTEXTO DISPONIBLE:
{context}

INSTRUCCIONES:
- Reconoce la limitación para responder completamente
- Proporciona la información parcial disponible si es útil
- Dirige al usuario al departamento o especialista apropiado
- Incluye información de contacto específica
- Sugiere preparar información adicional para la consulta
- Mantén un tono profesional y servicial

RESPUESTA DE ESCALAMIENTO:""",
                "max_tokens": 300
            }
        }
    
    def get_prompt(self, classification: str, question: str, context: str) -> str:
        """
        Obtener prompt formateado basado en la clasificación
        
        Args:
            classification: Tipo de consulta clasificada
            question: Pregunta del usuario
            context: Contexto relevante de la base de conocimiento
            
        Returns:
            Prompt formateado listo para el modelo
        """
        try:
            # Mapear clasificación a template
            template_key = self._map_classification_to_template(classification)
            
            # Obtener template
            template_info = self.templates.get(template_key, self.templates["general"])
            template = template_info["template"]
            
            # Formatear template con variables
            formatted_prompt = template.format(
                question=question,
                context=context if context.strip() else "No hay información específica disponible en la base de conocimiento."
            )
            
            return formatted_prompt
            
        except Exception as e:
            self.logger.error(f"Error formateando prompt: {e}")
            # Fallback a template general
            return self._get_fallback_prompt(question, context)
    
    def _map_classification_to_template(self, classification: str) -> str:
        """Mapear clasificación de ML a template de prompt"""
        classification_lower = classification.lower()
        
        if "recurso" in classification_lower or "rrhh" in classification_lower or "humano" in classification_lower:
            return "recursos_humanos"
        elif "tecnolog" in classification_lower or "sistema" in classification_lower or "software" in classification_lower:
            return "tecnologia"
        elif "proceso" in classification_lower or "procedimiento" in classification_lower:
            return "procesos"
        elif "politic" in classification_lower or "norma" in classification_lower:
            return "politicas"
        elif "empresa" in classification_lower or "organizac" in classification_lower or "general" in classification_lower:
            return "informacion"
        elif "escalamiento" in classification_lower or "complejo" in classification_lower:
            return "escalamiento"
        else:
            return "general"
    
    def _get_fallback_prompt(self, question: str, context: str) -> str:
        """Prompt de respaldo en caso de error"""
        return f"""Responde la siguiente pregunta basándote en el contexto proporcionado:

CONTEXTO: {context}

PREGUNTA: {question}

Proporciona una respuesta útil y profesional."""
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Obtener información de todos los templates"""
        return {
            key: {
                "name": template["name"],
                "description": template["description"],
                "max_tokens": template.get("max_tokens", 400)
            }
            for key, template in self.templates.items()
        }
    
    def get_template_info(self, template_key: str) -> Dict[str, Any]:
        """Obtener información específica de un template"""
        return self.templates.get(template_key, {})
    
    def add_custom_template(self, key: str, name: str, description: str, 
                           template: str, max_tokens: int = 400):
        """Agregar template personalizado"""
        self.templates[key] = {
            "name": name,
            "description": description,
            "template": template,
            "max_tokens": max_tokens
        }
        
        self.logger.info(f"Template personalizado agregado: {key}")
    
    def get_prompt_with_examples(self, classification: str, question: str, 
                                context: str, examples: list = None) -> str:
        """
        Obtener prompt con ejemplos de respuestas (few-shot learning)
        
        Args:
            classification: Tipo de consulta
            question: Pregunta del usuario
            context: Contexto de la base de conocimiento
            examples: Lista de ejemplos pregunta-respuesta
            
        Returns:
            Prompt con ejemplos incluidos
        """
        base_prompt = self.get_prompt(classification, question, context)
        
        if not examples:
            return base_prompt
        
        # Agregar ejemplos al prompt
        examples_text = "\n\nEJEMPLOS DE RESPUESTAS SIMILARES:\n"
        for i, example in enumerate(examples, 1):
            examples_text += f"\nEjemplo {i}:\n"
            examples_text += f"Pregunta: {example.get('question', '')}\n"
            examples_text += f"Respuesta: {example.get('answer', '')}\n"
        
        # Insertar ejemplos antes de la respuesta final
        prompt_parts = base_prompt.split("RESPUESTA")
        if len(prompt_parts) == 2:
            return prompt_parts[0] + examples_text + "\n\nRESPUESTA" + prompt_parts[1]
        else:
            return base_prompt + examples_text

