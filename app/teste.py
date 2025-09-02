import os
import json
import requests
from uuid import uuid4
from requests.exceptions import RequestException, Timeout, ConnectionError

# ========================= Config =========================
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# e-mails únicos (evita duplicidade)
_suffix = uuid4().hex[:6]
USER1 = {"nome": "User1", "email": f"user1_{_suffix}@example.com", "senha": "senha123"}
USER2 = {"nome": "User2", "email": f"user2_{_suffix}@example.com", "senha": "senha123"}
ADMIN = {"nome": "Admin", "email": f"admin_{_suffix}@example.com", "senha": "senha123", "perfil": "ADMIN"}

SENSITIVE_HEADERS = {"authorization"}
SENSITIVE_KEYS = {"senha", "password", "token", "access_token", "refresh_token"}

DELIM = "\n" + ("-" * 88) + "\n"  # delimitador entre testes

# ========================= Utilitários =========================
def _mask_dict(d):
    if not isinstance(d, dict):
        return d
    out = {}
    for k, v in d.items():
        lk = k.lower()
        if lk in SENSITIVE_HEADERS or lk in SENSITIVE_KEYS:
            out[k] = "***"
        elif isinstance(v, dict):
            out[k] = _mask_dict(v)
        elif isinstance(v, list):
            out[k] = [_mask_dict(x) for x in v]
        else:
            out[k] = v
    return out

def status(resp):
    return resp.status_code if isinstance(resp, requests.Response) else "NO_RESPONSE"

def get_json(resp):
    if not isinstance(resp, requests.Response):
        return None
    try:
        return resp.json()
    except ValueError:
        return None

def send(method, path, *, json_data=None, headers=None):
    """Único ponto de saída HTTP. Retorna (resp, full_url, method)."""
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.request(method.upper(), url, json=json_data, headers=headers, timeout=8)
        return resp, url, method.upper()
    except (RequestException, Timeout, ConnectionError):
        return None, url, method.upper()

def print_test_block(title, method, url, headers, json_sent, resp, expected_text, passed):
    # título
    print(f"\n🧪 {title}")
    # requisição
    print("requisição:")
    print(f"  método: {method}")
    print(f"  url: {url}")
    print(f"  cabeçalho inserido: {_mask_dict(headers) if headers else None}")
    print(f"  dados inseridos em json: {_mask_dict(json_sent) if json_sent is not None else None}")
    # resposta
    if isinstance(resp, requests.Response):
        print("resposta:")
        print(f"  status code: {resp.status_code}")
        body = get_json(resp)
        if body is None:
            # se não for json, mostre texto até 800 chars
            txt = resp.text or ""
            if len(txt) > 800: txt = txt[:800] + "…"
            print(f"  dados em json: None (body text resumido abaixo)")
            print(f"  body(text): {txt}")
        else:
            print(f"  dados em json: {_mask_dict(body)}")
    else:
        print("resposta:")
        print("  status code: NO_RESPONSE")
        print("  dados em json: None")

    # esperado + resultado
    print("[ESPERADO]")
    print(f"  {expected_text}")
    print("[RESULTADO]")
    print(f"  {'✅ SUCESSO' if passed else '❌ FALHA'}")
    print(DELIM)

# ========================= Scoreboards =========================
class Score:
    def __init__(self, total_max):
        self.total = 0
        self.total_max = total_max
    def add(self, pts, ok):
        if ok:
            self.total += pts

# ========================= Wrappers de API (somente envio) =========================
def api_create_user(payload):
    return send("POST", "/usuarios", json_data=payload)

def api_login(email, senha):
    payload = {"email": email, "senha": senha}
    return send("POST", "/auth/login", json_data=payload), payload

def api_post_message(headers, titulo, conteudo):
    payload = {"titulo": titulo, "conteudo": conteudo}
    return send("POST", "/mensagens", json_data=payload, headers=headers), payload

def api_put_message(headers, mid, **payload):
    return send("PUT", f"/mensagens/{mid}", json_data=payload, headers=headers), payload

def api_get_message(headers, mid):
    return send("GET", f"/mensagens/{mid}", headers=headers)

def api_delete_message(headers, mid):
    return send("DELETE", f"/mensagens/{mid}", headers=headers)

def api_post_comment(headers, mid, conteudo):
    payload = {"conteudo": conteudo}
    return send("POST", f"/mensagens/{mid}/comentarios", json_data=payload, headers=headers), payload

def api_put_comment(headers, mid, cid, **payload):
    return send("PUT", f"/mensagens/{mid}/comentarios/{cid}", json_data=payload, headers=headers), payload

def api_post_curtir(headers, mid):
    return send("POST", f"/mensagens/{mid}/curtir", headers=headers)

def api_get_excluidas(headers):
    return send("GET", "/mensagens/excluidas", headers=headers)

