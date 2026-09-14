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

# código: (nome, emoji, cor)
DIFICULDADES = {
    "E": ("Fácil", "🟢", "#00b8a3"),
    "M": ("Médio", "🟡", "#ffb800"),
    "H": ("Difícil", "🔴", "#ff375f"),
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

# a Blind 75 inteira está dentro da NeetCode 150
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

TEMAS = {
    "light": {
        "fundo": "#ffffff", "borda": "#d0d7de", "texto": "#1f2328",
        "suave": "#656d76", "trilho": "#eaeef2",
        "Blind 75": "#bf3989", "NeetCode 150": "#8250df",
    },
    "dark": {
        "fundo": "#0d1117", "borda": "#30363d", "texto": "#e6edf3",
        "suave": "#8d96a0", "trilho": "#21262d",
        "Blind 75": "#f778ba", "NeetCode 150": "#a371f7",
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
    """Marca os problemas das listas e devolve as soluções que estão fora delas."""
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


# ---------------------------------------------------------------- card SVG

RAIO = 50
CIRCUNFERENCIA = 2 * math.pi * RAIO


def painel_svg(x, nome, descricao, problemas, t):
    cor = t[nome]
    feitos, total = contar(problemas)
    cx, cy = x + 95, 148

    partes = [
        f'<text x="{x + 28}" y="46" class="titulo">{nome}</text>',
        f'<text x="{x + 28}" y="66" class="suave">{descricao}</text>',
        f'<text x="{x + 412}" y="48" class="pct" text-anchor="end" style="fill:{cor}">{feitos / total:.0%}</text>',
        f'<circle cx="{cx}" cy="{cy}" r="{RAIO}" fill="none" stroke="{t["trilho"]}" stroke-width="10"/>',
    ]
    if feitos:
        partes.append(
            f'<circle class="anel" cx="{cx}" cy="{cy}" r="{RAIO}" fill="none" stroke="{cor}" '
            f'stroke-width="10" stroke-linecap="round" stroke-dasharray="{CIRCUNFERENCIA:.2f}" '
            f'stroke-dashoffset="{CIRCUNFERENCIA * (1 - feitos / total):.2f}" '
            f'transform="rotate(-90 {cx} {cy})"/>'
        )
    partes += [
        f'<text x="{cx}" y="{cy + 3}" class="numero" text-anchor="middle">{feitos}</text>',
        f'<text x="{cx}" y="{cy + 21}" class="suave" text-anchor="middle">de {total}</text>',
    ]

    bx, largura = x + 190, 222
    for i, (codigo, (rotulo, _, cor_dif)) in enumerate(DIFICULDADES.items()):
        f, tot = contar([p for p in problemas if p["dificuldade"] == codigo])
        y = 114 + i * 40
        partes += [
            f'<text x="{bx}" y="{y}" class="rotulo">{rotulo}</text>',
            f'<text x="{bx + largura}" y="{y}" class="suave" text-anchor="end">'
            f'<tspan class="forte">{f}</tspan> / {tot}</text>',
            f'<rect x="{bx}" y="{y + 8}" width="{largura}" height="6" rx="3" fill="{t["trilho"]}"/>',
        ]
        if f:
            preenchido = max(largura * f / tot, 6)
            partes.append(
                f'<rect class="barra" x="{bx}" y="{y + 8}" width="{preenchido:.1f}" '
                f'height="6" rx="3" fill="{cor_dif}"/>'
            )

    return "\n  ".join(partes)


def gerar_card(problemas, tema):
    t = TEMAS[tema]
    b75 = [p for p in problemas if p["blind75"]]
    feitos_b75, _ = contar(b75)
    feitos_nc, _ = contar(problemas)

    estilo = f"""
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {t["texto"]}; }}
    .titulo {{ font-size: 19px; font-weight: 600; }}
    .suave {{ font-size: 12px; fill: {t["suave"]}; }}
    .rotulo {{ font-size: 13px; font-weight: 500; }}
    .forte {{ font-weight: 600; fill: {t["texto"]}; }}
    .pct {{ font-size: 22px; font-weight: 700; }}
    .numero {{ font-size: 30px; font-weight: 700; }}
  """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="236" viewBox="0 0 880 236" role="img" aria-labelledby="titulo">
  <title id="titulo">Blind 75: {feitos_b75} de 75 · NeetCode 150: {feitos_nc} de 150</title>
  <style>{estilo}</style>
  <rect x="0.5" y="0.5" width="879" height="235" rx="14" fill="{t["fundo"]}" stroke="{t["borda"]}"/>
  <line x1="440" y1="28" x2="440" y2="208" stroke="{t["borda"]}"/>
  {painel_svg(0, "Blind 75", "a lista clássica de entrevistas", b75, t)}
  {painel_svg(440, "NeetCode 150", "Blind 75 + 75 problemas extras", problemas, t)}
</svg>
"""


# ---------------------------------------------------------------- README

def badge(rotulo, mensagem, cor, extra=""):
    def esc(s):
        return quote(str(s).replace("-", "--").replace("_", "__").replace(" ", "_"), safe="_")
    return f"![{rotulo}](https://img.shields.io/badge/{esc(rotulo)}-{esc(mensagem)}-{cor}?style=for-the-badge{extra})"


def gerar_readme(problemas, extras):
    b75 = [p for p in problemas if p["blind75"]]
    feitos_b75, _ = contar(b75)
    feitos_nc, _ = contar(problemas)
    total_resolvidos = feitos_nc + len(extras)

    linhas = [
        '<div align="center">',
        "",
        "# 🧩 LeetCode",
        "",
        "Repositório para armazenar meus leetcodes resolvidos, primariamente das listas<br>",
        f"**[Blind 75]({LINK_BLIND_75})** e **[NeetCode 150]({LINK_NEETCODE_150})**",
        "",
        " ".join([
            badge("Python", "3", "3776AB", "&logo=python&logoColor=white"),
            badge("resolvidos", total_resolvidos, "f778ba"),
            badge("Blind 75", f"{feitos_b75}/75", "bf3989"),
            badge("NeetCode 150", f"{feitos_nc}/150", "8250df"),
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
        '  <img alt="Progresso nas listas Blind 75 e NeetCode 150" src="assets/estatisticas-light.svg" width="100%">',
        "</picture>",
        "",
        "> [!NOTE]",
        "> A NeetCode 150 contém a Blind 75 inteira, então todo problema da Blind conta para as duas listas.",
        "",
        "### Por categoria",
        "",
        "| Categoria | Progresso | NeetCode 150 | Blind 75 |",
        "| :-- | :-- | :-: | :-: |",
    ]

    for categoria in NEETCODE_150:
        grupo = [p for p in problemas if p["categoria"] == categoria]
        f_nc, t_nc = contar(grupo)
        f_b, t_b = contar([p for p in grupo if p["blind75"]])
        nome = f"{categoria} ✨" if f_nc == t_nc else categoria
        linhas.append(f"| {nome} | `{barra(f_nc, t_nc)}` | {f_nc} / {t_nc} | {f_b} / {t_b} |")

    linhas += ["", "## ✅ Resolvidos", ""]

    resolvidos = sorted(
        [p for p in problemas if p["arquivo"]] + extras,
        key=lambda p: p["numero"],
    )
    if resolvidos:
        linhas += [
            "| # | Problema | Dificuldade | Categoria | Listas | Solução |",
            "| --: | :-- | :-- | :-- | :-- | :-: |",
        ]
        for p in resolvidos:
            if "categoria" in p:
                nome, emoji, _ = DIFICULDADES[p["dificuldade"]]
                dificuldade, categoria = f"{emoji} {nome}", p["categoria"]
                listas = "Blind 75 · NeetCode 150" if p["blind75"] else "NeetCode 150"
            else:
                dificuldade = categoria = listas = "—"
            linhas.append(
                f"| {p['numero']} | [{p['titulo']}]({link_leetcode(p['titulo'])}) | {dificuldade} "
                f"| {categoria} | {listas} | [🐍]({link_solucao(p['arquivo'])}) |"
            )
    else:
        linhas.append("_Nenhum ainda — bora começar!_")

    linhas += [
        "",
        "## 🗺️ Roadmap",
        "",
        "Todos os problemas da NeetCode 150, por categoria. ⭐ = também está na Blind 75.",
        "",
    ]

    for categoria, itens in NEETCODE_150.items():
        grupo = [p for p in problemas if p["categoria"] == categoria]
        feitos, total = contar(grupo)
        linhas += [
            "<details>",
            f"<summary><b>{categoria.replace('&', '&amp;')}</b> · {feitos}/{total}</summary>",
            "",
            "| | # | Problema | Dificuldade | |",
            "| :-: | --: | :-- | :-- | :-: |",
        ]
        for p in grupo:
            status = f"[✅]({link_solucao(p['arquivo'])})" if p["arquivo"] else "⬜"
            nome, emoji, _ = DIFICULDADES[p["dificuldade"]]
            estrela = "⭐" if p["blind75"] else ""
            linhas.append(
                f"| {status} | {p['numero']} | [{p['titulo']}]({link_leetcode(p['titulo'])}) "
                f"| {emoji} {nome} | {estrela} |"
            )
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
        f"<sub>atualizado em {date.today():%d/%m/%Y} · feito com 💜</sub>",
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

    feitos_b75, _ = contar([p for p in problemas if p["blind75"]])
    feitos_nc, _ = contar(problemas)
    print(f"README atualizado! Blind 75: {feitos_b75}/75 · NeetCode 150: {feitos_nc}/150 · extras: {len(extras)}")


if __name__ == "__main__":
    main()
