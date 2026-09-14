"""Gera o README.md e os cards de estatísticas a partir das soluções.

Uso (na raiz do repositório):
    python3 docs/atualizar_readme.py

Cada solução é identificada pela primeira linha do arquivo, ex: "# 1. Two Sum".
"""

import math
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
ASSETS = DOCS / "assets"

LINK_BLIND_75 = "https://neetcode.io/practice?tab=blind75"
LINK_NEETCODE_150 = "https://neetcode.io/practice?tab=neetcode150"

# código: (nome, emoji)
DIFICULDADES = {
    "E": ("Fácil", "🟢"),
    "M": ("Médio", "🟡"),
    "H": ("Difícil", "🔴"),
}

# NeetCode 150 por categoria: (número, título, dificuldade)
NEETCODE_150 = {
    "Arrays & Hashing": [
        (217, "Contains Duplicate", "E"),
        (242, "Valid Anagram", "E"),
        (1, "Two Sum", "E"),
        (49, "Group Anagrams", "M"),
        (347, "Top K Frequent Elements", "M"),
        (271, "Encode and Decode Strings", "M"),
        (238, "Product of Array Except Self", "M"),
        (36, "Valid Sudoku", "M"),
        (128, "Longest Consecutive Sequence", "M"),
    ],
    "Two Pointers": [
        (125, "Valid Palindrome", "E"),
        (167, "Two Sum II - Input Array Is Sorted", "M"),
        (15, "3Sum", "M"),
        (11, "Container With Most Water", "M"),
        (42, "Trapping Rain Water", "H"),
    ],
    "Sliding Window": [
        (121, "Best Time to Buy and Sell Stock", "E"),
        (3, "Longest Substring Without Repeating Characters", "M"),
        (424, "Longest Repeating Character Replacement", "M"),
        (567, "Permutation in String", "M"),
        (76, "Minimum Window Substring", "H"),
        (239, "Sliding Window Maximum", "H"),
    ],
    "Stack": [
        (20, "Valid Parentheses", "E"),
        (155, "Min Stack", "M"),
        (150, "Evaluate Reverse Polish Notation", "M"),
        (22, "Generate Parentheses", "M"),
        (739, "Daily Temperatures", "M"),
        (853, "Car Fleet", "M"),
        (84, "Largest Rectangle in Histogram", "H"),
    ],
    "Binary Search": [
        (704, "Binary Search", "E"),
        (74, "Search a 2D Matrix", "M"),
        (875, "Koko Eating Bananas", "M"),
        (153, "Find Minimum in Rotated Sorted Array", "M"),
        (33, "Search in Rotated Sorted Array", "M"),
        (981, "Time Based Key-Value Store", "M"),
        (4, "Median of Two Sorted Arrays", "H"),
    ],
    "Linked List": [
        (206, "Reverse Linked List", "E"),
        (21, "Merge Two Sorted Lists", "E"),
        (141, "Linked List Cycle", "E"),
        (143, "Reorder List", "M"),
        (19, "Remove Nth Node From End of List", "M"),
        (138, "Copy List with Random Pointer", "M"),
        (2, "Add Two Numbers", "M"),
        (287, "Find the Duplicate Number", "M"),
        (146, "LRU Cache", "M"),
        (23, "Merge k Sorted Lists", "H"),
        (25, "Reverse Nodes in k-Group", "H"),
    ],
    "Trees": [
        (226, "Invert Binary Tree", "E"),
        (104, "Maximum Depth of Binary Tree", "E"),
        (543, "Diameter of Binary Tree", "E"),
        (110, "Balanced Binary Tree", "E"),
        (100, "Same Tree", "E"),
        (572, "Subtree of Another Tree", "E"),
        (235, "Lowest Common Ancestor of a Binary Search Tree", "M"),
        (102, "Binary Tree Level Order Traversal", "M"),
        (199, "Binary Tree Right Side View", "M"),
        (1448, "Count Good Nodes in Binary Tree", "M"),
        (98, "Validate Binary Search Tree", "M"),
        (230, "Kth Smallest Element in a BST", "M"),
        (105, "Construct Binary Tree from Preorder and Inorder Traversal", "M"),
        (124, "Binary Tree Maximum Path Sum", "H"),
        (297, "Serialize and Deserialize Binary Tree", "H"),
    ],
    "Tries": [
        (208, "Implement Trie (Prefix Tree)", "M"),
        (211, "Design Add and Search Words Data Structure", "M"),
        (212, "Word Search II", "H"),
    ],
    "Heap / Priority Queue": [
        (703, "Kth Largest Element in a Stream", "E"),
        (1046, "Last Stone Weight", "E"),
        (973, "K Closest Points to Origin", "M"),
        (215, "Kth Largest Element in an Array", "M"),
        (621, "Task Scheduler", "M"),
        (355, "Design Twitter", "M"),
        (295, "Find Median from Data Stream", "H"),
    ],
    "Backtracking": [
        (78, "Subsets", "M"),
        (39, "Combination Sum", "M"),
        (46, "Permutations", "M"),
        (90, "Subsets II", "M"),
        (40, "Combination Sum II", "M"),
        (79, "Word Search", "M"),
        (131, "Palindrome Partitioning", "M"),
        (17, "Letter Combinations of a Phone Number", "M"),
        (51, "N-Queens", "H"),
    ],
    "Graphs": [
        (200, "Number of Islands", "M"),
        (695, "Max Area of Island", "M"),
        (133, "Clone Graph", "M"),
        (286, "Walls and Gates", "M"),
        (994, "Rotting Oranges", "M"),
        (417, "Pacific Atlantic Water Flow", "M"),
        (130, "Surrounded Regions", "M"),
        (207, "Course Schedule", "M"),
        (210, "Course Schedule II", "M"),
        (684, "Redundant Connection", "M"),
        (323, "Number of Connected Components in an Undirected Graph", "M"),
        (261, "Graph Valid Tree", "M"),
        (127, "Word Ladder", "H"),
    ],
    "Advanced Graphs": [
        (1584, "Min Cost to Connect All Points", "M"),
        (743, "Network Delay Time", "M"),
        (787, "Cheapest Flights Within K Stops", "M"),
        (332, "Reconstruct Itinerary", "H"),
        (778, "Swim in Rising Water", "H"),
        (269, "Alien Dictionary", "H"),
    ],
    "1-D Dynamic Programming": [
        (70, "Climbing Stairs", "E"),
        (746, "Min Cost Climbing Stairs", "E"),
        (198, "House Robber", "M"),
        (213, "House Robber II", "M"),
        (5, "Longest Palindromic Substring", "M"),
        (647, "Palindromic Substrings", "M"),
        (91, "Decode Ways", "M"),
        (322, "Coin Change", "M"),
        (152, "Maximum Product Subarray", "M"),
        (139, "Word Break", "M"),
        (300, "Longest Increasing Subsequence", "M"),
        (416, "Partition Equal Subset Sum", "M"),
    ],
    "2-D Dynamic Programming": [
        (62, "Unique Paths", "M"),
        (1143, "Longest Common Subsequence", "M"),
        (309, "Best Time to Buy and Sell Stock with Cooldown", "M"),
        (518, "Coin Change II", "M"),
        (494, "Target Sum", "M"),
        (97, "Interleaving String", "M"),
        (72, "Edit Distance", "M"),
        (329, "Longest Increasing Path in a Matrix", "H"),
        (115, "Distinct Subsequences", "H"),
        (312, "Burst Balloons", "H"),
        (10, "Regular Expression Matching", "H"),
    ],
    "Greedy": [
        (53, "Maximum Subarray", "M"),
        (55, "Jump Game", "M"),
        (45, "Jump Game II", "M"),
        (134, "Gas Station", "M"),
        (846, "Hand of Straights", "M"),
        (1899, "Merge Triplets to Form Target Triplet", "M"),
        (763, "Partition Labels", "M"),
        (678, "Valid Parenthesis String", "M"),
    ],
    "Intervals": [
        (252, "Meeting Rooms", "E"),
        (57, "Insert Interval", "M"),
        (56, "Merge Intervals", "M"),
        (435, "Non-overlapping Intervals", "M"),
        (253, "Meeting Rooms II", "M"),
        (1851, "Minimum Interval to Include Each Query", "H"),
    ],
    "Math & Geometry": [
        (202, "Happy Number", "E"),
        (66, "Plus One", "E"),
        (48, "Rotate Image", "M"),
        (54, "Spiral Matrix", "M"),
        (73, "Set Matrix Zeroes", "M"),
        (50, "Pow(x, n)", "M"),
        (43, "Multiply Strings", "M"),
        (2013, "Detect Squares", "M"),
    ],
    "Bit Manipulation": [
        (136, "Single Number", "E"),
        (191, "Number of 1 Bits", "E"),
        (338, "Counting Bits", "E"),
        (190, "Reverse Bits", "E"),
        (268, "Missing Number", "E"),
        (371, "Sum of Two Integers", "M"),
        (7, "Reverse Integer", "M"),
    ],
}

