# Relatório Financeiro com Storytelling e Parâmetros (Power BI)

Desafio final da DIO (Formação Power BI Analyst): evolução do relatório financeiro com foco em UX, agora com uma página de **storytelling** e visões alternáveis por categoria e por valor.

## Conteúdo
- `Relatorio_Financeiro_Storytelling.pbix`: relatório com 4 páginas.
- `docs/parametros-de-campo.md`: DAX e passos para criar os parâmetros de campo reais.
- `scripts/`: Python que gerou o layout a partir do relatório original.

## Páginas
1. **Home**: capa com botão "Explorar análise".
2. **Visão Geral**: indicadores, vendas por período, segmento, produto e país.
3. **Detalhamento**: matriz de vendas e lucro, lucro por produto e vendas por semestre.
4. **História**: relatório para apresentar a um cliente. Título "Vender mais não é lucrar mais", dois capítulos e uma conclusão.

## A história (página 4)
- **Capítulo 1, quem gera o lucro?** Visão por categoria (Segmento, País, Produto). Government tem 44% das vendas e 67% do lucro. Enterprise tem 16,5% das vendas e lucro negativo. Channel Partners tem só 1,5% das vendas, mas a maior margem (73%).
- **Capítulo 2, como o negócio evoluiu?** Visão por valor (Vendas, Lucro, Unidades, Descontos e Custo) ao longo dos meses. 2014 teve 92,3 mi em vendas contra 26,4 mi em 2013 (base começa em setembro), com margem estável perto de 14%.
- **Conclusão:** rever preço e custo do Enterprise e ampliar o canal Channel Partners.

## Parâmetros
Na página História, as duas visões alternam com botões e favoritos (o botão ativo fica em rosa). O arquivo `docs/parametros-de-campo.md` traz o passo a passo para trocar essa alternância por parâmetros de campo nativos do Power BI.

## Navegação e estilo
Menu lateral em todas as páginas internas, com destaque ao focalizar e página atual marcada. Painéis escuros sobre fundo roxo, texto branco e proporção áurea (694 / 416 px) na divisão das colunas.

## Observação
O arquivo foi gerado editando o layout do `.pbix`, sem abrir no Power BI Desktop durante a geração. Ao abrir, o Desktop pode pedir para atualizar os dados.

## Versões do relatório
- `Relatorio_Financeiro_UX.pbix`: versão do desafio de UX (3 páginas, sem a página História).
- `Relatorio_Financeiro_Storytelling.pbix`: versão final do desafio de storytelling e parâmetros (4 páginas).
