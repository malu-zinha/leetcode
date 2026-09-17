"""Gera o README e os cards de estatísticas a partir das soluções do repositório.

Uso (na raiz do repositório):
    python3 scripts/atualizar_readme.py

Cada solução é uma pasta no formato que a extensão LeetHub cria: 0001-two-sum/.
As listas de problemas vêm de listas/*.json (veja scripts/importar_listas.py).
As datas de cada solução saem do histórico do git, então nada precisa ser anotado à mão.
"""

import json
import math
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
LISTAS = RAIZ / "listas"
SAIDA = RAIZ / ".github"
ASSETS = SAIDA / "assets"

FUSO = ZoneInfo("America/Sao_Paulo")
SEMANAS = 26  # meio ano de heatmap

# código: (nome, plural, emoji)
DIFICULDADES = {
    "E": ("Fácil", "fáceis", "🟢"),
    "M": ("Médio", "médios", "🟡"),
    "H": ("Difícil", "difíceis", "🔴"),
}

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

ROSA = "f58fc4"
AZUL = "8dd3f7"

TEMAS = {
    "claro": {
        "fundo": "#ffffff", "borda": "#f6d9e8", "texto": "#1f2328",
        "suave": "#6e6a78", "trilho": "#fcedf5",
        "rosa": f"#{ROSA}", "azul": f"#{AZUL}",
        "escala": ["#fcedf5", "#f9d2e7", "#f5aed4", "#f58fc4", "#d9629f"],
    },
    "escuro": {
        "fundo": "#0d1117", "borda": "#30363d", "texto": "#e6edf3",
        "suave": "#8d96a0", "trilho": "#232833",
        "rosa": "#ffa9d4", "azul": "#a3dcfb",
        "escala": ["#232833", "#5c3149", "#94456f", "#d2699f", "#ffa9d4"],
    },
}

CORES_DIFICULDADE = {"E": "#3fb950", "M": "#d29922", "H": "#f85149"}


# ------------------------------------------------------------------ dados

def git(*argumentos):
    return subprocess.run(
        ["git", *argumentos], cwd=RAIZ, capture_output=True, text=True, check=True
    ).stdout


def datas_por_arquivo():
    """Data em que cada arquivo entrou no repositório, seguindo renomeações."""
    try:
        saida = git("log", "--reverse", "--diff-filter=AR", "--name-status", "-M", "--format=@%aI")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  sem histórico do git: as datas e o heatmap vão ficar vazios")
        return {}

    datas, data = {}, None
    for linha in saida.splitlines():
        if linha.startswith("@"):
            data = datetime.fromisoformat(linha[1:]).astimezone(FUSO).date()
        elif linha.startswith("A\t"):
            datas.setdefault(linha.split("\t")[1], data)
        elif linha.startswith("R"):
            _, antigo, novo = linha.split("\t")
            datas[novo] = datas.pop(antigo, data)
    return datas


def carregar_listas():
    listas = [json.loads(arquivo.read_text(encoding="utf-8")) for arquivo in LISTAS.glob("*.json")]
    if not listas:
        raise SystemExit("Nenhuma lista em listas/ — rode antes: python3 scripts/importar_listas.py")
    return sorted(listas, key=lambda lista: lista["ordem"])


def montar_catalogo(listas):
    """Junta as listas em {numero: problema}; a lista mais antiga define a categoria."""
    catalogo = {}
    for lista in listas:
        for problema in lista["problemas"]:
            registro = catalogo.setdefault(problema["numero"], {**problema, "listas": []})
            registro["listas"].append(lista["nome"])
            if problema.get("video") and not registro.get("video"):
                registro["video"] = problema["video"]
    return catalogo


def encontrar_solucoes():
    """{numero: arquivo de código} a partir das pastas 0001-two-sum/ da raiz."""
    solucoes = {}
    for pasta in sorted(RAIZ.glob("[0-9][0-9][0-9][0-9]-*")):
        if not pasta.is_dir():
            continue
        arquivos = [
            arquivo for arquivo in sorted(pasta.iterdir())
            if arquivo.is_file() and arquivo.name not in ("README.md", "NOTES.md")
        ]
        if not arquivos:
            print(f"⚠️  pasta sem solução: {pasta.name}")
            continue
        solucoes[int(pasta.name.split("-")[0])] = arquivos[0]
    return solucoes