# a Blind 75 inteira está dentro da NeetCode 150 (marcada com ⭐ no README)
BLIND_75 = {
    217, 242, 1, 49, 347, 271, 238, 128,
    125, 15, 11,
    121, 3, 424, 76,
    20,
    153, 33,
    206, 21, 141, 143, 19, 23,
    226, 104, 100, 572, 235, 102, 98, 230, 105, 124, 297,
    208, 211, 212,
    295,
    39, 79,
    200, 133, 417, 207, 323, 261,
    269,
    70, 198, 213, 5, 647, 91, 322, 152, 139, 300,
    62, 1143,
    53, 55,
    252, 57, 56, 435, 253,
    48, 54, 73,
    191, 338, 190, 268, 371,
}

ROSA = "f58fc4"
AZUL = "8dd3f7"

TEMAS = {
    "light": {
        "fundo": "#ffffff", "borda": "#f6d9e8", "texto": "#1f2328",
        "suave": "#6e6a78", "trilho": "#fcedf5",
        "rosa": f"#{ROSA}", "azul": f"#{AZUL}",
    },
    "dark": {
        "fundo": "#0d1117", "borda": "#30363d", "texto": "#e6edf3",
        "suave": "#8d96a0", "trilho": "#232833",
        "rosa": "#ffa9d4", "azul": "#a3dcfb",
    },
}


