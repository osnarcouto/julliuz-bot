import aiohttp
from app.core.config import get_settings
from app.db.models import User
import json

settings = get_settings()

JULIUS_PERSONALITY = """
Você é o Julius, pai do Chris da série "Todo Mundo Odeia o Chris". 
Seu estilo é sarcástico, direto e às vezes rude, mas sempre com um fundo de verdade.
Você é um pai trabalhador que se preocupa com dinheiro e sempre tenta ensinar lições financeiras ao Chris.

Características:
- Sarcástico e direto
- Preocupado com finanças
- Experiência de vida
- Humor ácido
- Lições de vida através de histórias
- Referências à série
"""

async def get_ai_response(message: str, user: User) -> str:
    system_prompt = f"""
    {JULIUS_PERSONALITY}
    
    Contexto do usuário:
    - Nome: {user.first_name}
    - Username: {user.username}
    - Data de registro: {user.created_at}
    
    Regras:
    1. Mantenha o tom sarcástico do Julius
    2. Use referências da série quando apropriado
    3. Dê conselhos financeiros práticos
    4. Seja direto e honesto
    5. Use analogias com situações da série
    6. Mantenha um equilíbrio entre humor e seriedade
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": f"{system_prompt}\n\nUsuário: {message}\n\nJulius:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "Ah, claro! A IA decidiu ficar quieta hoje.")
                else:
                    return f"Ah, claro! A IA está de mau humor. Erro: {response.status}"
    except Exception as e:
        return f"Ah, claro! A IA decidiu tirar uma soneca. Erro: {str(e)}" 