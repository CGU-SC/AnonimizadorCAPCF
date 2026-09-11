# Backlog

O que está previsto para este projeto. Uma linha por funcionalidade, sem
detalhe — o detalhe de cada uma é a spec, escrita uma de cada vez.

| # | Funcionalidade | O que ela entrega para quem usa | Situação |
| --- | --- | --- | --- |
| 1 | Interface da janela | A estrutura com o menu lateral (Gerar OCR / Anonimizar) e o painel principal onde cada módulo aparece | construída |
| 2 | Módulo de OCR | Transforma um documento escaneado sem texto em texto legível, usando o Tesseract local | em construção — 2 de 7 etapas: escolher o documento e ler com contagem e cancelar. Faltam a tela de conferência lado a lado, a decisão sobre o PDF que já tem texto, a tabela, salvar o `.md` e o aviso do motor faltando |
| 3 | Módulo de Anonimizador de CPF | Encontra todo CPF no texto (em qualquer formato de pontuação), mascara e gera o `.md` pronto para o assistente | prevista |
| 4 | Motor de leitura por IA local | Liga o módulo de OCR a um modelo de IA rodando na própria máquina (LM Studio) ou em servidor da UFSC, como alternativa ao Tesseract — endereço restrito à máquina ou à rede da universidade | prevista |
