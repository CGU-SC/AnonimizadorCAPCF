# Backlog

O que está previsto para este projeto. Uma linha por funcionalidade, sem
detalhe — o detalhe de cada uma é a spec, escrita uma de cada vez.

| # | Funcionalidade | O que ela entrega para quem usa | Situação |
| --- | --- | --- | --- |
| 1 | Interface da janela | A estrutura com o menu lateral (Gerar OCR / Anonimizar) e o painel principal onde cada módulo aparece | construída |
| 2 | Módulo de OCR | Transforma um documento escaneado sem texto em texto legível, usando o Tesseract local | em spec |
| 3 | Módulo de Anonimizador de CPF | Encontra todo CPF no texto (em qualquer formato de pontuação), mascara e gera o `.md` pronto para o assistente | prevista |
| 4 | Motor de leitura por IA local | Liga o módulo de OCR a um modelo de IA rodando na própria máquina (LM Studio) ou em servidor da UFSC, como alternativa ao Tesseract — endereço restrito à máquina ou à rede da universidade | prevista |
