#!/usr/bin/env python3
"""Converte uma transcrição (SRT, VTT, JSON do Whisper ou TXT com tempos) em frases numeradas.

Saídas (na pasta --saida):
  frases.json  lista de frases {id, inicio, fim, falante, texto, palavras}
  frases.md    uma linha por frase: F012 [05:12.30–05:18.04] (A) texto

Legendas costumam quebrar no meio da frase. O script reconstrói frases completas:
estima o tempo de cada palavra (real, se o JSON tiver palavras; interpolado no caso
contrário) e fecha a frase em pontuação final, pausa longa ou troca de falante.

Uso: python preparar_transcricao.py entrada.srt --saida trabalho/ [--pausa 1.2] [--max 30]
"""
import argparse, json, os, re, sys

TC = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:[.,](\d{1,3}))?")


def tsec(s):
    m = TC.search(s)
    if not m:
        raise ValueError(f"tempo inválido: {s}")
    h, mi, se, ms = m.groups()
    ms = (ms or "0").ljust(3, "0")[:3]
    return int(h or 0) * 3600 + int(mi) * 60 + int(se) + int(ms) / 1000


def fmt(t):
    m, s = divmod(t, 60)
    h, m = divmod(int(m), 60)
    return f"{h}:{m:02d}:{s:05.2f}" if h else f"{m:02d}:{s:05.2f}"


def limpa(txt):
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = re.sub(r"\{[^}]+\}", "", txt)
    return re.sub(r"\s+", " ", txt).strip()


def separa_falante(txt):
    """'<v Maria>texto' ou 'MARIA: texto' ou '[Maria] texto' -> (falante, texto)."""
    m = re.match(r"^<v\s+([^>]+)>(.*)$", txt.strip(), re.S)
    if m:
        return m.group(1).strip(), m.group(2)
    m = re.match(r"^\[([^\]]{1,30})\]\s*(.*)$", txt.strip(), re.S)
    if m:
        return m.group(1).strip(), m.group(2)
    m = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç .]{0,25}):\s+(.*)$", txt.strip(), re.S)
    if m and len(m.group(1).split()) <= 3:
        return m.group(1).strip(), m.group(2)
    return None, txt


def cues_legenda(conteudo):
    """SRT e VTT: lista de (inicio, fim, falante, texto)."""
    cues = []
    blocos = re.split(r"\n\s*\n", conteudo.replace("\r", ""))
    for b in blocos:
        linhas = [l for l in b.split("\n") if l.strip()]
        idx = next((i for i, l in enumerate(linhas) if "-->" in l), None)
        if idx is None:
            continue
        ini, fim = linhas[idx].split("-->")
        fim = fim.strip().split(" ")[0]
        bruto = " ".join(linhas[idx + 1:])
        fal, txt = separa_falante(bruto)
        txt = limpa(txt)
        if txt:
            cues.append((tsec(ini), tsec(fim), fal, txt))
    return cues


def cues_txt(conteudo):
    """Linhas com tempo no início: '[00:05:12] texto' ou '05:12 - texto'."""
    cues = []
    for l in conteudo.splitlines():
        m = re.match(r"^\s*\[?((?:\d+:)?\d{1,2}:\d{2}(?:[.,]\d+)?)\]?\s*[-–:]?\s*(.+)$", l)
        if m:
            fal, txt = separa_falante(m.group(2))
            cues.append([tsec(m.group(1)), None, fal, limpa(txt)])
    for i, c in enumerate(cues):
        c[1] = cues[i + 1][0] if i + 1 < len(cues) else c[0] + max(2, len(c[3]) / 15)
    return [tuple(c) for c in cues if c[3]]


def palavras_de_cues(cues):
    """Interpola tempo por palavra proporcional ao número de caracteres."""
    pal = []
    for ini, fim, fal, txt in cues:
        ws = txt.split()
        total = sum(len(w) + 1 for w in ws) or 1
        t, dur = ini, max(fim - ini, 0.01)
        for w in ws:
            d = dur * (len(w) + 1) / total
            pal.append({"w": w, "s": round(t, 3), "e": round(t + d, 3), "f": fal, "real": False})
            t += d
    return pal