def resolver(catalogo, solucoes, datas):
    """Marca o que está resolvido e devolve também as soluções fora de todas as listas."""
    extras = []
    for numero, arquivo in solucoes.items():
        caminho = arquivo.relative_to(RAIZ).as_posix()
        registro = catalogo.get(numero)
        if registro is None:
            registro = catalogo[numero] = {
                "numero": numero,
                "titulo": titulo_da_pasta(arquivo.parent.name),
                "slug": arquivo.parent.name.split("-", 1)[1],
                "dificuldade": None,
                "categoria": None,
                "listas": [],
            }
            extras.append(registro)
        registro["arquivo"] = caminho
        registro["data"] = datas.get(caminho)
    return extras


def titulo_da_pasta(nome):
    return " ".join(palavra.capitalize() for palavra in nome.split("-", 1)[1].split("-"))


def resolvidos(problemas):
    return [problema for problema in problemas if problema.get("arquivo")]


def contar(problemas):
    return len(resolvidos(problemas)), len(problemas)


def problemas_da_lista(lista, catalogo):
    return [catalogo[problema["numero"]] for problema in lista["problemas"]]


def lista_em_foco(listas, catalogo):
    """A primeira lista da fila que ainda não terminou (ou a última, se acabou tudo)."""
    for lista in listas:
        feitos, total = contar(problemas_da_lista(lista, catalogo))
        if feitos < total:
            return lista
    return listas[-1]


def sequencias(dias, hoje):
    """(sequência atual, recorde) em dias consecutivos com pelo menos um problema novo."""
    dias = set(dias)
    atual, dia = 0, hoje if hoje in dias else hoje - timedelta(days=1)
    while dia in dias:
        atual += 1
        dia -= timedelta(days=1)

    recorde = corrente = 0
    anterior = None
    for dia in sorted(dias):
        corrente = corrente + 1 if anterior and (dia - anterior).days == 1 else 1
        recorde = max(recorde, corrente)
        anterior = dia
    return atual, recorde


# ------------------------------------------------------------------ formatação

def slug(titulo):
    s = re.sub(r"[^a-z0-9 -]", "", titulo.lower())
    return re.sub(r"[ -]+", "-", s).strip("-")


def link_leetcode(problema):
    return f"https://leetcode.com/problems/{problema.get('slug') or slug(problema['titulo'])}/"


def link_solucao(problema):
    # relativo a .github/README.md
    return "../" + problema["arquivo"]


def sigla(nome):
    letras = "".join(letra for letra in re.sub(r"\d", "", nome) if letra.isupper())
    numero = "".join(re.findall(r"\d+", nome))
    return f"{letras}{numero}"


def barra(feitos, total, tamanho=12):
    cheios = round(tamanho * feitos / total) if total else 0
    if feitos and not cheios:
        cheios = 1
    return "█" * cheios + "░" * (tamanho - cheios)


def nome_problema(problema):
    marca = " 🔒" if problema.get("premium") else ""
    return f"[{problema['titulo']}]({link_leetcode(problema)}){marca}"


def dificuldade_texto(problema):
    if not problema.get("dificuldade"):
        return "—"
    nome, _, emoji = DIFICULDADES[problema["dificuldade"]]
    return f"{emoji} {nome}"


def data_texto(problema):
    return f"{problema['data']:%d/%m/%y}" if problema.get("data") else "—"


# ------------------------------------------------------------------ card de progresso

def gerar_card(listas, catalogo, tema):
    t = TEMAS[tema]
    foco = lista_em_foco(listas, catalogo)
    feitos, total = contar(problemas_da_lista(foco, catalogo))
    todos = list(catalogo.values())

    cx, cy, raio = 132, 132, 74
    circunferencia = 2 * math.pi * raio
    bx, largura = 270, 574
    altura = max(264, 140 + len(listas) * 40 + 40)

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
        f'<text x="{cx}" y="{cy + 32}" class="suave" text-anchor="middle">da lista em foco</text>',
        f'<text x="{bx}" y="58" class="titulo">{foco["nome"]}</text>',
        f'<text x="{bx}" y="80" class="suave">lista em foco</text>',
        f'<text x="{bx + largura}" y="62" class="total" text-anchor="end">'
        f'<tspan class="forte">{feitos}</tspan> / {total}</text>',
    ]

    x = bx
    for codigo, (rotulo, plural, _) in DIFICULDADES.items():
        quantos = len([p for p in resolvidos(todos) if p.get("dificuldade") == codigo])
        partes += [
            f'<circle cx="{x + 5}" cy="104" r="5" fill="{CORES_DIFICULDADE[codigo]}"/>',
            f'<text x="{x + 17}" y="109" class="suave">{quantos} {plural}</text>',
        ]
        x += 24 + len(plural) * 7 + 14

    for i, lista in enumerate(listas):
        f, tot = contar(problemas_da_lista(lista, catalogo))
        y = 140 + i * 40
        rotulo = f'{lista["nome"]} ✨' if f == tot else lista["nome"]
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{altura}" viewBox="0 0 880 {altura}" role="img" aria-labelledby="titulo">
  <title id="titulo">{foco["nome"]}: {feitos} de {total} ({feitos / total:.0%})</title>
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
  <rect x="0.5" y="0.5" width="879" height="{altura - 1}" rx="16" fill="{t["fundo"]}" stroke="{t["borda"]}"/>
  {corpo}
