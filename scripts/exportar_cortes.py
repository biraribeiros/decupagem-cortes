#!/usr/bin/env python3
"""Valida cortes.json contra frases.json e gera os arquivos de edição.

Uso: python exportar_cortes.py cortes.json frases.json --saida entrega/ [--fps 29.97] [--pre 0.15] [--pos 0.30]

Gera: decupagem.md, decupagem.csv, marcadores.csv, cortes/<ID>.edl, legendas/<ID>.srt,
textos/<ID>.txt e validacao.txt. Sai com código 1 se houver erro bloqueante.
"""
import argparse, csv, json, os, re, sys

PESOS = {"completude": 25, "gancho": 15, "relevancia": 15, "desenvolvimento": 15,
         "autonomia": 10, "clareza": 10, "emocao": 10}


def fmt(t):
    m, s = divmod(max(t, 0), 60)
    h, m = divmod(int(m), 60)
    return f"{h}:{m:02d}:{s:05.2f}" if h else f"{m:02d}:{s:05.2f}"


def dur(t):
    m, s = divmod(round(t), 60)
    return f"{m}:{s:02d}"


def tc(seg, fps):
    """Timecode non-drop: conta quadros reais e rotula em base inteira."""
    return tc_q(int(round(seg * fps)), fps)


def tc_q(n, fps):
    base = round(fps)
    f = n % base; s = n // base
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f:02d}"