def slug(titulo):
    s = re.sub(r"[^a-z0-9 -]", "", titulo.lower())
    return re.sub(r"[ -]+", "-", s).strip("-")


def link_leetcode(titulo):
    return f"https://leetcode.com/problems/{slug(titulo)}/"


def carregar_problemas():
    problemas = []
    for categoria, itens in NEETCODE_150.items():
        for numero, titulo, dificuldade in itens:
            problemas.append({
                "numero": numero,
                "titulo": titulo,
                "dificuldade": dificuldade,
                "categoria": categoria,
                "blind75": numero in BLIND_75,
                "arquivo": None,
            })
    assert len(problemas) == 150, f"NeetCode 150 com {len(problemas)} problemas"
    assert sum(p["blind75"] for p in problemas) == 75, "Blind 75 incompleta"
    return problemas


def ler_cabecalho(arquivo):
    """Lê '# 1. Two Sum' da primeira linha não vazia -> (1, 'Two Sum')."""
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            m = re.match(r"#\s*(\d+)\.\s*(.+)", linha.strip())
            return (int(m.group(1)), m.group(2).strip()) if m else (None, None)
    return None, None


def marcar_resolvidos(problemas):
    """Marca os problemas da lista e devolve as soluções que estão fora dela."""
    por_numero = {p["numero"]: p for p in problemas}
    por_slug = {slug(p["titulo"]): p for p in problemas}
    extras = []

    for arquivo in sorted(RAIZ.glob("*/*.py")):
        pasta = arquivo.parent.name
        if pasta == "docs" or pasta.startswith("."):
            continue

        numero, titulo = ler_cabecalho(arquivo)
        problema = por_numero.get(numero) or por_slug.get(arquivo.stem)
        if problema:
            problema["arquivo"] = problema["arquivo"] or arquivo
        elif numero:
            extras.append({"numero": numero, "titulo": titulo, "arquivo": arquivo})
        else:
            print(f"⚠️  ignorado (sem '# N. Título' na 1ª linha): {arquivo.relative_to(RAIZ)}")

    return extras


def contar(problemas):
    return sum(1 for p in problemas if p["arquivo"]), len(problemas)


def link_solucao(arquivo):
    # links relativos a docs/README.md
    return "../" + quote(arquivo.relative_to(RAIZ).as_posix())


def barra(feitos, total, tamanho=12):
    cheios = round(tamanho * feitos / total)
    if feitos and not cheios:
        cheios = 1
    return "█" * cheios + "░" * (tamanho - cheios)


def nome_problema(p):
    estrela = " ⭐" if p.get("blind75") else ""
    return f"[{p['titulo']}]({link_leetcode(p['titulo'])}){estrela}"


# ---------------------------------------------------------------- card SVG