</svg>
"""


# ------------------------------------------------------------------ heatmap

def gerar_heatmap(catalogo, hoje, tema):
    t = TEMAS[tema]
    por_dia = {}
    for problema in resolvidos(catalogo.values()):
        if problema.get("data"):
            por_dia[problema["data"]] = por_dia.get(problema["data"], 0) + 1

    fim = hoje + timedelta(days=6 - (hoje.weekday() + 1) % 7)
    inicio = fim - timedelta(days=SEMANAS * 7 - 1)
    lado, vao, x0, y0 = 15, 4, 48, 74

    partes, mes_anterior = [], None
    for semana in range(SEMANAS):
        x = x0 + semana * (lado + vao)
        for dia_semana in range(7):
            dia = inicio + timedelta(days=semana * 7 + dia_semana)
            if dia > hoje:
                continue
            quantos = por_dia.get(dia, 0)
            cor = t["escala"][min(quantos, 4)] if quantos else t["trilho"]
            y = y0 + dia_semana * (lado + vao)
            titulo = f"{dia:%d/%m/%Y}: {quantos} problema{'s' if quantos != 1 else ''}"
            partes.append(
                f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="4" fill="{cor}">'
                f"<title>{titulo}</title></rect>"
            )
        primeiro = inicio + timedelta(days=semana * 7)
        if primeiro.month != mes_anterior:
            partes.append(f'<text x="{x}" y="{y0 - 10}" class="suave">{MESES[primeiro.month - 1]}</text>')
            mes_anterior = primeiro.month

    for indice, rotulo in ((1, "seg"), (3, "qua"), (5, "sex")):
        y = y0 + indice * (lado + vao) + 12
        partes.append(f'<text x="8" y="{y}" class="suave">{rotulo}</text>')

    atual, recorde = sequencias(por_dia, hoje)
    ultimos = sum(quantos for dia, quantos in por_dia.items() if dia >= inicio)
    painel = x0 + SEMANAS * (lado + vao) + 24
    partes += [
        f'<text x="{painel}" y="96" class="numero">{atual}</text>',
        f'<text x="{painel}" y="116" class="suave">dias seguidos</text>',
        f'<text x="{painel}" y="152" class="rotulo">recorde: {recorde} dias</text>',
        f'<text x="{painel}" y="174" class="suave">{ultimos} nos últimos 6 meses</text>',
    ]

    legenda_x = x0 + SEMANAS * (lado + vao) - 5 * (lado + vao) - 40
    partes.append(f'<text x="{legenda_x - 8}" y="{y0 + 7 * (lado + vao) + 22}" class="suave" text-anchor="end">menos</text>')
    for nivel in range(5):
        x = legenda_x + nivel * (lado + vao)
        cor = t["escala"][nivel] if nivel else t["trilho"]
        partes.append(
            f'<rect x="{x}" y="{y0 + 7 * (lado + vao) + 10}" width="{lado}" height="{lado}" rx="4" fill="{cor}"/>'
        )
    partes.append(
        f'<text x="{legenda_x + 5 * (lado + vao) + 4}" y="{y0 + 7 * (lado + vao) + 22}" class="suave">mais</text>'
    )

    altura = y0 + 7 * (lado + vao) + 44
    corpo = "\n  ".join(partes)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{altura}" viewBox="0 0 880 {altura}" role="img" aria-labelledby="titulo">
  <title id="titulo">Atividade: {atual} dias seguidos, recorde de {recorde} dias</title>
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {t["texto"]}; }}
    .titulo {{ font-size: 20px; font-weight: 600; }}
    .suave {{ font-size: 11px; fill: {t["suave"]}; }}
    .rotulo {{ font-size: 13px; font-weight: 500; }}
    .numero {{ font-size: 34px; font-weight: 700; fill: {t["rosa"]}; }}
  </style>
  <rect x="0.5" y="0.5" width="879" height="{altura - 1}" rx="16" fill="{t["fundo"]}" stroke="{t["borda"]}"/>
  <text x="40" y="44" class="titulo">Atividade</text>
  {corpo}
</svg>
"""