def srt_tc(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cortes"); ap.add_argument("frases")
    ap.add_argument("--saida", default="entrega")
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--pre", type=float, default=0.15)
    ap.add_argument("--pos", type=float, default=0.30)
    ap.add_argument("--chars", type=int, default=42, help="máx. caracteres por bloco de legenda")
    a = ap.parse_args()

    C = json.load(open(a.cortes, encoding="utf-8"))
    F = json.load(open(a.frases, encoding="utf-8"))
    frases = F["frases"] if isinstance(F, dict) else F
    idx = {f["id"]: i for i, f in enumerate(frases)}
    fps = a.fps or C.get("fps", 29.97)
    pesos = C.get("pesos", PESOS)
    dmin, dmax = C.get("duracao_min", 0), C.get("duracao_max", 10 ** 6)
    fonte = C.get("fonte", F.get("fonte", "FONTE") if isinstance(F, dict) else "FONTE")

    erros, avisos, saida = [], [], []

    for c in C.get("cortes", []):
        cid = c.get("id", "?")
        partes = []
        for k, t in enumerate(c.get("trechos", [])):
            de, ate = t.get("de"), t.get("ate", t.get("de"))
            if de not in idx or ate not in idx:
                erros.append(f"{cid}: frase inexistente em trecho {k+1} ({de}–{ate})"); continue
            i0, i1 = idx[de], idx[ate]
            if i1 < i0:
                erros.append(f"{cid}: trecho {k+1} com 'ate' antes de 'de' ({de}–{ate})"); continue
            ini = frases[i0]["inicio"] - a.pre
            if i0 > 0: ini = max(ini, frases[i0 - 1]["fim"])
            fim = frases[i1]["fim"] + a.pos
            if i1 + 1 < len(frases): fim = min(fim, frases[i1 + 1]["inicio"])
            if "inicio" in t: ini = float(t["inicio"])
            if "fim" in t: fim = float(t["fim"])
            ini = max(ini, 0)
            palavras = [p for f in frases[i0:i1 + 1] for p in f.get("palavras", [])
                        if p["e"] > ini and p["s"] < fim]
            texto = " ".join(p["w"] for p in palavras) or " ".join(f["texto"] for f in frases[i0:i1 + 1])
            fal = sorted({f["falante"] for f in frases[i0:i1 + 1] if f.get("falante")})
            partes.append({"de": de, "ate": ate, "i0": i0, "ini": ini, "fim": fim, "texto": texto,
                           "palavras": palavras, "falantes": fal})
        if not partes:
            erros.append(f"{cid}: nenhum trecho válido"); continue

        fora_ordem = any(partes[k]["ini"] < partes[k - 1]["ini"] for k in range(1, len(partes)))
        if fora_ordem and not c.get("nao_linear"):
            erros.append(f"{cid}: trechos fora da ordem do vídeo sem 'nao_linear: true'")
        for k in range(1, len(partes)):
            if partes[k]["ini"] < partes[k - 1]["fim"] and not fora_ordem:
                avisos.append(f"{cid}: trechos {k} e {k+1} se sobrepõem")
        falantes = sorted({x for p in partes for x in p["falantes"]})
        if len(partes) > 1 and len(falantes) > 1:
            avisos.append(f"{cid}: costura com falantes diferentes ({', '.join(falantes)}); confira fidelidade")

        total = sum(p["fim"] - p["ini"] for p in partes)
        if c.get("status", "aprovado") == "aprovado" and not (dmin <= total <= dmax):
            avisos.append(f"{cid}: duração {dur(total)} fora da faixa {dur(dmin)}–{dur(dmax)}")

        notas = c.get("notas") or {}
        score = None
        if notas:
            falt = [k for k in pesos if k not in notas]
            if falt: avisos.append(f"{cid}: notas faltando ({', '.join(falt)})")
            score = round(sum(pesos[k] * float(notas.get(k, 0)) / 10 for k in pesos))
        saida.append({**c, "_partes": partes, "_total": total, "_score": score})

    # sobreposição entre cortes aprovados (mesma ideia em dois cortes?)
    aprov = [s for s in saida if s.get("status", "aprovado") == "aprovado"]
    for i in range(len(aprov)):
        for j in range(i + 1, len(aprov)):
            for p in aprov[i]["_partes"]:
                for q in aprov[j]["_partes"]:
                    ov = min(p["fim"], q["fim"]) - max(p["ini"], q["ini"])
                    if ov > 3:
                        avisos.append(f"{aprov[i]['id']} e {aprov[j]['id']} compartilham {ov:.0f}s de material; confira se não repetem a ideia")

    os.makedirs(a.saida, exist_ok=True)
    for sub in ("cortes", "legendas", "textos"):
        os.makedirs(os.path.join(a.saida, sub), exist_ok=True)

    ordem = sorted(saida, key=lambda s: (s.get("status", "aprovado") != "aprovado", -(s["_score"] or 0)))

    # CSV
    with open(os.path.join(a.saida, "decupagem.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["corte", "status", "titulo", "titulo_publicacao", "trechos", "entrada", "saida", "duracao",
                    "score", "nao_linear", "ideia", "gancho", "lettering", "ajustes"])
        for s in ordem:
            p = s["_partes"]; let = s.get("lettering") or {}
            w.writerow([s["id"], s.get("status", "aprovado"), s.get("titulo", ""), s.get("titulo_publicacao", ""),
                        " + ".join(f"{x['de']}–{x['ate']}" for x in p), fmt(p[0]["ini"]), fmt(p[-1]["fim"]),
                        dur(s["_total"]), s["_score"] if s["_score"] is not None else "",
                        "sim" if s.get("nao_linear") else "não", s.get("ideia", ""), s.get("gancho", ""),
                        let.get("texto", "") if isinstance(let, dict) else let, s.get("ajustes", "")])

    # marcadores (um por trecho, sobre o vídeo bruto)
    with open(os.path.join(a.saida, "marcadores.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["nome", "entrada_tc", "saida_tc", "entrada", "saida", "comentario"])
        for s in ordem:
            for k, p in enumerate(s["_partes"], 1):
                w.writerow([f"{s['id']}.{k} {s.get('titulo','')}", tc(p["ini"], fps), tc(p["fim"], fps),
                            fmt(p["ini"]), fmt(p["fim"]), s.get("ideia", "")])

    # EDL, SRT e TXT por corte
    for s in ordem:
        cid = s["id"]; rec = 3600 * round(fps)  # timeline começa em 01:00:00:00
        with open(os.path.join(a.saida, "cortes", f"{cid}.edl"), "w", encoding="utf-8") as f:
            f.write(f"TITLE: {cid} {s.get('titulo','')}\nFCM: NON-DROP FRAME\n\n")
            for k, p in enumerate(s["_partes"], 1):
                q0, q1 = int(round(p["ini"] * fps)), int(round(p["fim"] * fps))
                f.write(f"{k:03d}  AX       AA/V  C        {tc_q(q0, fps)} {tc_q(q1, fps)} "
                        f"{tc_q(rec, fps)} {tc_q(rec + q1 - q0, fps)}\n* FROM CLIP NAME: {fonte}\n\n")
                rec += q1 - q0
        # legenda re-temporizada para a timeline do corte
        blocos, desloc = [], 0.0
        for p in s["_partes"]:
            ws = p["palavras"] or [{"w": t, "s": p["ini"], "e": p["fim"]} for t in [p["texto"]]]
            atual = []
            for n_w, wd in enumerate(ws):
                junto = len(" ".join(x["w"] for x in atual + [wd]))
                # evita sobra curta: se faltam até 2 palavras para fechar a frase, estica o bloco
                resto = []
                for x in ws[n_w:n_w + 2]:
                    resto.append(x)
                    if re.search(r"[.!?]$", x["w"]): break
                fecha_logo = re.search(r"[.!?]$", resto[-1]["w"]) and \
                    len(" ".join(x["w"] for x in atual + resto)) <= a.chars + 12
                if atual and junto > a.chars and not fecha_logo:
                    blocos.append((atual[0]["s"] - p["ini"] + desloc, atual[-1]["e"] - p["ini"] + desloc, atual)); atual = []
                atual.append(wd)
                if re.search(r"[.!?]$", wd["w"]):
                    blocos.append((atual[0]["s"] - p["ini"] + desloc, atual[-1]["e"] - p["ini"] + desloc, atual)); atual = []
            if atual:
                blocos.append((atual[0]["s"] - p["ini"] + desloc, atual[-1]["e"] - p["ini"] + desloc, atual))
            desloc += p["fim"] - p["ini"]
        with open(os.path.join(a.saida, "legendas", f"{cid}.srt"), "w", encoding="utf-8") as f:
            for n, (i0, i1, ws) in enumerate(blocos, 1):
                f.write(f"{n}\n{srt_tc(max(i0,0))} --> {srt_tc(max(i1, i0 + 0.3))}\n{' '.join(x['w'] for x in ws)}\n\n")
        with open(os.path.join(a.saida, "textos", f"{cid}.txt"), "w", encoding="utf-8") as f:
            f.write(f"{cid} {s.get('titulo','')}\n\n" + "\n\n[corte]\n\n".join(p["texto"] for p in s["_partes"]) + "\n")

    # decupagem.md
    with open(os.path.join(a.saida, "decupagem.md"), "w", encoding="utf-8") as f:
        f.write(f"# Decupagem: {C.get('projeto', fonte)}\n\n")
        if C.get("premissas"): f.write(f"**Premissas:** {C['premissas']}\n\n")
        f.write(f"Fonte: `{fonte}` · {fps} fps · margens {a.pre}s / {a.pos}s\n\n")
        f.write("| # | Título | Entrada | Saída | Duração | Score | Status |\n|---|---|---|---|---|---:|---|\n")
        for s in ordem:
            p = s["_partes"]
            f.write(f"| {s['id']} | {s.get('titulo','')} | {fmt(p[0]['ini'])} | {fmt(p[-1]['fim'])} | "
                    f"{dur(s['_total'])} | {s['_score'] if s['_score'] is not None else '–'} | {s.get('status','aprovado')} |\n")
        for s in ordem:
            p = s["_partes"]; let = s.get("lettering") or {}
            f.write(f"\n---\n\n## {s['id']} · {s.get('titulo','')}\n\n")
            f.write(f"**Score {s['_score'] if s['_score'] is not None else '–'}** · {dur(s['_total'])} · "
                    f"{'não linear' if s.get('nao_linear') else 'linear'} · {s.get('tipo','')}\n\n")
            f.write("| Trecho | Frases | Entrada | Saída | TC entrada | TC saída |\n|---|---|---|---|---|---|\n")
            for k, x in enumerate(p, 1):
                f.write(f"| {k} | {x['de']}–{x['ate']} | {fmt(x['ini'])} | {fmt(x['fim'])} | {tc(x['ini'],fps)} | {tc(x['fim'],fps)} |\n")
            for rot, ch in (("Título de publicação", "titulo_publicacao"), ("Ideia", "ideia"), ("Gancho", "gancho"),
                            ("Desenvolvimento", "desenvolvimento"), ("Fechamento", "fechamento"),
                            ("Termos verificados", "termos_verificados"), ("Ajustes", "ajustes"),
                            ("Alternativas", "alternativas")):
                if s.get(ch): f.write(f"\n**{rot}:** {s[ch]}  ")
            if let:
                if isinstance(let, dict):
                    f.write(f"\n**Lettering ({let.get('formato','')}):** {let.get('texto','')}"
                            f"{' · entra em ' + let['entra_em'] if let.get('entra_em') else ''}  ")
                else:
                    f.write(f"\n**Lettering:** {let}  ")
            if s.get("notas"):
                f.write("\n**Notas:** " + " · ".join(f"{k} {v}" for k, v in s["notas"].items()) + "  ")
            f.write("\n\n**Fala:**\n\n" + "\n\n> ✂\n\n".join(f"> {x['texto']}" for x in p) + "\n")
        if C.get("descartados"):
            f.write("\n---\n\n## Descartados\n\n| Ideia | Trechos | Motivo |\n|---|---|---|\n")
            for d in C["descartados"]:
                f.write(f"| {d.get('ideia','')} | {d.get('trechos','')} | {d.get('motivo','')} |\n")

    with open(os.path.join(a.saida, "validacao.txt"), "w", encoding="utf-8") as f:
        f.write("ERROS\n" + ("\n".join(erros) or "nenhum") + "\n\nAVISOS\n" + ("\n".join(avisos) or "nenhum") + "\n")

    print(f"{len(saida)} cortes exportados para {a.saida}/")
    for e in erros: print("ERRO:", e)
    for v in avisos: print("AVISO:", v)
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
