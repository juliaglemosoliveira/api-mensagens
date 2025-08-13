import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5000"  # ajuste se necessário

USER_A = {"nome": "User A", "email": "user_a@example.com", "senha": "senha123"}
USER_B = {"nome": "User B", "email": "user_b@example.com", "senha": "senha123"}

def safe_call(method, url, **kwargs):
    try:
        return method(url, timeout=6, **kwargs)
    except RequestException as e:
        print(f"❌ ERRO DE REDE em {url}: {e}")
        return None

def create_user(user):
    return safe_call(requests.post, f"{BASE_URL}/usuarios", json=user)

def login(user):
    resp = safe_call(requests.post, f"{BASE_URL}/auth/login", json={
        "email": user["email"],
        "senha": user["senha"]
    })
    if resp is not None and resp.status_code == 200:
        data = resp.json()
        return data.get("access_token")
    return None

def main():
    nota = 0
    print("=== CONFORMIDADE API x APIDOC (JWT, MENSAGENS, COMENTÁRIOS) ===\n")

    # 1) Criar USER_A
    print("1) Criando USER_A ...")
    r1 = create_user(USER_A)
    if r1 is not None:
        if r1.status_code == 201:
            nota += 3
            print("   ✅ USER_A criado (201).")
        else:
            print(f"   ❌ Esperado 201, obtido: {r1.status_code}")
    else:
        print("   ❌ Sem resposta da API.")

    # 2) Criar USER_B
    print("2) Criando USER_B ...")
    r2 = create_user(USER_B)
    if r2 is not None:
        if r2.status_code == 201:
            nota += 3
            print("   ✅ USER_B criado (201).")
        else:
            print(f"   ❌ Esperado 201, obtido: {r2.status_code}")
    else:
        print("   ❌ Sem resposta da API.")
