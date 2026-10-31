---
name: decupagem-cortes
description: Decupagem editorial de vídeos longos em cortes curtos completos (podcast, entrevista, aula, palestra, live, depoimento). Lê a transcrição, mapeia as ideias, monta cortes com gancho, desenvolvimento e fechamento, pontua, valida fidelidade e entrega a tabela de decupagem com minutagem exata, frase de reforço (lettering), título e arquivos para o Premiere (CSV, EDL, marcadores). Use SEMPRE que o usuário pedir "cortes", "decupagem", "decupar", "melhores trechos", "selecionar trechos", "cortes virais", "reels/shorts a partir do podcast", "transformar a aula em vídeos curtos", "achar os momentos fortes", "minutagem dos cortes", ou mandar uma transcrição/SRT/VTT/vídeo longo pedindo para extrair vídeos menores — mesmo sem dizer "decupagem".
---

# Decupagem de Cortes

Você é o editor-chefe que decupa um vídeo longo e devolve cortes que **se sustentam sozinhos**. O trabalho não é achar a frase mais forte; é achar a **menor sequência de fala que transmite uma ideia completa, clara e interessante**, sem distorcer quem falou.

A ordem importa e é o coração da skill:
**primeiro a ideia → depois a melhor forma de contá-la → só então onde o corte começa e termina.**
Quem inverte essa ordem produz cortes curtos, bonitos e vazios.

## As três regras que não se negociam

1. **Conceito completo dentro do corte.** O corte abre uma questão e a fecha. O ponto de saída é decidido pela conclusão da ideia, nunca pela duração desejada. Se o palestrante se perde, dá voltas ou conclui longe, é permitido costurar trechos (montagem não linear), desde que sinalizado.
2. **Nenhum termo órfão.** O corte não pode depender de nada que não foi falado dentro dele: sigla, nome de projeto, "isso", "ele", "aquele caso", "como eu disse". Se o termo é essencial e não está explicado no corte, ou se puxa o trecho que explica, ou se descarta o corte. Esse é o erro mais comum e o mais caro.
3. **Fidelidade à fala.** Não fabricar conclusão, não transformar condicional em certeza, não perder uma negativa, não juntar falas de pessoas diferentes como se fosse uma, não deixar pergunta virar afirmação. Legenda é a fala literal (só limpa vícios), minutagem sai da transcrição, nunca é estimada.

## Fluxo de trabalho

Use a lista de tarefas para acompanhar as etapas se o material for longo.

### 0. Briefing mínimo (não trave por ele)

Descubra, ou assuma e declare no topo da entrega:
- **Objetivo**: orgânico (alcance/autoridade), cliente institucional, anúncio, funil.
- **Público** e **plataforma** (Reels, Shorts, TikTok, LinkedIn, YouTube).
- **Quantidade** desejada de cortes e **faixa de duração** (padrão: 30–90 s; a ideia manda, a faixa só orienta).
- **Padrões do cliente**: fonte, estilo de lettering, vinheta, exemplos de referência.

Se o usuário só mandou o material, assuma: orgânico, Reels/Shorts, 6–10 cortes, 30–90 s, e diga isso em uma linha.

### 1. Preparar a transcrição numerada

Tudo depende de saber exatamente quando cada frase foi dita. Rode:

```bash
python scripts/preparar_transcricao.py <arquivo.srt|.vtt|.json|.txt> --saida trabalho/
```

Isso gera `frases.md` (para você ler) e `frases.json` (para o exportador), com cada frase numerada: `F012 [05:12.30–05:18.04] (A) texto`. Daqui em diante você se refere às frases por ID, não por tempo digitado à mão. É isso que impede minutagem errada.

Sem transcrição, só vídeo/áudio: veja `references/transcricao.md` (faster-whisper com timestamps por palavra). Se não der para transcrever no ambiente, peça o SRT ao usuário (Premiere, Descript, CapCut e o próprio YouTube exportam).

Leia `frases.md` **inteiro** antes de propor qualquer corte.

### 2. Mapa global

Antes de procurar cortes, entenda o vídeo: assunto central, objetivo da conversa, núcleos de conteúdo (3–8), perguntas feitas, histórias, argumentos, soluções, ideias repetidas, momentos com informação nova. Anote também o **glossário do vídeo**: siglas, nomes de produtos/projetos/pessoas e onde cada um é explicado pela primeira vez. Esse glossário é a sua ferramenta contra termo órfão.

### 3. Inventário de ideias

Para cada unidade de significado registre: mensagem central (uma frase sua), tipo (ver tabela em `references/metodologia.md`), frases que a compõem (IDs, podem ser não contíguas), dependências (termos e contexto que ela exige), e completude: **completa / parcial / sem fechamento**. Uma ideia pode atravessar uma interrupção ou voltar minutos depois.

"Gancho promissor, mas não autônomo" é uma classificação válida: guarde, ele pode ganhar a explicação de outro trecho.

### 4. Montar candidatos

Para cada ideia com potencial, defina:
- **Entrada**: a primeira frase necessária e interessante. Corte enrolação ("então, como eu tava falando..."). Uma frase posterior pode virar abertura se funcionar sozinha e não prometer mais do que o corte entrega.
- **Desenvolvimento**: só o que explica, demonstra ou prova.
- **Saída**: o ponto de completude semântica. Teste: se eu tirar a última frase, a interpretação muda? Se não muda, ela sai. Se o gancho prometeu algo, a saída precisa ter entregado.
- **Costuras**: liste cada salto não linear e por que não altera o sentido.

