# Transcrição com timestamps

A decupagem precisa de timestamps confiáveis. Ordem de preferência:

1. **SRT/VTT que o usuário já tem** (Premiere "Transcrição baseada em texto" > exportar legendas, Descript, CapCut, YouTube Studio). Melhor caminho: rápido e já revisado.
2. **JSON do Whisper com palavras** (`word_timestamps`), que permite cortar dentro de frases longas.
3. **Transcrever aqui** com faster-whisper:

```bash
pip install faster-whisper --break-system-packages
python - <<'EOF'
from faster_whisper import WhisperModel
import json, sys
m = WhisperModel("small", device="cpu", compute_type="int8")   # "medium" = mais preciso, mais lento
segs, info = m.transcribe("ENTRADA.mp4", language="pt", word_timestamps=True, vad_filter=True)
out = {"segments": []}
for s in segs:
    out["segments"].append({"start": s.start, "end": s.end, "text": s.text,
        "words": [{"start": w.start, "end": w.end, "word": w.word} for w in (s.words or [])]})
json.dump(out, open("transcricao.json", "w"), ensure_ascii=False, indent=1)
EOF
```

Em CPU, conte aproximadamente o tempo real do vídeo com o modelo `small`. Para vídeos acima de ~30 min, prefira pedir o SRT ao usuário ou avisar o tempo antes de começar.

Se o modelo de download não for acessível na rede do ambiente, peça o SRT.

## Identificação de falantes

Whisper não separa falantes. Se a transcrição não tiver, use o contexto (pergunta/resposta, nomes citados) e anote o falante nas frases relevantes. Em entrevista, isso evita colar pergunta de um com resposta de outro de forma enganosa.

## Erros de transcrição

Nomes próprios, siglas e termos técnicos costumam vir errados. Monte o glossário (etapa 2) e corrija no texto da decupagem. Se um erro de transcrição muda o sentido de um trecho e você não tem como confirmar, marque o corte como `revisar`.
