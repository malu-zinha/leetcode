"""Busca as listas de problemas em fontes públicas e escreve os JSONs de listas/.

Uso (na raiz do repositório):
    python3 scripts/importar_listas.py                    # Blind 75, NeetCode 150, Top Interview 150
    python3 scripts/importar_listas.py --roadmap          # + o roadmap completo do NeetCode
    python3 scripts/importar_listas.py --plano leetcode-75 --nome "LeetCode 75" --ordem 4

Fontes:
    - NeetCode:  .problemSiteData.json do repo neetcode-gh/leetcode (categoria, dificuldade, vídeo)
    - LeetCode:  studyPlanV2Detail do GraphQL público (qualquer study plan oficial)

O gerador do README não conhece lista nenhuma: ele lê o que estiver em listas/*.json.
"""

import argparse
import json
import re
import ssl
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LISTAS = RAIZ / "listas"

NEETCODE_DATA = "https://raw.githubusercontent.com/neetcode-gh/leetcode/main/.problemSiteData.json"
LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

NAVEGADOR = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

DIFICULDADES = {"easy": "E", "medium": "M", "hard": "H"}

# Os study plans do LeetCode agrupam com outros nomes. Para o README somar tudo nas
# mesmas seções, os problemas que o NeetCode não conhece caem na categoria equivalente.
GRUPOS_EQUIVALENTES = {
    "Array / String": "Arrays & Hashing",
    "Hashmap": "Arrays & Hashing",
    "Matrix": "Math & Geometry",
    "Math": "Math & Geometry",
    "Binary Tree General": "Trees",
    "Binary Tree BFS": "Trees",
    "Binary Search Tree": "Trees",
    "Graph General": "Graphs",
    "Graph BFS": "Graphs",
    "Trie": "Tries",
    "Heap": "Heap / Priority Queue",
    "Kadane's Algorithm": "Greedy",
    "1D DP": "1-D Dynamic Programming",
    "Multidimensional DP": "2-D Dynamic Programming",
    "Divide & Conquer": "Binary Search",
}


def contexto_ssl():
    """O Python do python.org no macOS não usa os certificados do sistema."""
    try:
        import certifi
    except ImportError:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def baixar(url, dados=None, cabecalhos=None):
    corpo = json.dumps(dados).encode() if dados else None
    pedido = urllib.request.Request(url, data=corpo, headers=cabecalhos or {})
    pedido.add_header("User-Agent", NAVEGADOR)
    with urllib.request.urlopen(pedido, timeout=60, context=contexto_ssl()) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ------------------------------------------------------------------ NeetCode

def carregar_neetcode():
    """Devolve {numero: problema} com tudo que o NeetCode sabe sobre cada problema."""
    catalogo = {}
    for item in baixar(NEETCODE_DATA):
        codigo = item.get("code") or ""
        if not re.match(r"^\d+-", codigo):
            continue
        numero = int(codigo.split("-")[0])
        catalogo[numero] = {
            "numero": numero,
            "titulo": item["problem"],
            "slug": item["link"].strip("/"),
            "dificuldade": DIFICULDADES[item["difficulty"].lower()],
            "categoria": item["pattern"],
            "video": item.get("video") or None,
            "premium": bool(item.get("premium")),
            "blind75": bool(item.get("blind75")),
            "neetcode150": bool(item.get("neetcode150")),
        }
    return catalogo


# ------------------------------------------------------------------ LeetCode

CONSULTA_PLANO = """
query studyPlanDetail($slug: String!) {
  studyPlanV2Detail(planSlug: $slug) {
    name
    planSubGroups { name questions { id title titleSlug difficulty } }
  }
}
"""