def palavras_de_json(dados):
    segs = dados.get("segments", dados if isinstance(dados, list) else [])
    pal, cues = [], []
    for s in segs:
        fal = s.get("speaker")
        ws = s.get("words") or []
        if ws:
            for w in ws:
                txt = (w.get("word") or w.get("text") or "").strip()
                if txt:
                    pal.append({"w": txt, "s": round(float(w["start"]), 3), "e": round(float(w["end"]), 3),
                                "f": fal, "real": True})
        else:
            cues.append((float(s["start"]), float(s["end"]), fal, limpa(s.get("text", ""))))
    if cues:
        pal += palavras_de_cues(cues)
        pal.sort(key=lambda p: p["s"])
    return pal


FIM = re.compile(r"[.!?…]+[\"'”»)]*$")


def monta_frases(pal, pausa, maximo):
    frases, atual = [], []

    def fecha():
        if atual:
            frases.append(atual[:])
            atual.clear()

    for i, p in enumerate(pal):
        if atual:
            gap = p["s"] - atual[-1]["e"]
            troca = p["f"] and atual[-1]["f"] and p["f"] != atual[-1]["f"]
            longa = p["e"] - atual[0]["s"] > maximo and re.search(r"[,;:]$", atual[-1]["w"])
            muito_longa = p["e"] - atual[0]["s"] > maximo * 1.5
            if gap >= pausa or troca or longa or muito_longa:
                fecha()
        atual.append(p)
        if FIM.search(p["w"]):
            fecha()
    fecha()

    saida = []
    for n, fr in enumerate(frases, 1):
        falantes = [p["f"] for p in fr if p["f"]]
        saida.append({
            "id": f"F{n:03d}",
            "inicio": fr[0]["s"],
            "fim": fr[-1]["e"],
            "falante": max(set(falantes), key=falantes.count) if falantes else None,
            "texto": " ".join(p["w"] for p in fr),
            "tempo_por_palavra": "real" if all(p["real"] for p in fr) else "estimado",
            "palavras": [{"w": p["w"], "s": p["s"], "e": p["e"]} for p in fr],
        })
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--saida", default="trabalho")
    ap.add_argument("--pausa", type=float, default=1.2, help="pausa (s) que encerra uma frase")
    ap.add_argument("--max", type=float, default=30, help="duração (s) a partir da qual a frase é quebrada na vírgula")
    a = ap.parse_args()

    ext = os.path.splitext(a.entrada)[1].lower()
    conteudo = open(a.entrada, encoding="utf-8-sig", errors="replace").read()
    if ext == ".json":
        pal = palavras_de_json(json.loads(conteudo))
    elif ext in (".srt", ".vtt"):
        pal = palavras_de_cues(cues_legenda(conteudo))
    else:
        cues = cues_legenda(conteudo) if "-->" in conteudo else cues_txt(conteudo)
        pal = palavras_de_cues(cues)
    if not pal:
        sys.exit("Nenhum texto com tempo encontrado. Formatos aceitos: SRT, VTT, JSON do Whisper, TXT com [mm:ss].")

    frases = monta_frases(pal, a.pausa, a.max)
    os.makedirs(a.saida, exist_ok=True)
    json.dump({"fonte": os.path.basename(a.entrada), "frases": frases},
              open(os.path.join(a.saida, "frases.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(os.path.join(a.saida, "frases.md"), "w", encoding="utf-8") as f:
        f.write(f"# Frases numeradas: {os.path.basename(a.entrada)}\n\n")
        f.write(f"{len(frases)} frases · duração {fmt(frases[-1]['fim'])} · "
                f"tempo por palavra: {'real' if all(x['tempo_por_palavra']=='real' for x in frases) else 'estimado (interpolado da legenda)'}\n\n")
        anterior = None
        for x in frases:
            if anterior is not None and x["inicio"] - anterior > 3:
                f.write(f"\n— pausa de {x['inicio'] - anterior:.1f}s —\n\n")
            fal = f" ({x['falante']})" if x["falante"] else ""
            f.write(f"{x['id']} [{fmt(x['inicio'])}–{fmt(x['fim'])}]{fal} {x['texto']}\n")
            anterior = x["fim"]
    print(f"{len(frases)} frases -> {a.saida}/frases.md e frases.json")


if __name__ == "__main__":
    main()
