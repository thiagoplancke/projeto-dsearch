from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL


def mask_key(api_key):
    if not api_key:
        return "não configurada"
    if len(api_key) <= 10:
        return f"configurada, tamanho={len(api_key)}"
    return f"{api_key[:6]}...{api_key[-4:]} tamanho={len(api_key)}"


if not GEMINI_API_KEY:
    raise SystemExit(
        "GEMINI_API_KEY não encontrada. Crie um arquivo .env na raiz ou defina a variável de ambiente."
    )

print(f"GEMINI_API_KEY: {mask_key(GEMINI_API_KEY)}")
print(f"Modelo: {GEMINI_MODEL}")

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents="Responda apenas: OK",
)

print(f"Resposta Gemini: {response.text}")