def gerar_card(problemas, tema):
    t = TEMAS[tema]
    feitos, total = contar(problemas)
    cx, cy, raio = 132, 132, 74
    circunferencia = 2 * math.pi * raio
    bx, largura = 270, 574

    partes = [
        f'<circle cx="{cx}" cy="{cy}" r="{raio}" fill="none" stroke="{t["trilho"]}" stroke-width="14"/>',
    ]
    if feitos:
        partes.append(
            f'<circle cx="{cx}" cy="{cy}" r="{raio}" fill="none" stroke="url(#gradiente)" '
            f'stroke-width="14" stroke-linecap="round" stroke-dasharray="{circunferencia:.2f}" '
            f'stroke-dashoffset="{circunferencia * (1 - feitos / total):.2f}" '
            f'transform="rotate(-90 {cx} {cy})"/>'
        )
    partes += [
        f'<text x="{cx}" y="{cy + 10}" class="pct" text-anchor="middle">{feitos / total:.0%}</text>',
        f'<text x="{cx}" y="{cy + 32}" class="suave" text-anchor="middle">concluído</text>',
        f'<text x="{bx}" y="58" class="titulo">NeetCode 150</text>',
        f'<text x="{bx}" y="80" class="suave">progresso nos 150 problemas</text>',
        f'<text x="{bx + largura}" y="62" class="total" text-anchor="end">'
        f'<tspan class="forte">{feitos}</tspan> / {total}</text>',
    ]

    for i, (codigo, (rotulo, _)) in enumerate(DIFICULDADES.items()):
        f, tot = contar([p for p in problemas if p["dificuldade"] == codigo])
        y = 128 + i * 40
        partes += [
            f'<text x="{bx}" y="{y}" class="rotulo">{rotulo}</text>',
            f'<text x="{bx + largura}" y="{y}" class="suave" text-anchor="end">'
            f'<tspan class="forte">{f}</tspan> / {tot}</text>',
            f'<rect x="{bx}" y="{y + 9}" width="{largura}" height="8" rx="4" fill="{t["trilho"]}"/>',
        ]
        if f:
            preenchido = max(largura * f / tot, 8)
            partes.append(
                f'<rect x="{bx}" y="{y + 9}" width="{preenchido:.1f}" height="8" rx="4" '
                f'fill="url(#gradiente-barra)"/>'
            )

    corpo = "\n  ".join(partes)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="264" viewBox="0 0 880 264" role="img" aria-labelledby="titulo">
  <title id="titulo">NeetCode 150: {feitos} de {total} ({feitos / total:.0%})</title>
  <defs>
    <linearGradient id="gradiente" gradientUnits="userSpaceOnUse" x1="0" y1="{cy - raio}" x2="0" y2="{cy + raio}">
      <stop offset="0" stop-color="{t["rosa"]}"/>
      <stop offset="1" stop-color="{t["azul"]}"/>
    </linearGradient>
    <linearGradient id="gradiente-barra">
      <stop offset="0" stop-color="{t["rosa"]}"/>
      <stop offset="1" stop-color="{t["azul"]}"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {t["texto"]}; }}
    .titulo {{ font-size: 20px; font-weight: 600; }}
    .suave {{ font-size: 12px; fill: {t["suave"]}; }}
    .total {{ font-size: 15px; fill: {t["suave"]}; }}
    .rotulo {{ font-size: 13px; font-weight: 500; }}
    .forte {{ font-weight: 700; fill: {t["texto"]}; }}
    .pct {{ font-size: 36px; font-weight: 700; }}
  </style>
  <rect x="0.5" y="0.5" width="879" height="263" rx="16" fill="{t["fundo"]}" stroke="{t["borda"]}"/>
  {corpo}