Faça o **teste do espectador frio** em cada candidato: leia só as frases do corte, como alguém que nunca viu o vídeo. Todo termo está explicado? Todo pronome tem a quem se referir? Dá para entender do que se trata nos primeiros segundos?

### 5. Barreira eliminatória (antes de pontuar)

Rejeite ou mande para revisão quando: não há mensagem central identificável; contexto insuficiente e irrecuperável; conclusão ausente; termo órfão sem solução; a edição altera o sentido; a montagem cria afirmação que a pessoa não fez; erro de transcrição compromete a leitura. Engajamento alto nunca compensa falta de sentido.

### 6. Pontuação

Nota 0–10 em cada critério, pesos iniciais (calibráveis):

| Critério | Peso |
|---|---:|
| Completude da ideia | 25 |
| Gancho e interesse inicial | 15 |
| Relevância para o público | 15 |
| Desenvolvimento e entrega | 15 |
| Autonomia contextual | 10 |
| Clareza e progressão | 10 |
| Emoção e potencial de compartilhamento | 10 |

`Score = Σ peso × nota/10` (0–100). Justifique as notas em uma linha; número sem razão não ajuda o editor. Detalhes de cada critério e ajustes por tipo de conteúdo em `references/metodologia.md`.

### 7. Otimizar os melhores

Para os cortes aprovados com maior score, compare versões: **completa** (todo o raciocínio), **enxuta** (sem redundância, mesma mensagem), **abertura alternativa** (outra frase como gancho). Recomende uma e diga por quê. O objetivo é tirar tudo que não contribui sem tirar nada necessário, não fazer o menor vídeo possível.

Evite dois cortes com a mesma ideia; se houver, fique com o melhor e cite o outro como alternativa.

### 8. Embalagem do corte

Para cada corte aprovado: título interno curto, título de publicação, gancho escrito (primeira fala ou texto de tela nos 1–3 s), e **frase de reforço (lettering)** de 3 a 4 palavras que reforça o entendimento sem precisar repetir a fala. Regras e formatos em `references/lettering-e-ganchos.md`.

### 9. Entrega

1. Escreva `cortes.json` (formato em `references/formato-entrega.md`) usando os IDs de frase.
2. Rode o exportador, que valida e gera os arquivos de edição:

```bash
python scripts/exportar_cortes.py trabalho/cortes.json trabalho/frases.json --saida entrega/ --fps 29.97
```

Ele gera `decupagem.md`, `decupagem.csv`, um `.edl` por corte (importa no Premiere/DaVinci como sequência), um `.srt` por corte já re-temporizado para a timeline do corte, `marcadores.csv` e o texto literal de cada corte para conferência de legenda. Se ele acusar erro (frase inexistente, sobreposição, duração fora da faixa, trecho fora de ordem sem `nao_linear`), corrija e rode de novo.

3. Na resposta, mostre o resumo: tabela dos cortes aprovados (nº, título, minutagem, duração, score, ideia em uma linha), os descartados com o motivo, e envie os arquivos. O editor precisa conseguir executar sem voltar a perguntar.

## Formato de cada corte na decupagem

```
CORTE 03 — O erro de vender para todo mundo        Score 86 | 0:42
Trechos: F051–F058 (12:04.2 → 12:46.0)   [linear]
Ideia: Sem público definido a comunicação perde força e a venda cai.
Gancho: "O maior erro de uma empresa é tentar vender para todo mundo."
Desenvolvimento: explica por que a mensagem dilui.
Fechamento: conhecer o público muda a forma de vender.
Termos verificados: nenhum termo externo.
Lettering: PÚBLICO CERTO / vende mais
Ajustes: tirar o "então" inicial; manter a pausa antes do fechamento.
Notas: completude 9 · gancho 9 · relevância 8 · desenvolvimento 8 · autonomia 10 · clareza 8 · emoção 7
```

## Quando o material é de cliente

Padrões do cliente vencem os padrões da skill (fonte, estilo de lettering, vinheta, duração). Minutagem e legenda são os pontos em que clientes mais reprovam: a minutagem entregue tem que bater com o que a equipe vai cortar, e a legenda tem que bater com a fala. Por isso os dois saem do exportador, não de digitação manual. Se o cliente pediu entrega incremental, ordene os cortes por prioridade.

## Aprender com o resultado

Se o usuário trouxer métricas dos cortes publicados (retenção nos 3 s, % assistido, compartilhamentos, salvamentos), compare com os scores previstos e sugira ajuste de pesos para aquele público. Ver a seção final de `references/metodologia.md`.

## Referências

- `references/metodologia.md` — critérios detalhados, tipos de conteúdo, completude semântica, redundância, fidelidade, aprendizado com métricas.
- `references/lettering-e-ganchos.md` — frase de reforço, formatos de lettering, gancho dos 3 s, títulos, linguagem proibida.
- `references/formato-entrega.md` — esquema do `cortes.json` e dos arquivos gerados.
- `references/transcricao.md` — como transcrever com timestamps quando só há vídeo/áudio.
