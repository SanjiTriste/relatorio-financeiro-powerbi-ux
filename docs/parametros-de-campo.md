# Parâmetros de campo (Field Parameters)

A página **História** alterna as visões com botões e favoritos. Para usar parâmetros de campo reais do Power BI, crie as duas tabelas abaixo no Power BI Desktop e troque os campos dos dois visuais da página.

## 1. Medidas de apoio (aba Modelagem > Nova medida)
```DAX
Total Vendas = SUM(financials[ Sales])
Total Lucro = SUM(financials[Profit])
Total Unidades = SUM(financials[Units Sold])
Total Descontos = SUM(financials[Discounts])
Total Custo = SUM(financials[COGS])
```
(O nome da coluna de vendas tem um espaço no início: `[ Sales]`.)

## 2. Parâmetro de categorias
Modelagem > Novo parâmetro > Campos. Marque Segment, Country e Product, mantenha "Adicionar segmentação a esta página" e renomeie para `Parâmetro Categoria`. O código gerado equivale a:
```DAX
Parâmetro Categoria = {
    ("Segmento", NAMEOF('financials'[Segment]), 0),
    ("País",     NAMEOF('financials'[Country]), 1),
    ("Produto",  NAMEOF('financials'[Product]), 2)
}
```

## 3. Parâmetro de valores
Mesmo caminho, marcando as cinco medidas, com o nome `Parâmetro Valor`:
```DAX
Parâmetro Valor = {
    ("Vendas",     NAMEOF('financials'[Total Vendas]),    0),
    ("Lucro",      NAMEOF('financials'[Total Lucro]),     1),
    ("Unidades",   NAMEOF('financials'[Total Unidades]),  2),
    ("Descontos",  NAMEOF('financials'[Total Descontos]), 3),
    ("Custo",      NAMEOF('financials'[Total Custo]),     4)
}
```

## 4. Aplicar nos visuais
- Gráfico de barras "Lucro por categoria": eixo = `Parâmetro Categoria`, valor = `Total Lucro`.
- Gráfico de área "Evolução mensal": eixo = Date (mês), valor = `Parâmetro Valor`.
Depois, remova os botões e gráficos empilhados e deixe as segmentações dos parâmetros no lugar.
