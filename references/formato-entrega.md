# Formato de entrega

## cortes.json

Você escreve este arquivo usando os IDs de frase de `frases.json`. Nunca digite tempos à mão: o exportador calcula a minutagem a partir das frases.

```json
{
  "projeto": "Podcast Agro ep. 2 - Café do Cerrado",
  "fonte": "EP02_CAFE.mp4",
  "fps": 29.97,
  "duracao_min": 20,
  "duracao_max": 90,
  "premissas": "Orgânico, Reels, público produtor de café",
  "cortes": [
    {
      "id": "C01",
      "titulo": "O erro de vender para todo mundo",
      "titulo_publicacao": "Vender pra todo mundo não vende",
      "tipo": "podcast",
      "status": "aprovado",
      "trechos": [
        {"de": "F051", "ate": "F058"}
      ],
      "nao_linear": false,
      "ideia": "Sem público definido a comunicação perde força e a venda cai.",
      "gancho": "O maior erro de uma empresa é tentar vender para todo mundo.",
      "desenvolvimento": "Explica por que a mensagem dilui.",
      "fechamento": "Conhecer o público muda a forma de vender.",
      "termos_verificados": "nenhum termo externo",
      "lettering": {"formato": "A", "texto": "PÚBLICO CERTO / vende mais", "entra_em": "F056"},
      "ajustes": "Tirar o 'então' inicial.",
      "notas": {"completude": 9, "gancho": 9, "relevancia": 8, "desenvolvimento": 8, "autonomia": 10, "clareza": 8, "emocao": 7},
      "alternativas": "Versão enxuta: F051–F052 + F056–F058 (0:27)"
    }
  ],
  "descartados": [
    {"ideia": "História do primeiro cliente", "trechos": "F120–F131", "motivo": "Depende de 'o projeto do Cerrado', explicado só em F010."}
  ]
}
```

Campos:
- `status`: `aprovado`, `revisar` (passa com ressalva) ou `gancho_nao_autonomo`.
- `trechos`: lista em ordem de montagem. Mais de um item = costura. Se a ordem de montagem não seguir a ordem do vídeo, marque `nao_linear: true` e explique em `ajustes`.
- `notas`: o exportador calcula o score com os pesos padrão. Para pesos próprios, adicione `"pesos": {...}` na raiz.
- Recortar dentro de uma frase longa: use `{"de": "F051", "ate": "F051", "inicio": 312.4, "fim": 318.0}` com tempos tirados de `frases.json` (timestamps por palavra, quando existirem). Só nesse caso tempo manual é aceito.

## Arquivos gerados por `exportar_cortes.py`

| Arquivo | Uso |
|---|---|
| `decupagem.md` | documento de leitura para equipe/cliente, um bloco por corte |
| `decupagem.csv` | planilha: corte, título, entrada, saída, duração, score, ideia, lettering |
| `cortes/C01.edl` | sequência CMX3600 do corte (Premiere: Arquivo > Importar; DaVinci: Timelines > Import > EDL). Reconecte a mídia `fonte` se pedir |
| `legendas/C01.srt` | legenda da fala literal, já re-temporizada para começar em 0 na timeline do corte (blocos de até 42 caracteres) |
| `marcadores.csv` | um marcador por trecho com timecode, para a equipe localizar no vídeo bruto |
| `textos/C01.txt` | fala literal do corte, para conferência de legenda |
| `validacao.txt` | erros e avisos (duração fora da faixa, sobreposição entre cortes, não linear sem marcação) |

Margens: o exportador aplica 0,15 s antes da primeira palavra e 0,30 s depois da última, sem invadir a frase vizinha. Ajustável com `--pre` e `--pos`.