def carregar_plano(slug):
    """Devolve (nome, [problema]) de um study plan oficial do LeetCode."""
    resposta = baixar(
        LEETCODE_GRAPHQL,
        {"query": CONSULTA_PLANO, "variables": {"slug": slug}},
        {"Content-Type": "application/json", "Referer": f"https://leetcode.com/studyplan/{slug}/"},
    )
    if resposta.get("errors"):
        raise SystemExit(f"LeetCode devolveu erro para '{slug}': {resposta['errors']}")
    plano = (resposta.get("data") or {}).get("studyPlanV2Detail")
    if not plano:
        raise SystemExit(f"Study plan '{slug}' não encontrado.")

    problemas = []
    for grupo in plano["planSubGroups"]:
        for questao in grupo["questions"]:
            problemas.append({
                "numero": int(questao["id"]),
                "titulo": questao["title"],
                "slug": questao["titleSlug"],
                "dificuldade": DIFICULDADES[questao["difficulty"].lower()],
                "categoria": grupo["name"],
            })
    return plano["name"], problemas


# -------------------------------------------------------------------- escrita

def por_categoria(problemas):
    """Agrupa mantendo a ordem de aparição, como no roadmap original."""
    ordenados = []
    for categoria in dict.fromkeys(p["categoria"] for p in problemas):
        ordenados += [p for p in problemas if p["categoria"] == categoria]
    return ordenados


def limpar(problema):
    campos = ("numero", "titulo", "slug", "dificuldade", "categoria", "video", "premium")
    return {c: problema[c] for c in campos if problema.get(c)}


def escrever(arquivo, nome, link, ordem, problemas):
    LISTAS.mkdir(exist_ok=True)
    conteudo = {
        "nome": nome,
        "link": link,
        "ordem": ordem,
        "problemas": [limpar(p) for p in por_categoria(problemas)],
    }
    caminho = LISTAS / f"{arquivo}.json"
    caminho.write_text(json.dumps(conteudo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {caminho.relative_to(RAIZ)}: {len(problemas)} problemas")
    return conteudo


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--roadmap", action="store_true", help="também gera o roadmap completo do NeetCode")
    ap.add_argument("--plano", help="slug de um study plan do LeetCode, ex: leetcode-75")
    ap.add_argument("--nome", help="nome da lista do --plano (padrão: o nome que o LeetCode devolve)")
    ap.add_argument("--ordem", type=int, default=4, help="posição do --plano na sua fila de estudo")
    args = ap.parse_args()

    print("Baixando dados do NeetCode...")
    catalogo = carregar_neetcode()
    todos = list(catalogo.values())

    blind75 = [p for p in todos if p["blind75"]]
    neetcode150 = [p for p in todos if p["neetcode150"]]
    assert len(blind75) == 75, f"Blind 75 veio com {len(blind75)} problemas"
    assert len(neetcode150) == 150, f"NeetCode 150 veio com {len(neetcode150)} problemas"
    assert {p["numero"] for p in blind75} <= {p["numero"] for p in neetcode150}, \
        "tem problema na Blind 75 fora da NeetCode 150"

    escrever("blind75", "Blind 75", "https://neetcode.io/practice?tab=blind75", 1, blind75)
    escrever("neetcode150", "NeetCode 150", "https://neetcode.io/practice?tab=neetcode150", 2, neetcode150)

    if args.roadmap:
        roadmap = [p for p in todos if p["categoria"] != "JavaScript"]
        escrever("neetcode-roadmap", "NeetCode Roadmap", "https://neetcode.io/roadmap", 9, roadmap)

    planos = [(args.plano, args.nome, args.ordem)] if args.plano else [
        ("top-interview-150", "Top Interview 150", 3),
    ]
    for slug, nome, ordem in planos:
        print(f"Baixando o study plan '{slug}' do LeetCode...")
        nome_oficial, problemas = carregar_plano(slug)
        for problema in problemas:
            # a categoria do NeetCode vale mais: mantém as seções do README iguais entre as listas
            conhecido = catalogo.get(problema["numero"])
            if conhecido:
                problema["categoria"] = conhecido["categoria"]
                problema["video"] = conhecido["video"]
                problema["premium"] = conhecido["premium"]
            else:
                problema["categoria"] = GRUPOS_EQUIVALENTES.get(problema["categoria"], problema["categoria"])
        escrever(slug, nome or nome_oficial, f"https://leetcode.com/studyplan/{slug}/", ordem, problemas)

    print("Listas atualizadas!")


if __name__ == "__main__":
    main()
