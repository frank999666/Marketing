import json
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class AIContentService:

    async def generate_content(
        self,
        platform: str,
        content_type: str,
        topic: Optional[str],
        brand_context: Dict[str, Any],
        num_variations: int = 3,
    ) -> List[dict]:
        brand_info = self._format_brand_context(brand_context)
        platform_guides = self._get_platform_guide(platform, content_type)

        prompt = f"""Eres un experto en marketing digital. Genera {num_variations} variaciones de contenido para {platform}.

Tipo de contenido: {content_type}
{"Tema: " + topic if topic else "Genera contenido atractivo y relevante."}

Información de la marca:
{brand_info}

Guías para {platform}:
{platform_guides}

Para cada variación, genera:
1. title: Título llamativo
2. body: El copy completo del post
3. hashtags: Array de 5-10 hashtags relevantes
4. cta: Llamado a la acción
5. best_time: Mejor hora sugerida para publicar

Responde en formato JSON con un array "variations"."""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un copywriter experto en marketing digital. Respondes siempre en JSON válido."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
            )

            content = json.loads(response.choices[0].message.content)
            return content.get("variations", [content])

        except Exception:
            return [{"title": "Error generating content", "body": "No se pudo generar el contenido. Intenta de nuevo.", "hashtags": [], "cta": ""}]

    async def generate_image(self, prompt: str, platform: str) -> Optional[str]:
        dimensions = self._get_image_dimensions(platform)
        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=f"Professional marketing image for social media: {prompt}. Modern, clean design, high quality.",
                size=dimensions,
                quality="hd",
                n=1,
            )
            return response.data[0].url
        except Exception:
            return None

    async def chat_assistant(
        self,
        message: str,
        company_context: Dict[str, Any],
        extra_context: Optional[Dict] = None,
    ) -> dict:
        context_str = json.dumps(company_context, indent=2, default=str)

        system_prompt = f"""Eres el Director de Marketing Digital de la empresa. Tienes acceso a los datos de la empresa y debes responder preguntas sobre marketing, estrategia, contenido y análisis.

Contexto de la empresa:
{context_str}

Instrucciones:
- Responde usando los datos reales de la empresa
- Explica el razonamiento detrás de cada recomendación
- Sé específico y accionable
- Si no tienes datos suficientes, indícalo
- Ofrece 2-3 sugerencias adicionales relacionadas"""

        messages = [{"role": "system", "content": system_prompt}]
        if extra_context:
            messages.append({"role": "user", "content": f"Contexto adicional: {json.dumps(extra_context)}"})
        messages.append({"role": "user", "content": message})

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
            )
            answer = response.choices[0].message.content

            suggestions = []
            if "ventas" in message.lower() or "sales" in message.lower():
                suggestions = ["Ver campañas activas", "Analizar tendencias", "Crear nueva campaña"]
            elif "contenido" in message.lower() or "content" in message.lower():
                suggestions = ["Generar contenido", "Ver calendario", "Analizar engagement"]
            else:
                suggestions = ["Ver analytics", "Crear campaña", "Generar reporte"]

            return {"answer": answer, "suggestions": suggestions}

        except Exception:
            return {"answer": "Disculpa, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo.", "suggestions": []}

    async def generate_campaign_strategy(
        self,
        objective: str,
        budget: float,
        target_audience: Optional[str],
        product_description: Optional[str],
        brand_context: Dict[str, Any],
    ) -> dict:
        brand_info = self._format_brand_context(brand_context)

        prompt = f"""Eres un estratega de publicidad digital. Diseña una campaña publicitaria.

Objetivo: {objective}
Presupuesto: ${budget}
{"Público objetivo: " + target_audience if target_audience else "Define el público ideal."}
{"Producto/Servicio: " + product_description if product_description else "Basándote en la marca."}

Marca:
{brand_info}

Genera:
1. campaign_name: Nombre de la campaña
2. platform: Plataforma recomendada (instagram, facebook, tiktok, twitter)
3. strategy_summary: Resumen de la estrategia
4. audience_config: Configuración de audiencia (edad, intereses, ubicación)
5. creatives: Array de 2-3 variaciones de anuncios con:
   - copy: Texto del anuncio
   - headline: Título
   - description: Descripción
   - cta: Llamado a la acción
   - variant: A/B testing label (A, B, C)

Responde en JSON."""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en publicidad digital. Respondes en JSON válido."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            return json.loads(response.choices[0].message.content)

        except Exception:
            return {
                "campaign_name": "Campaña Generada",
                "platform": "instagram",
                "strategy_summary": "No se pudo generar la estrategia. Intenta de nuevo.",
                "creatives": [],
            }

    def _format_brand_context(self, context: Dict[str, Any]) -> str:
        if not context:
            return "No hay información de marca disponible."
        parts = []
        if context.get("industry"):
            parts.append(f"Industria: {context['industry']}")
        if context.get("tone"):
            parts.append(f"Tono: {context['tone']}")
        if context.get("values"):
            parts.append(f"Valores: {', '.join(context['values'])}")
        if context.get("target_audience"):
            parts.append(f"Público objetivo: {context['target_audience']}")
        return "\n".join(parts) if parts else "Información de marca no disponible."

    def _get_platform_guide(self, platform: str, content_type: str) -> str:
        guides = {
            "instagram": {
                "post": "Máximo 2200 caracteres. Usa emojis. 5-10 hashtags. CTA claro. Fotos de alta calidad.",
                "reel": "15-60 segundos. Hook en los primeros 3 segundos. Texto en pantalla. Música trending.",
                "story": "Vertical 9:16. Máximo 15 segundos. Stickers, encuestas. CTA con swipe up.",
                "carousel": "Máximo 10 slides. Primero slide impactante. Último con CTA. Educación o storytelling.",
            },
            "tiktok": {
                "post": "Video 15-60 segundos. Hook fuerte. Tendencias y sonidos. Auténtico y natural.",
                "reel": "Tutorial, behind the scenes, o entretenimiento. Texto en pantalla.",
            },
            "twitter": {
                "tweet": "Máximo 280 caracteres. Directo. Usa hashtags relevantes. Hilos para contenido largo.",
                "thread": "Primero tweet impactante. 5-10 tweets. Cada uno con valor. CTA al final.",
            },
        }
        platform_guides = guides.get(platform, {})
        return platform_guides.get(content_type, "Sigue las mejores prácticas de la plataforma.")

    def _get_image_dimensions(self, platform: str) -> str:
        dimensions = {
            "instagram": "1024x1024",
            "tiktok": "1024x1792",
            "twitter": "1024x1024",
            "facebook": "1200x630",
            "linkedin": "1200x627",
        }
        return dimensions.get(platform, "1024x1024")