# ========================= Teste principal =========================
def main():
    print(f"=== SUÍTE DE TESTES — BASE_URL={BASE_URL} — suffix={_suffix} ===\n")

    # Pontuação
    orig = Score(total_max=30)
    alt  = Score(total_max=40)

    # ------ BLOCO ORIGINAL (30 pts) ------
    # 1) Criar três usuários - 2 user e 1 admin - (2pt 2pt 2pt)
    resp, url, met = api_create_user(USER1)
    ok = status(resp) == 201
    print_test_block("1) Criar USER1", met, url, None, USER1, resp, "201 Created", ok)
    orig.add(2, ok)

    resp, url, met = api_create_user(USER2)
    ok = status(resp) == 201
    print_test_block("2) Criar USER2", met, url, None, USER2, resp, "201 Created", ok)
    orig.add(2, ok)

    resp, url, met = api_create_user(ADMIN)
    ok = status(resp) == 201
    print_test_block("3) Criar ADMIN", met, url, None, ADMIN, resp, "201 Created", ok)
    orig.add(2, ok)

    # Autenticações (informativo – sem pontuar)
    (resp, url, met), payload = api_login(USER1["email"], USER1["senha"])
    tok_u1 = get_json(resp).get("access_token") if status(resp) == 200 and get_json(resp) else None
    print_test_block("Login USER1", met, url, None, payload, resp, "200 OK + access_token", tok_u1 is not None)

    (resp, url, met), payload = api_login(USER2["email"], USER2["senha"])
    tok_u2 = get_json(resp).get("access_token") if status(resp) == 200 and get_json(resp) else None
    print_test_block("Login USER2", met, url, None, payload, resp, "200 OK + access_token", tok_u2 is not None)

    (resp, url, met), payload = api_login(ADMIN["email"], ADMIN["senha"])
    tok_ad = get_json(resp).get("access_token") if status(resp) == 200 and get_json(resp) else None
    print_test_block("Login ADMIN", met, url, None, payload, resp, "200 OK + access_token", tok_ad is not None)

    h1 = {"Authorization": f"Bearer {tok_u1}"} if tok_u1 else None
    h2 = {"Authorization": f"Bearer {tok_u2}"} if tok_u2 else None
    ha = {"Authorization": f"Bearer {tok_ad}"} if tok_ad else None

    # 2) USER1 cria três mensagens - (2pt 2pt 2pt)
    mids = []
    for i in range(3):
        (resp, url, met), payload = api_post_message(h1, f"Título {i+1}", f"Conteúdo {i+1}")
        ok = status(resp) == 201 and get_json(resp) and get_json(resp).get("id") is not None
        if ok:
            mids.append(get_json(resp)["id"])
        print_test_block(f"{4+i}) USER1 cria mensagem {i+1}", met, url, h1, payload, resp, "201 Created + id", ok)
        orig.add(2, ok)

    target_mid = mids[0] if mids else None

    # 3) USER2 tenta editar mensagem - 3 pt (403)
    (resp, url, met), payload = api_put_message(h2, target_mid, titulo="x", conteudo="tentativa user2") if target_mid else ((None, f"{BASE_URL}/mensagens/None", "PUT"), {})
    ok = status(resp) == 403
    print_test_block("7) USER2 tenta editar mensagem", met, url, h2, payload, resp, "403 Forbidden", ok)
    orig.add(3, ok)

    # 4) USER2 cria comentário - 5pt (201)
    (resp, url, met), payload = api_post_comment(h2, target_mid, "Comentário do USER2") if target_mid else ((None, f"{BASE_URL}/mensagens/None/comentarios", "POST"), {"conteudo": "Comentário do USER2"})
    comm_id = get_json(resp).get("id") if status(resp) == 201 and get_json(resp) else None
    ok = status(resp) == 201 and comm_id is not None
    print_test_block("8) USER2 cria comentário", met, url, h2, payload, resp, "201 Created + id", ok)
    orig.add(5, ok)

    # 5) USER2 altera comentário - 5pt (200)
    (resp, url, met), payload = api_put_comment(h2, target_mid, comm_id, conteudo="Comentário do USER2 (editado)") if comm_id else ((None, f"{BASE_URL}/mensagens/{target_mid}/comentarios/None", "PUT"), {"conteudo": "Comentário do USER2 (editado)"})
    ok = status(resp) == 200
    print_test_block("9) USER2 altera comentário", met, url, h2, payload, resp, "200 OK", ok)
    orig.add(5, ok)

    # 6) ADMIN deleta 1 mensagem - 2pt (204)
    del_mid = mids[2] if len(mids) >= 3 else (mids[0] if mids else None)
    resp, url, met = api_delete_message(ha, del_mid) if del_mid else (None, f"{BASE_URL}/mensagens/None", "DELETE")
    ok = status(resp) == 204
    print_test_block("10) ADMIN deleta 1 mensagem", met, url, ha, None, resp, "204 No Content", ok)
    orig.add(2, ok)

    # 7) USER1 tenta acessar mensagem apagada - 3pt (404)
    resp, url, met = api_get_message(h1, del_mid) if del_mid else (None, f"{BASE_URL}/mensagens/None", "GET")
    ok = status(resp) == 404
    print_test_block("11) USER1 tenta acessar mensagem apagada", met, url, h1, None, resp, "404 Not Found", ok)
    orig.add(3, ok)

    # ------ BLOCO ALTERAÇÕES (40 pts) ------
    like_mid = mids[1] if len(mids) >= 2 else (mids[0] if mids else None)

    # 8) curtidas inicia 0 — 5 pts
    resp, url, met = api_get_message(h1, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None", "GET")
    cur0 = get_json(resp).get("curtidas") if status(resp) == 200 and get_json(resp) else None
    ok = isinstance(cur0, int) and cur0 == 0
    print_test_block("ALT 1) GET mensagem (curtidas=0)", met, url, h1, None, resp, "200 OK + curtidas == 0", ok)
    alt.add(5, ok)

    # 9) PUT 'curtidas' não altera — 5 pts (bloquear/ignorar) + confirmar permanece 0
    (resp_put, url_put, met_put), payload = api_put_message(h1, like_mid, conteudo="mudando conteúdo", curtidas=99) if like_mid else ((None, f"{BASE_URL}/mensagens/None", "PUT"), {"conteudo": "mudando conteúdo", "curtidas": 99})
    ok_put = status(resp_put) in (200, 403, 422)
    print_test_block("ALT 2) PUT mensagem com 'curtidas' no payload", met_put, url_put, h1, payload, resp_put, "200/403/422 e servidor ignora/bloqueia 'curtidas'", ok_put)

    resp_chk, url_chk, met_chk = api_get_message(h1, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None", "GET")
    cur_after = get_json(resp_chk).get("curtidas") if status(resp_chk) == 200 and get_json(resp_chk) else None
    ok = ok_put and cur_after == 0
    print_test_block("ALT 2-verif) GET após PUT (curtidas deve continuar 0)", met_chk, url_chk, h1, None, resp_chk, "200 OK + curtidas == 0", ok)
    alt.add(5, ok)

    # 10) POST /mensagens/{id}/curtir incrementa — 5 pts (USER2 curte)
    resp, url, met = api_post_curtir(h2, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None/curtir", "POST")
    ok_like_status = status(resp) in (200, 201)
    print_test_block("ALT 3) POST /curtir", met, url, h2, None, resp, "200/201", ok_like_status)

    resp_chk, url_chk, met_chk = api_get_message(h1, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None", "GET")
    cur1 = get_json(resp_chk).get("curtidas") if status(resp_chk) == 200 and get_json(resp_chk) else None
    ok = ok_like_status and cur1 == 1
    print_test_block("ALT 3-verif) GET após curtir (curtidas=1)", met_chk, url_chk, h1, None, resp_chk, "200 OK + curtidas == 1", ok)
    alt.add(5, ok)

    # 11) admin não pode curtir — 5 pts (403)
    resp, url, met = api_post_curtir(ha, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None/curtir", "POST")
    ok = status(resp) == 403
    print_test_block("ALT 4) ADMIN tentar curtir", met, url, ha, None, resp, "403 Forbidden", ok)
    alt.add(5, ok)

    # 12) autor da mensagem não pode curtir — 5 pts (403)
    resp, url, met = api_post_curtir(h1, like_mid) if like_mid else (None, f"{BASE_URL}/mensagens/None/curtir", "POST")
    ok = status(resp) == 403
    print_test_block("ALT 5) Autor tentar curtir própria mensagem", met, url, h1, None, resp, "403 Forbidden", ok)
    alt.add(5, ok)

    # 13) /mensagens/excluidas — 10 pts (ADMIN) contém deletada
    resp, url, met = api_get_excluidas(ha)
    contains_deleted = False
    if status(resp) == 200 and isinstance(get_json(resp), list):
        ids = {item.get("id") for item in get_json(resp) if isinstance(item, dict)}
        contains_deleted = (del_mid in ids)
    ok = status(resp) == 200 and contains_deleted
    print_test_block("ALT 6) GET /mensagens/excluidas (ADMIN)", met, url, ha, None, resp, "200 OK + lista contém mensagem deletada", ok)
    alt.add(10, ok)

    # 14) somente admin pode acessar excluídas — 5 pts (USER → 403)
    resp, url, met = api_get_excluidas(h2)
    ok = status(resp) == 403
    print_test_block("ALT 7) /mensagens/excluidas com USER", met, url, h2, None, resp, "403 Forbidden", ok)
    alt.add(5, ok)

    # ========================= RESUMO FINAL (apenas no final) =========================
    print("\n" + "=" * 88)
    print("RESUMO FINAL")
    print(f"  Pontos (API ORIGINAL): {orig.total} / 30")
    print(f"  Pontos (ALTERAÇÕES):   {alt.total} / 40")
    print("=" * 88 + "\n")


if __name__ == "__main__":
    main()