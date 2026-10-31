# Decupagem de Cortes — Skill para Claude

Skill que transforma vídeos longos (podcast, entrevista, aula, palestra, live, depoimento) em **cortes curtos completos**: cada corte abre uma ideia e a fecha, sem depender de nada que ficou de fora.

O princípio central: **primeiro a ideia, depois a melhor forma de contá-la, só então onde o corte começa e termina.** Achar a frase mais forte não basta; a skill procura a menor sequência de fala que transmite uma ideia completa, clara e interessante, sem distorcer quem falou.

## O que ela faz

1. Numera a transcrição em frases completas, com tempo exato de cada uma.
2. Mapeia o vídeo inteiro: núcleos de conteúdo, glossário de termos e onde cada um é explicado.
3. Monta o inventário de ideias e os candidatos a corte (entrada, desenvolvimento, saída, costuras).
4. Elimina o que não se sustenta sozinho: termo órfão, conclusão ausente, edição que muda o sentido.
5. Pontua os aprovados em 7 critérios (completude, gancho, relevância, desenvolvimento, autonomia, clareza, emoção).
6. Sugere título, gancho dos 3 primeiros segundos e frase de reforço (lettering) de 3 a 4 palavras.
7. Exporta os arquivos de edição.

### Arquivos gerados

| Arquivo | Uso |
|---|---|
| `decupagem.md` / `decupagem.csv` | decupagem para equipe e cliente |
| `cortes/C01.edl` | sequência do corte, importa no Premiere e no DaVinci |
| `legendas/C01.srt` | legenda da fala literal, sincronizada com a timeline do corte |
| `marcadores.csv` | timecode de cada trecho no vídeo bruto |
| `textos/C01.txt` | fala literal para conferência |
| `validacao.txt` | erros e avisos (duração, sobreposição, costura sem marcação) |

### Entradas aceitas

SRT, VTT, JSON do Whisper (com ou sem timestamps por palavra) ou TXT com `[mm:ss]` no início das linhas. Sem transcrição, a skill orienta a transcrever com faster-whisper.

## Instalação

**Claude (app/web):** baixe `decupagem-cortes.skill` na página de [Releases](../../releases) e importe na área de Skills das configurações do Claude.

**Claude Code:** copie a pasta da skill para o seu diretório de skills:

```bash
git clone https://github.com/biraribeiros/decupagem-cortes.git
cp -r decupagem-cortes ~/.claude/skills/decupagem-cortes
```

No Windows (PowerShell):

```powershell
git clone https://github.com/biraribeiros/decupagem-cortes.git "$env:USERPROFILE\.claude\skills\decupagem-cortes"
```

Os scripts usam só Python 3 padrão, sem dependências.

## Como usar

Mande a transcrição e peça algo como:

- "decupa esse podcast, quero cortes pra reels, público produtor rural"
- "acha os melhores trechos dessa aula, até 60 segundos cada"
- "faz a decupagem desse SRT com a minutagem pra equipe cortar no Premiere"

Os scripts também funcionam sozinhos:

```bash
python scripts/preparar_transcricao.py entrevista.srt --saida trabalho/
# escreva trabalho/cortes.json (formato em references/formato-entrega.md)
python scripts/exportar_cortes.py trabalho/cortes.json trabalho/frases.json --saida entrega/ --fps 29.97
```

## Estrutura

```
SKILL.md                      fluxo de trabalho e regras
references/metodologia.md     critérios, tipos de conteúdo, fidelidade, métricas
references/lettering-e-ganchos.md
references/formato-entrega.md
references/transcricao.md
scripts/preparar_transcricao.py
scripts/exportar_cortes.py
evals/                        casos de teste
```

## Licença

MIT. Criado por Bira Ribeiro.
