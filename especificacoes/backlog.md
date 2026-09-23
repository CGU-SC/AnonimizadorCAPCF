# Backlog

O que está previsto para este projeto. Uma linha por funcionalidade, sem
detalhe — o detalhe de cada uma é a spec, escrita uma de cada vez.

| # | Funcionalidade | O que ela entrega para quem usa | Situação |
| --- | --- | --- | --- |
| 1 | Interface da janela | A estrutura com o menu lateral (Gerar OCR / Anonimizar) e o painel principal onde cada módulo aparece | construída |
| 2 | Módulo de OCR | Transforma um documento escaneado sem texto em texto legível, usando o Tesseract local | construída — as 7 etapas conferidas na tela, e os 26 critérios da spec 002 passando na revisão de 13/09/2026 |
| 3 | Módulo de Anonimizador de CPF | Encontra todo CPF no texto (em qualquer formato de pontuação), mascara e gera o `.md` pronto para o assistente | construída — as 8 etapas conferidas na tela, de 15 a 23/09/2026, e os 51 critérios da spec 003 conferidos: 50 na revisão de 22/09/2026, e o da reabertura do programa na tela, em 23/09 |
| 4 | Motor de leitura por IA local | Liga o módulo de OCR a um modelo de IA rodando na própria máquina (LM Studio) ou em servidor da UFSC, como alternativa ao Tesseract — endereço restrito à máquina ou à rede da universidade | prevista |
| 5 | Abrir documento do Word | Aceita `.docx` no Anonimizar, tirando o texto e as tabelas de dentro dele sem instalar nada a mais na máquina | prevista — pedida em 16/09/2026, na conferência da etapa 2 do Anonimizar. Precisa de levantamento próprio: as tabelas, o que mora fora do corpo do texto (cabeçalho, rodapé, nota, caixa de texto, comentário) e a imagem colada dentro do documento. O `.doc` antigo fica de fora: exigiria o Word instalado ou um programa a mais nas máquinas do núcleo |
