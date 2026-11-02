# Relatório Financeiro — Power BI com foco em UX

Solução do desafio de projeto da DIO: atualizar o relatório financeiro com foco na experiência do usuário (posicionamento, contraste, proporção áurea e segmentação dos dados).

## Conteúdo
- `Relatorio_Financeiro_UX.pbix`: relatório final com 3 páginas.
- `scripts/`: scripts Python que geraram o layout a partir do relatório original (`icons.py` cria os ícones, `build.py` monta o `.pbix`).

## Páginas
1. **Home**: capa com botão "Explorar análise" (destaque ao focalizar).
2. **Visão Geral**: filtro de período, 5 indicadores (Vendas, Lucro, Unidades, Descontos, COGS) e painéis de Período, Segmento, Produto e País, com botões para alternar barras/pizza e treemap/mapa.
3. **Detalhamento**: matriz de vendas e lucro (Segmento > País × Ano), lucro por produto, vendas por semestre e filtros de Segmento e Ano.

## Navegação
Menu lateral nas páginas 2 e 3 com Home, Visão geral e Detalhes. A página atual fica destacada em rosa; os demais botões clareiam ao focalizar.

## Decisões de design
- Divisão de colunas ~1,6:1 (694 px / 430 px), seguindo a proporção áurea.
- Texto branco sobre painéis escuros; cores de segmento consistentes entre os gráficos.

## Observação
O arquivo foi gerado editando o layout do `.pbix` original, sem abrir no Power BI Desktop durante a geração. Ao abrir, o Desktop pode pedir para atualizar os dados.
