"""
Servicio GenAI - Modelo de Lenguaje API-based
Implementa la funcionalidad de generación de respuestas usando OpenAI GPT
"""

import openai
import os
from typing import Optional
import asyncio
import logging

class GenAIService:
    """Servicio para interactuar con modelos de lenguaje generativo"""
    
    def __init__(self):
        """Inicializar el servicio GenAI"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Configurar cliente OpenAI si hay API key
        if self.api_key and self.api_key != "sk-demo-key-for-testing":
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.logger.warning("API key de OpenAI no configurada, usando respuestas simuladas")
    
    def is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.client is not None or self.api_key == "sk-demo-key-for-testing"
    
    async def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generar respuesta usando el modelo de lenguaje
        
        Args:
            prompt: El prompt completo para el modelo
            max_tokens: Número máximo de tokens en la respuesta
            
        Returns:
            Respuesta generada por el modelo
        """
        try:
            if self.client:
                # Usar OpenAI real
                response = await self._call_openai_api(prompt, max_tokens)
            else:
                # Usar respuesta simulada para demo
                response = await self._generate_mock_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return f"Lo siento, hubo un error procesando tu pregunta: {str(e)}"
    
    async def _call_openai_api(self, prompt: str, max_tokens: int) -> str:
        """Llamar a la API de OpenAI"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Eres un asistente de IA útil y conocedor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error en API de OpenAI: {e}")
            raise
    
    async def _generate_mock_response(self, prompt: str) -> str:
        """
        Generar respuesta simulada para demostración
        Analiza el prompt y genera una respuesta contextual
        """
        # Simular tiempo de procesamiento
        await asyncio.sleep(0.5)
        
        prompt_lower = prompt.lower()
        
        # Respuestas basadas en palabras clave
        if "saludo" in prompt_lower or "hola" in prompt_lower:
            return "¡Hola! Soy tu asistente de IA. ¿En qué puedo ayudarte hoy?"
        
        elif "empresa" in prompt_lower or "organización" in prompt_lower:
            return """Basándome en la información disponible, puedo ayudarte con consultas sobre:
            
• Políticas y procedimientos organizacionales
• Recursos humanos y beneficios
• Procesos internos y flujos de trabajo
• Información general de la empresa
• Contactos y directorios internos

¿Hay algo específico sobre la organización que te gustaría saber?"""
        
        elif "política" in prompt_lower or "procedimiento" in prompt_lower:
            return """Las políticas y procedimientos de la organización están diseñados para:

1. **Garantizar la consistencia** en las operaciones diarias
2. **Cumplir con regulaciones** aplicables
3. **Proteger a empleados y clientes**
4. **Optimizar procesos** y eficiencia

Para consultas específicas sobre políticas, puedo ayudarte a encontrar la información relevante en nuestra base de conocimiento."""
        
        elif "recurso" in prompt_lower or "rrhh" in prompt_lower or "humano" in prompt_lower:
            return """El departamento de Recursos Humanos gestiona:

• **Beneficios y compensaciones**: Seguros, vacaciones, bonos
• **Desarrollo profesional**: Capacitaciones, evaluaciones
• **Políticas laborales**: Horarios, código de conducta
• **Procesos administrativos**: Solicitudes, permisos

¿Necesitas información específica sobre alguno de estos temas?"""
        
        elif "tecnología" in prompt_lower or "sistema" in prompt_lower or "software" in prompt_lower:
            return """Nuestros sistemas tecnológicos incluyen:

• **Plataformas de colaboración**: Teams, Slack, correo electrónico
• **Sistemas empresariales**: CRM, ERP, gestión de documentos
• **Herramientas de productividad**: Office 365, Google Workspace
• **Seguridad**: VPN, autenticación multifactor

Para soporte técnico específico, puedo dirigirte al equipo apropiado."""
        
        elif "proceso" in prompt_lower or "flujo" in prompt_lower:
            return """Los procesos organizacionales están optimizados para:

1. **Eficiencia operativa**: Reducir tiempos y costos
2. **Calidad consistente**: Mantener estándares altos
3. **Trazabilidad**: Seguimiento y auditoría
4. **Mejora continua**: Optimización basada en datos

¿Te interesa conocer algún proceso específico?"""
        
        elif "ayuda" in prompt_lower or "soporte" in prompt_lower:
            return """Estoy aquí para ayudarte con:

✓ **Consultas generales** sobre la organización
✓ **Búsqueda de información** en nuestra base de conocimiento
✓ **Direccionamiento** a los departamentos correctos
✓ **Explicación de procesos** y procedimientos
✓ **Acceso a recursos** y documentación

¿Qué tipo de ayuda necesitas específicamente?"""
        
        else:
            # Respuesta genérica inteligente
            return f"""He analizado tu consulta y, basándome en la información disponible, puedo ofrecerte una respuesta contextual.

Para brindarte la información más precisa y útil, me gustaría entender mejor tu consulta. ¿Podrías proporcionar más detalles sobre:

• El contexto específico de tu pregunta
• El tipo de información que buscas
• El departamento o área relacionada

Esto me permitirá acceder a la información más relevante de nuestra base de conocimiento y proporcionarte una respuesta más completa y útil."""
    
    async def generate_summary(self, text: str, max_length: int = 100) -> str:
        """Generar resumen de un texto"""
        prompt = f"""Genera un resumen conciso del siguiente texto en máximo {max_length} palabras:

{text}

Resumen:"""
        
        return await self.generate_response(prompt, max_tokens=150)
    
    async def answer_with_context(self, question: str, context: str) -> str:
        """Responder pregunta con contexto específico"""
        prompt = f"""Basándote en el siguiente contexto, responde la pregunta de manera precisa y útil:

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""
        
        return await self.generate_response(prompt, max_tokens=400)