# ------------------------------------------------------------------ README

def badge(rotulo, mensagem, extra=""):
    def esc(texto):
        return quote(str(texto).replace("-", "--").replace("_", "__").replace(" ", "_"), safe="_")
    return (
        f"![{rotulo}](https://img.shields.io/badge/{esc(rotulo)}-{esc(mensagem)}-{AZUL}"
        f"?style=for-the-badge&labelColor={ROSA}{extra})"
    )


def tabela_resolvidos(problemas):
    linhas = [
        "| # | Problema | Dificuldade | Categoria | Listas | Resolvido | Solução |",
        "| --: | :-- | :-- | :-- | :-- | :-- | :-: |",
    ]
    for problema in problemas:
        siglas = " · ".join(sigla(nome) for nome in problema["listas"]) or "—"
        linhas.append(
            f"| {problema['numero']} | {nome_problema(problema)} | {dificuldade_texto(problema)} "
            f"| {problema.get('categoria') or '—'} | {siglas} | {data_texto(problema)} "
            f"| [🐍]({link_solucao(problema)}) |"
        )
    return linhas


def gerar_readme(listas, catalogo, hoje):
    todos = list(catalogo.values())
    feitos = resolvidos(todos)
    foco = lista_em_foco(listas, catalogo)
    por_dia = {p["data"] for p in feitos if p.get("data")}
    atual, _ = sequencias(por_dia, hoje)
    contagem = {codigo: len([p for p in feitos if p.get("dificuldade") == codigo]) for codigo in DIFICULDADES}

    caminho_listas = " → ".join(f"**[{lista['nome']}]({lista['link']})**" for lista in listas)

    linhas = [
        '<div align="center">',
        "",
        "# 🧩 LeetCode",
        "",
        "Repositório dos meus leetcodes resolvidos, seguindo as listas<br>",
        caminho_listas,
        "",
        " ".join([
            badge("Python", "3", "&logo=python&logoColor=white"),
            badge("resolvidos", len(feitos)),
            badge("dificuldade", " · ".join(
                f"{emoji} {contagem[codigo]}" for codigo, (*_, emoji) in DIFICULDADES.items()
            )),
            badge("sequência", f"{atual} dias"),
        ]),
        "",
        "</div>",
        "",
        "<br>",
        "",
        "## 📊 Estatísticas",
        "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/estatisticas-escuro.svg">',
        '  <img alt="Progresso nas listas" src="assets/estatisticas-claro.svg" width="100%">',
        "</picture>",
        "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/atividade-escuro.svg">',
        '  <img alt="Atividade dos últimos 6 meses" src="assets/atividade-claro.svg" width="100%">',
        "</picture>",
        "",
        "### Por lista",
        "",
        "| Lista | Progresso | Resolvidos | |",
        "| :-- | :-- | :-: | :-- |",
    ]

    for lista in listas:
        f, total = contar(problemas_da_lista(lista, catalogo))
        marca = "🎯 em foco" if lista is foco else ("✨ completa" if f == total else "")
        linhas.append(f"| [{lista['nome']}]({lista['link']}) | `{barra(f, total)}` | {f} / {total} | {marca} |")

    linhas += [
        "",
        "### Por categoria",
        "",
        "| Categoria | Progresso | Resolvidos |",
        "| :-- | :-- | :-: |",
    ]

    categorias = dict.fromkeys(
        problema["categoria"] for lista in listas for problema in lista["problemas"]
    )
    for categoria in categorias:
        grupo = [p for p in todos if p.get("categoria") == categoria]
        f, total = contar(grupo)
        nome = f"{categoria} ✨" if f == total else categoria
        linhas.append(f"| {nome} | `{barra(f, total)}` | {f} / {total} |")

    linhas += ["", "## ✅ Resolvidos", ""]
    if feitos:
        recentes = sorted(feitos, key=lambda p: (p.get("data") or hoje, p["numero"]), reverse=True)
        if len(recentes) > 10:
            linhas += ["Os 10 últimos:", ""]
        linhas += tabela_resolvidos(recentes[:10])
        if len(recentes) > 10:
            linhas += [
                "",
                "<details>",
                f"<summary><b>Todos os {len(recentes)}</b>, por número</summary>",
                "",
                *tabela_resolvidos(sorted(feitos, key=lambda p: p["numero"])),
                "",
                "</details>",
            ]
    else:
        linhas.append("_Nenhum ainda — bora começar!_")

    linhas += [
        "",
        f"## 🗺️ Roadmap · {foco['nome']}",
        "",
        "A lista da vez. 🔒 = precisa de LeetCode Premium · 🎥 = vídeo do NeetCode",
        "",
    ]

    problemas_foco = problemas_da_lista(foco, catalogo)
    for categoria in dict.fromkeys(p["categoria"] for p in foco["problemas"]):
        grupo = [p for p in problemas_foco if p["categoria"] == categoria]
        f, total = contar(grupo)
        linhas += [
            "<details>",
            f"<summary><b>{categoria.replace('&', '&amp;')}</b> · {f}/{total}</summary>",
            "",
            "| | # | Problema | Dificuldade | |",
            "| :-: | --: | :-- | :-- | :-: |",
        ]
        for problema in grupo:
            status = f"[✅]({link_solucao(problema)})" if problema.get("arquivo") else "⬜"
            video = f"[🎥](https://youtu.be/{problema['video']})" if problema.get("video") else ""
            linhas.append(
                f"| {status} | {problema['numero']} | {nome_problema(problema)} "
                f"| {dificuldade_texto(problema)} | {video} |"
            )
        linhas += ["", "</details>", ""]

    ultima = max((p["data"] for p in feitos if p.get("data")), default=None)
    linhas += [
        "## 📝 Colinha",
        "",
        "Algumas funções e sintaxe que eu vivo esquecendo rs <3 → [`funcoes.py`](../docs/funcoes.py)",
        "",
        "## 🔄 Como funciona",
        "",
        "Resolvo no [leetcode.com](https://leetcode.com/) e não faço mais nada:",
        "",
        "1. a extensão [LeetHub-3.0](https://github.com/raphaelheinz/LeetHub-3.0) commita a solução aqui quando a submissão passa;",
        "2. a [Action](workflows/readme.yml) roda o [gerador](../scripts/atualizar_readme.py) e atualiza este README e os cards;",
        "3. as datas e a sequência de dias saem do próprio histórico do git.",
        "",
        "```text",
        "leetcode/",
        "├── 0001-two-sum/           # uma pasta por problema (criada pela extensão)",
        "├── listas/                 # as listas em JSON; lista nova = arquivo novo",
        "├── scripts/                # gerador do README e importador das listas",
        "├── docs/funcoes.py         # a colinha",
        "└── .github/README.md       # este arquivo, gerado",
        "```",
        "",
        "Para adicionar uma lista nova (por exemplo o LeetCode 75):",
        "",
        "```bash",
        "python3 scripts/importar_listas.py --plano leetcode-75 --ordem 4",
        "```",
        "",
        "---",
        "",
        '<div align="center">',
        f"<sub>última solução em {ultima:%d/%m/%Y} · feito com 🩷</sub>" if ultima else "<sub>feito com 🩷</sub>",
        "</div>",
        "",
    ]
    return "\n".join(linhas)


def main():
    hoje = datetime.now(FUSO).date()
    listas = carregar_listas()
    catalogo = montar_catalogo(listas)
    extras = resolver(catalogo, encontrar_solucoes(), datas_por_arquivo())

    ASSETS.mkdir(parents=True, exist_ok=True)
    for tema in TEMAS:
        (ASSETS / f"estatisticas-{tema}.svg").write_text(gerar_card(listas, catalogo, tema), encoding="utf-8")
        (ASSETS / f"atividade-{tema}.svg").write_text(gerar_heatmap(catalogo, hoje, tema), encoding="utf-8")
    (SAIDA / "README.md").write_text(gerar_readme(listas, catalogo, hoje), encoding="utf-8")

    total = len(resolvidos(catalogo.values()))
    print(f"README atualizado! {total} resolvidos · " + " · ".join(
        f"{lista['nome']}: {contar(problemas_da_lista(lista, catalogo))[0]}/{len(lista['problemas'])}"
        for lista in listas
    ) + (f" · fora das listas: {len(extras)}" if extras else ""))


if __name__ == "__main__":
    main()