</svg>
"""


# ---------------------------------------------------------------- README

def badge(rotulo, mensagem, extra=""):
    def esc(s):
        return quote(str(s).replace("-", "--").replace("_", "__").replace(" ", "_"), safe="_")
    return (
        f"![{rotulo}](https://img.shields.io/badge/{esc(rotulo)}-{esc(mensagem)}-{AZUL}"
        f"?style=for-the-badge&labelColor={ROSA}{extra})"
    )


def gerar_readme(problemas, extras):
    feitos, total = contar(problemas)

    linhas = [
        '<div align="center">',
        "",
        "# 🧩 LeetCode",
        "",
        "Repositório para armazenar meus leetcodes resolvidos, primariamente das listas<br>",
        f"**[Blind 75]({LINK_BLIND_75})** e **[NeetCode 150]({LINK_NEETCODE_150})**",
        "",
        " ".join([
            badge("Python", "3", "&logo=python&logoColor=white"),
            badge("NeetCode 150", f"{feitos}/{total} · {feitos / total:.0%}"),
            badge("resolvidos", feitos + len(extras)),
        ]),
        "",
        "</div>",
        "",
        "<br>",
        "",
        "## 📊 Estatísticas",
        "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/estatisticas-dark.svg">',
        '  <img alt="Progresso na NeetCode 150" src="assets/estatisticas-light.svg" width="100%">',
        "</picture>",
        "",
        "### Por categoria",
        "",
        "| Categoria | Progresso | Resolvidos |",
        "| :-- | :-- | :-: |",
    ]

    for categoria in NEETCODE_150:
        f, t = contar([p for p in problemas if p["categoria"] == categoria])
        nome = f"{categoria} ✨" if f == t else categoria
        linhas.append(f"| {nome} | `{barra(f, t)}` | {f} / {t} |")

    linhas += [
        "",
        "## ✅ Resolvidos",
        "",
        "⭐ = também está na Blind 75",
        "",
    ]

    resolvidos = sorted(
        [p for p in problemas if p["arquivo"]] + extras,
        key=lambda p: p["numero"],
    )
    if resolvidos:
        linhas += [
            "| # | Problema | Dificuldade | Categoria | Solução |",
            "| --: | :-- | :-- | :-- | :-: |",
        ]
        for p in resolvidos:
            if "categoria" in p:
                nome, emoji = DIFICULDADES[p["dificuldade"]]
                dificuldade, categoria = f"{emoji} {nome}", p["categoria"]
            else:
                dificuldade = categoria = "—"
            linhas.append(
                f"| {p['numero']} | {nome_problema(p)} | {dificuldade} "
                f"| {categoria} | [🐍]({link_solucao(p['arquivo'])}) |"
            )
    else:
        linhas.append("_Nenhum ainda — bora começar!_")

    linhas += [
        "",
        "## 🗺️ Roadmap",
        "",
        "Todos os problemas da NeetCode 150, por categoria. ⭐ = também está na Blind 75",
        "",
    ]

    for categoria in NEETCODE_150:
        grupo = [p for p in problemas if p["categoria"] == categoria]
        f, t = contar(grupo)
        linhas += [
            "<details>",
            f"<summary><b>{categoria.replace('&', '&amp;')}</b> · {f}/{t}</summary>",
            "",
            "| | # | Problema | Dificuldade |",
            "| :-: | --: | :-- | :-- |",
        ]
        for p in grupo:
            status = f"[✅]({link_solucao(p['arquivo'])})" if p["arquivo"] else "⬜"
            nome, emoji = DIFICULDADES[p["dificuldade"]]
            linhas.append(f"| {status} | {p['numero']} | {nome_problema(p)} | {emoji} {nome} |")
        linhas += ["", "</details>", ""]

    linhas += [
        "## 📝 Colinha",
        "",
        "Algumas funções e sintaxe que eu vivo esquecendo rs <3 → [`funcoes.py`](funcoes.py)",
        "",
        "## 📁 Estrutura",
        "",
        "```text",
        "leetcode/",
        "├── Blind-75/               # soluções da Blind 75",
        "├── NeetCode-150/           # soluções da NeetCode 150",
        "└── docs/",
        "    ├── README.md            # gerado automaticamente",
        "    ├── atualizar_readme.py  # gera o README e os cards",
        "    ├── funcoes.py           # colinha de sintaxe",
        "    └── assets/              # cards de estatísticas",
        "```",
        "",
        "## 🔄 Atualizando",
        "",
        "Toda solução começa com o número e o nome do problema na primeira linha:",
        "",
        "```python",
        "# 1. Two Sum",
        "```",
        "",
        "Depois de adicionar uma solução, é só rodar na raiz do repositório:",
        "",
        "```bash",
        "python3 docs/atualizar_readme.py",
        "```",
        "",
        "---",
        "",
        '<div align="center">',
        f"<sub>atualizado em {date.today():%d/%m/%Y} · feito com 🩷</sub>",
        "</div>",
        "",
    ]
    return "\n".join(linhas)


def main():
    problemas = carregar_problemas()
    extras = marcar_resolvidos(problemas)

    ASSETS.mkdir(exist_ok=True)
    for tema in TEMAS:
        (ASSETS / f"estatisticas-{tema}.svg").write_text(gerar_card(problemas, tema), encoding="utf-8")
    (DOCS / "README.md").write_text(gerar_readme(problemas, extras), encoding="utf-8")

    feitos, total = contar(problemas)
    print(f"README atualizado! NeetCode 150: {feitos}/{total} ({feitos / total:.0%}) · extras: {len(extras)}")


if __name__ == "__main__":
    main()
