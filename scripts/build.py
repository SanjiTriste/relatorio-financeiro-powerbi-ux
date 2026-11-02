import json, copy, zipfile, random, shutil, os, re

SRC = '/home/claude/in/x_p1'
ORIG = '/home/claude/in/p1.pbix'
OUT = '/home/claude/out/Relatorio_Financeiro_UX.pbix'
random.seed(7)

j = json.loads(open(f'{SRC}/Report/Layout', 'rb').read().decode('utf-16-le'))
cfg = json.loads(j['config'])

# ---------- helpers ----------
def dumps(o): return json.dumps(o, separators=(',', ':'))
def L(v): return {"expr": {"Literal": {"Value": v}}}
def S(v): return L("'%s'" % v)
def D(n): return L("%sD" % n)
def N(n): return L("%sL" % n)
def B(b): return L('true' if b else 'false')
def C(h): return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % h}}}}}
def newid(): return ''.join(random.choice('0123456789abcdef') for _ in range(20))

PINK = '#E8588F'; PINK_D = '#C2427A'
PANEL = '#1A0933'; PANEL_T = 38
WHITE = '#FFFFFF'; SOFT = '#D8C7F2'
SEG = {'Government': '#F5C518', 'Midmarket': '#E8588F', 'Channel Partners': '#8F7CF0',
       'Enterprise': '#35C6B6', 'Small Business': '#F4864A'}

PG_HOME = 'ReportSection3ee2a4126027e0713e1d'
PG_OVER = 'ReportSection'
PG_DET = 'ReportSection5e4ef9ee0e160b92ecde'

def make_container(name, x, y, w, h, z, tab, single, parent=None, extra=None, query=None, dt=None):
    pos = {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": tab}
    c = {"name": name, "layouts": [{"id": 0, "position": pos}], "singleVisual": single}
    if parent: c["parentGroupName"] = parent
    cont = {"x": x, "y": y, "z": z, "width": w, "height": h, "config": dumps(c), "filters": "[]", "tabOrder": tab}
    if query: cont["query"] = query
    if dt: cont["dataTransforms"] = dt
    return cont

def set_pos(cont, x, y, w, h, z=None, tab=None):
    c = json.loads(cont['config'])
    p = c['layouts'][0]['position']
    p.update(x=x, y=y, width=w, height=h)
    cont.update(x=x, y=y, width=w, height=h)
    if z is not None: p['z'] = z; cont['z'] = z
    if tab is not None: p['tabOrder'] = tab; cont['tabOrder'] = tab
    cont['config'] = dumps(c)

def edit(cont, fn):
    c = json.loads(cont['config']); fn(c); cont['config'] = dumps(c)

def set_parent(cont, parent):
    edit(cont, lambda c: c.__setitem__('parentGroupName', parent))

# ---------- visual factories ----------
def shape(x, y, w, h, z, tab, fill=PANEL, transp=PANEL_T, rnd=14, parent=None, name=None, line=None):
    obj = {"shape": [{"properties": {"tileShape": S('rectangle'), "roundEdge": N(rnd)}}],
           "rotation": [{"properties": {"shapeAngle": N(0)}}],
           "fill": [{"properties": {"fillColor": C(fill), "transparency": D(transp)}, "selector": {"id": "default"}}],
           "outline": [{"properties": {"show": B(False)}}]}
    if line:
        obj["outline"] = [{"properties": {"show": B(True), "lineColor": C(line), "weight": D(1)}}]
    sv = {"visualType": "shape", "drillFilterOtherVisuals": True, "objects": obj}
    return make_container(name or newid(), x, y, w, h, z, tab, sv, parent)

def image(x, y, w, h, z, tab, item, parent=None, alt=None):
    vc = {}
    if alt: vc["general"] = [{"properties": {"altText": S(alt)}}]
    sv = {"visualType": "image", "drillFilterOtherVisuals": True,
          "objects": {"general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {
              "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": item}}}}}]}}
    if vc: sv["vcObjects"] = vc
    return make_container(newid(), x, y, w, h, z, tab, sv, parent)

def textbox(x, y, w, h, z, tab, text, size=14, bold=True, color=WHITE, align='left', parent=None):
    run = {"value": text, "textStyle": {"fontSize": "%spt" % size, "color": color}}
    if bold: run["textStyle"]["fontWeight"] = "bold"
    para = {"textRuns": [run], "horizontalTextAlignment": align}
    sv = {"visualType": "textbox", "drillFilterOtherVisuals": True,
          "objects": {"general": [{"properties": {"paragraphs": [para]}}]},
          "vcObjects": {"background": [{"properties": {"show": B(False)}}]}}
    return make_container(newid(), x, y, w, h, z, tab, sv, parent)

def button(x, y, w, h, z, tab, link, text=None, size=10, fcolor=WHITE, base=None, base_t=0,
           hover=(WHITE, 80), press=(PINK, 0), rnd=12, parent=None, alt=None, bold=False, name=None):
    fill = []
    if base: fill.append({"properties": {"show": B(True), "fillColor": C(base), "transparency": D(base_t)}, "selector": {"id": "default"}})
    else: fill.append({"properties": {"show": B(False)}, "selector": {"id": "default"}})
    if hover: fill.append({"properties": {"show": B(True), "fillColor": C(hover[0]), "transparency": D(hover[1])}, "selector": {"id": "hover"}})
    if press: fill.append({"properties": {"show": B(True), "fillColor": C(press[0]), "transparency": D(press[1])}, "selector": {"id": "pressed"}})
    obj = {"icon": [{"properties": {"shapeType": S('blank')}, "selector": {"id": "default"}}, {"properties": {"show": B(False)}}],
           "shape": [{"properties": {"roundEdge": N(rnd)}, "selector": {"id": "default"}}],
           "outline": [{"properties": {"show": B(False)}}],
           "fill": fill}
    if text:
        tp = {"text": S(text), "fontSize": D(size), "fontColor": C(fcolor)}
        if bold: tp["bold"] = B(True)
        obj["text"] = [{"properties": {"show": B(True)}}, {"properties": tp, "selector": {"id": "default"}}]
    else:
        obj["text"] = [{"properties": {"show": B(False)}}]
    vl = dict(show=B(True))
    if link[0] == 'page': vl.update(type=S('PageNavigation'), navigationSection=S(link[1]))
    elif link[0] == 'bookmark': vl.update(type=S('Bookmark'), bookmark=S(link[1]))
    elif link[0] == 'url': vl.update(type=S('WebUrl'), webUrl=S(link[1]))
    vc = {"visualLink": [{"properties": vl}]}
    if alt: vc["general"] = [{"properties": {"altText": S(alt)}}]
    sv = {"visualType": "actionButton", "drillFilterOtherVisuals": True, "objects": obj, "vcObjects": vc}
    return make_container(name or newid(), x, y, w, h, z, tab, sv, parent)

def group(name, title, x, y, w, h, z, tab):
    c = {"name": name, "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": tab}}],
         "singleVisualGroup": {"displayName": title, "groupMode": 0,
                               "objects": {"background": [{"properties": {"show": B(False)}}]}}}
    return {"x": x, "y": y, "z": z, "width": w, "height": h, "config": dumps(c), "filters": "[]", "tabOrder": tab}

# ---------- query helpers ----------
def col(c): return {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": c}}
def agg(c, fn=0): return {"Aggregation": {"Expression": col(c), "Function": fn}}
def colE(c): return {"Column": {"Expression": {"SourceRef": {"Entity": "financials"}}, "Property": c}}
def aggE(c, fn=0): return {"Aggregation": {"Expression": colE(c), "Function": fn}}
FROM = [{"Name": "f", "Entity": "financials", "Type": 0}]
LABEL = {' Sales': 'Vendas', 'Profit': 'Lucro', 'Units Sold': 'Unidades Vendidas', 'Discounts': 'Descontos', 'COGS': 'Custo (COGS)'}

def sel_col(c): d = col(c); d["Name"] = "financials.%s" % c; return d
def sel_sum(c): d = agg(c); d["Name"] = "Sum(financials.%s)" % c; return d

def cmd(select, binding, orderby=None):
    q = {"Version": 2, "From": FROM, "Select": select}
    if orderby: q["OrderBy"] = orderby
    return dumps({"Commands": [{"SemanticQueryDataShapeCommand": {"Query": q, "Binding": binding, "ExecutionMetricsKind": 1}}]}), q

def sel_meta(c, kind, roles, disp=None):
    if kind == 'sum':
        return {"displayName": disp or ("Soma de %s" % c), "queryName": "Sum(financials.%s)" % c, "roles": roles,
                "type": {"category": None, "underlyingType": 259}, "expr": aggE(c)}
    ut = 260 if c == 'Year' else 1
    return {"displayName": disp or c, "queryName": "financials.%s" % c, "roles": roles,
            "type": {"category": None, "underlyingType": ut}, "expr": colE(c)}

def card(x, y, w, h, z, tab, c, parent=None):
    name = newid(); disp = LABEL[c]
    sel = [sel_sum(c)]
    qs, q = cmd(sel, {"Primary": {"Groupings": [{"Projections": [0]}]}, "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}}, "Version": 1})
    ref = "Sum(financials.%s)" % c
    obj = {"labels": [{"properties": {"fontSize": D(26), "color": C(WHITE)}}],
           "categoryLabels": [{"properties": {"show": B(True), "fontSize": D(11), "color": C(SOFT)}}],
           "wordWrap": [{"properties": {"show": B(True)}}]}
    sv = {"visualType": "card", "projections": {"Values": [{"queryRef": ref}]}, "prototypeQuery": q,
          "columnProperties": {ref: {"displayName": disp}}, "drillFilterOtherVisuals": True, "hasDefaultSort": True,
          "objects": obj, "vcObjects": {"background": [{"properties": {"show": B(False)}}]}}
    dt = {"objects": obj, "projectionOrdering": {"Values": [0]},
          "queryMetadata": {"Select": [{"Restatement": disp, "Name": ref, "Type": 1}]},
          "visualElements": [{"DataRoles": [{"Name": "Values", "Projection": 0, "isActive": False}]}],
          "selects": [sel_meta(c, 'sum', {"Values": True}, disp)]}
    return make_container(name, x, y, w, h, z, tab, sv, parent, query=qs, dt=dumps(dt))

def chart(vtype, x, y, w, h, z, tab, cat, meas, color, parent=None, labels=True):
    name = newid()
    sel = [sel_sum(meas), sel_col(cat)]
    order = [{"Direction": 2, "Expression": agg(meas)}] if cat != 'Semestres' else [{"Direction": 1, "Expression": col(cat)}]
    qs, q = cmd(sel, {"Primary": {"Groupings": [{"Projections": [0, 1]}]}, "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 1000}}}, "Version": 1}, order)
    mref = "Sum(financials.%s)" % meas; cref = "financials.%s" % cat
    axis = {"labelColor": C(WHITE), "showAxisTitle": B(False)}
    obj = {"dataPoint": [{"properties": {"fill": C(color)}}],
           "labels": [{"properties": {"show": B(labels), "color": C(WHITE), "fontSize": D(10)}}],
           "categoryAxis": [{"properties": dict(axis)}],
           "valueAxis": [{"properties": {"show": B(False), "labelColor": C(WHITE), "showAxisTitle": B(False)}}]}
    sv = {"visualType": vtype, "projections": {"Y": [{"queryRef": mref}], "Category": [{"queryRef": cref, "active": True}]},
          "prototypeQuery": q, "drillFilterOtherVisuals": True, "hasDefaultSort": True, "objects": obj,
          "vcObjects": {"background": [{"properties": {"show": B(False)}}], "title": [{"properties": {"show": B(False)}}]}}
    dt = {"objects": obj, "projectionOrdering": {"Y": [0], "Category": [1]},
          "projectionActiveItems": {"Category": [{"queryRef": cref, "suppressConcat": False}]},
          "queryMetadata": {"Select": [{"Restatement": "Soma de %s" % meas, "Name": mref, "Type": 1}, {"Restatement": cat, "Name": cref, "Type": 2048}]},
          "visualElements": [{"DataRoles": [{"Name": "Y", "Projection": 0, "isActive": False}, {"Name": "Category", "Projection": 1, "isActive": True}]}],
          "selects": [dict(sel_meta(meas, 'sum', {"Y": True}), sort=2, sortOrder=0) if cat != 'Semestres' else sel_meta(meas, 'sum', {"Y": True}),
                      sel_meta(cat, 'col', {"Category": True})]}
    return make_container(name, x, y, w, h, z, tab, sv, parent, query=qs, dt=dumps(dt))

def slicer(x, y, w, h, z, tab, c):
    name = newid()
    sel = [sel_col(c)]
    qs, q = cmd(sel, {"Primary": {"Groupings": [{"Projections": [0]}]}, "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 200}}}, "Version": 1},
                [{"Direction": 1, "Expression": col(c)}])
    ref = "financials.%s" % c
    obj = {"data": [{"properties": {"mode": S('Dropdown')}}],
           "header": [{"properties": {"show": B(False)}}],
           "selection": [{"properties": {"selectAllCheckboxEnabled": B(True), "singleSelect": B(False)}}],
           "items": [{"properties": {"fontColor": C(WHITE), "background": C('#2A1250'), "textSize": D(12)}}]}
    sv = {"visualType": "slicer", "projections": {"Values": [{"queryRef": ref, "active": True}]}, "prototypeQuery": q,
          "drillFilterOtherVisuals": True, "hasDefaultSort": True, "objects": obj,
          "vcObjects": {"background": [{"properties": {"show": B(True), "color": C('#2A1250'), "transparency": D(0)}}]}}
    dt = {"objects": obj, "projectionOrdering": {"Values": [0]},
          "projectionActiveItems": {"Values": [{"queryRef": ref, "suppressConcat": False}]},
          "queryMetadata": {"Select": [{"Restatement": c, "Name": ref, "Type": 2048}]},
          "visualElements": [{"DataRoles": [{"Name": "Values", "Projection": 0, "isActive": True}]}],
          "selects": [sel_meta(c, 'col', {"Values": True})]}
    return make_container(name, x, y, w, h, z, tab, sv, None, query=qs, dt=dumps(dt))

def matrix(x, y, w, h, z, tab):
    name = newid()
    rows = ['Segment', 'Country']; colsy = 'Year'; vals = [' Sales', 'Profit']
    sel = [sel_col('Segment'), sel_col('Country'), sel_col('Year'), sel_sum(' Sales'), sel_sum('Profit')]
    binding = {"Primary": {"Groupings": [{"Projections": [0, 1], "Subtotal": 1}]},
               "Secondary": {"Groupings": [{"Projections": [2, 3, 4]}]},
               "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 500}}, "Secondary": {"Top": {"Count": 100}}},
               "Version": 1}
    qs, q = cmd(sel, binding, [{"Direction": 1, "Expression": col('Segment')}])
    refs = {c: "financials.%s" % c for c in ['Segment', 'Country', 'Year']}
    sref = "Sum(financials. Sales)"; pref = "Sum(financials.Profit)"
    colorsH = {"fontColor": C(WHITE), "backColor": C('#7A3FB0'), "fontSize": D(11)}
    obj = {"columnHeaders": [{"properties": dict(colorsH)}],
           "rowHeaders": [{"properties": {"fontColor": C(WHITE), "backColor": C('#341660'), "fontSize": D(11)}}],
           "values": [{"properties": {"fontColorPrimary": C(WHITE), "backColorPrimary": C('#24104A'),
                                      "fontColorSecondary": C(WHITE), "backColorSecondary": C('#2C1558'), "fontSize": D(11)}}],
           "total": [{"properties": {"fontColor": C(WHITE), "backColor": C('#7A3FB0'), "fontSize": D(11)}}],
           "grid": [{"properties": {"gridHorizontal": B(True), "gridHorizontalColor": C('#5B3A8A'),
                                    "gridVertical": B(False), "outlineColor": C('#5B3A8A')}}]}
    sv = {"visualType": "pivotTable",
          "projections": {"Rows": [{"queryRef": refs['Segment'], "active": True}, {"queryRef": refs['Country'], "active": True}],
                          "Columns": [{"queryRef": refs['Year'], "active": True}],
                          "Values": [{"queryRef": sref}, {"queryRef": pref}]},
          "prototypeQuery": q,
          "columnProperties": {sref: {"displayName": "Vendas"}, pref: {"displayName": "Lucro"}},
          "drillFilterOtherVisuals": True, "hasDefaultSort": True, "objects": obj,
          "vcObjects": {"background": [{"properties": {"show": B(False)}}], "title": [{"properties": {"show": B(False)}}]}}
    dt = {"objects": obj, "projectionOrdering": {"Rows": [0, 1], "Columns": [2], "Values": [3, 4]},
          "projectionActiveItems": {"Rows": [{"queryRef": refs['Segment'], "suppressConcat": False}, {"queryRef": refs['Country'], "suppressConcat": False}],
                                    "Columns": [{"queryRef": refs['Year'], "suppressConcat": False}]},
          "queryMetadata": {"Select": [{"Restatement": "Segment", "Name": refs['Segment'], "Type": 2048},
                                       {"Restatement": "Country", "Name": refs['Country'], "Type": 2048},
                                       {"Restatement": "Year", "Name": refs['Year']},
                                       {"Restatement": "Vendas", "Name": sref, "Type": 1},
                                       {"Restatement": "Lucro", "Name": pref, "Type": 1}]},
          "visualElements": [{"DataRoles": [{"Name": "Rows", "Projection": 0, "isActive": True}, {"Name": "Rows", "Projection": 1, "isActive": True},
                                            {"Name": "Columns", "Projection": 2, "isActive": True},
                                            {"Name": "Values", "Projection": 3, "isActive": False}, {"Name": "Values", "Projection": 4, "isActive": False}]}],
          "selects": [sel_meta('Segment', 'col', {"Rows": True}), sel_meta('Country', 'col', {"Rows": True}),
                      sel_meta('Year', 'col', {"Columns": True}),
                      sel_meta(' Sales', 'sum', {"Values": True}, "Vendas"), sel_meta('Profit', 'sum', {"Values": True}, "Lucro")]}
    return make_container(name, x, y, w, h, z, tab, sv, None, query=qs, dt=dumps(dt))

# ---------- sidebar ----------
RES = {'home': 'icon_home9001.png', 'overview': 'icon_overview9002.png', 'detail': 'icon_detail9003.png', 'logo': 'logo_dio9004.png'}
NAV = [('home', 'Home', PG_HOME), ('overview', 'Visão geral', PG_OVER), ('detail', 'Detalhes', PG_DET)]
PIN_ITEM = 'Untitled_design_(4)560860300455668.png'
DIO_URL = 'https://web.dio.me/play?section_type=formation&tab=programas'

def sidebar(active, z0, t0):
    out = []; z = z0; t = t0
    def nz():
        nonlocal z, t
        z += 10; t += 10
        return z, t
    a, b = nz(); out.append(shape(20, 20, 92, 680, a, b, PANEL, PANEL_T, 16, name=newid()))
    a, b = nz(); out.append(image(31, 38, 70, 31, a, b, RES['logo'], alt='Logotipo DIO'))
    y = 130
    for key, label, pg in NAV:
        is_active = (pg == active)
        if is_active:
            a, b = nz(); out.append(shape(26, y, 80, 86, a, b, PINK, 0, 14))
        a, b = nz(); out.append(image(49, y + 10, 34, 34, a, b, RES[key], alt='Ícone ' + label))
        a, b = nz(); out.append(textbox(26, y + 50, 80, 26, a, b, label, 9, True, WHITE if is_active else SOFT, 'center'))
        if not is_active:
            a, b = nz(); out.append(button(26, y, 80, 86, a, b, ('page', pg), None, hover=(WHITE, 78), press=(PINK, 20), rnd=14,
                                           alt='Ir para ' + label))
        y += 98
    a, b = nz(); out.append(image(46, 632, 40, 40, a, b, PIN_ITEM, alt='Sobre a DIO'))
    a, b = nz(); out.append(button(40, 626, 52, 52, a, b, ('url', DIO_URL), None, hover=(WHITE, 78), press=(PINK, 20), rnd=26, alt='Abrir plataforma DIO'))
    return out

# =====================================================================
# PAGE 1: HOME
# =====================================================================
home = j['sections'][0]
for v in home['visualContainers']:
    c = json.loads(v['config'])
    if c['singleVisual']['visualType'] == 'actionButton':
        o = c['singleVisual']['objects']
        o['fill'] = [{"properties": {"show": B(False)}, "selector": {"id": "default"}},
                     {"properties": {"show": B(True), "fillColor": C(WHITE), "transparency": D(82)}, "selector": {"id": "hover"}},
                     {"properties": {"show": B(True), "fillColor": C(PINK), "transparency": D(40)}, "selector": {"id": "pressed"}}]
        o['shape'] = [{"properties": {"roundEdge": N(60)}, "selector": {"id": "default"}}]
        c['singleVisual']['vcObjects']['general'] = [{"properties": {"altText": S('Explorar análise: abrir a Visão Geral')}}]
        v['config'] = dumps(c)
home['displayName'] = 'Home'

# =====================================================================
# PAGE 2: VISAO GERAL
# =====================================================================
ov = j['sections'][1]
byname = {json.loads(v['config'])['name']: v for v in ov['visualContainers']}
def g(n): return copy.deepcopy(byname[n])

G_FILTRO, G_TEMPO, G_SEG, G_PAIS = 'd2969ade29b747921c30', '9ba478b9b8a3952c9b00', '9addf5c4242a73dc8873', '727b51b31571a6e610a6'
new = []

# background (reuse original purple)
bg = g('5cca43fb4a592e1ed969'); set_pos(bg, 0, 0, 1280, 720, 0, 0); new.append(bg)

CX, CW = 136, 1124
# --- header + KPI group
gf = group(G_FILTRO, 'Cabeçalho e indicadores', CX, 24, CW, 156, 1000, 1000)
new.append(gf)
t = 1010; z = 1010
def zt():
    global z, t
    z += 10; t += 10
    return z, t
a, b = zt(); tx = textbox(0, 0, 560, 48, a, b, 'Visão Geral de Vendas', 26, True, WHITE, 'left', G_FILTRO); new.append(tx)
a, b = zt(); new.append(textbox(560, 8, 200, 32, a, b, 'Selecione o período', 12, False, SOFT, 'right', G_FILTRO))
sl = g('ae85209b2ee41bd6e209'); set_pos(sl, 772, 2, 252, 44, *zt()); set_parent(sl, G_FILTRO)
def style_slicer(c):
    o = c['singleVisual']['objects']
    o['date'] = [{"properties": {"textSize": D(12), "fontColor": C(WHITE), "background": C('#2A1250')}}]
    c['singleVisual']['vcObjects'] = {"background": [{"properties": {"show": B(True), "color": C('#2A1250'), "transparency": D(0)}}]}
edit(sl, style_slicer); new.append(sl)
BM_CLEAN_OVER = 'Bookmark' + newid()
a, b = zt(); new.append(button(1036, 2, 88, 44, a, b, ('bookmark', BM_CLEAN_OVER), 'Limpar', 11, WHITE, base=PINK, base_t=0,
                               hover=(PINK_D, 0), press=(WHITE, 60), rnd=12, parent=G_FILTRO, bold=True, alt='Limpar filtro de período'))
kpis = [' Sales', 'Profit', 'Units Sold', 'Discounts', 'COGS']
cw = (CW - 4 * 12) / 5
for i, c in enumerate(kpis):
    x = i * (cw + 12)
    a, b = zt(); new.append(shape(x, 60, cw, 96, a, b, PANEL, PANEL_T, 14, parent=G_FILTRO))
    a, b = zt(); new.append(card(x + 8, 66, cw - 16, 84, a, b, c, G_FILTRO))

# --- time group (area)
GT_W, GT_H = 694, 250
gt = group(G_TEMPO, 'Perspectiva temporal das vendas', CX, 192, GT_W, GT_H, 2000, 2000); new.append(gt)
a, b = 2010, 2010; new.append(shape(0, 0, GT_W, GT_H, a, b, PANEL, PANEL_T, 14, parent=G_TEMPO))
new.append(textbox(16, 10, 400, 28, 2020, 2020, 'Vendas por Período', 14, True, WHITE, 'left', G_TEMPO))
ar = g('525d8f28a5f711cc3f1f'); set_pos(ar, 8, 40, GT_W - 16, GT_H - 48, 2030, 2030); set_parent(ar, G_TEMPO)
def style_area(c):
    o = c['singleVisual']['objects']
    o['dataPoint'] = [{"properties": {"fill": C(PINK)}}]
    o['valueAxis'] = [{"properties": {"labelColor": C(WHITE), "gridlineColor": C('#6A4A9A'), "showAxisTitle": B(False)}}]
    o['categoryAxis'] = [{"properties": {"labelColor": C(WHITE), "showAxisTitle": B(False)}}]
    c['singleVisual']['vcObjects']['title'] = [{"properties": {"show": B(False)}}]
edit(ar, style_area); new.append(ar)

# --- segment group (donut/bar toggle)
GS_X, GS_W = CX + GT_W + 14, CW - GT_W - 14
gs = group(G_SEG, 'Sales x Segmento', GS_X, 192, GS_W, GT_H, 3000, 3000); new.append(gs)
new.append(shape(0, 0, GS_W, GT_H, 3010, 3010, PANEL, PANEL_T, 14, parent=G_SEG))
new.append(textbox(16, 10, 230, 28, 3020, 3020, 'Vendas por Segmento', 14, True, WHITE, 'left', G_SEG))
def seg_points(prop='fill'):
    pts = []
    for sname, hx in SEG.items():
        pts.append({"properties": {prop: C(hx)}, "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0,
                    "Left": colE('Segment'), "Right": {"Literal": {"Value": "'%s'" % sname}}}}}]}})
    return pts
bar = g('832c7ce5c30a04562a4e'); set_pos(bar, 8, 40, GS_W - 16, GT_H - 48, 3030, 3030); set_parent(bar, G_SEG)
def style_bar(c):
    o = c['singleVisual']['objects']
    o['dataPoint'] = [{"properties": {"showAllDataPoints": B(True)}}] + seg_points()
    c['singleVisual']['vcObjects']['title'] = [{"properties": {"show": B(False)}}]
edit(bar, style_bar); new.append(bar)
don = g('b19b1b2f76ae3ba75142'); set_pos(don, 8, 40, GS_W - 16, GT_H - 48, 3040, 3040); set_parent(don, G_SEG)
def style_don(c):
    o = c['singleVisual']['objects']
    o['dataPoint'] = seg_points()
    o['legend'] = [{"properties": {"show": B(True), "position": S('Bottom'), "labelColor": C(WHITE), "fontSize": D(10), "showTitle": B(False)}}]
    c['singleVisual']['vcObjects']['title'] = [{"properties": {"show": B(False)}}]
edit(don, style_don); new.append(don)
b1 = g('50d18f70ad6156345333'); b2 = g('bb416660b75fce88fa6a')
def tgl(cont, label, x, z):
    set_pos(cont, x, 10, 70, 26, z, z); set_parent(cont, G_SEG)
    def f(c):
        sv = c['singleVisual']
        o = sv['objects']
        o['text'] = [{"properties": {"show": B(True)}}, {"properties": {"text": S(label), "fontSize": D(10), "fontColor": C(WHITE)}, "selector": {"id": "default"}}]
        o['fill'] = [{"properties": {"show": B(True), "fillColor": C(WHITE), "transparency": D(86)}, "selector": {"id": "default"}},
                     {"properties": {"show": B(True), "fillColor": C(PINK), "transparency": D(0)}, "selector": {"id": "hover"}},
                     {"properties": {"show": B(True), "fillColor": C(PINK_D), "transparency": D(0)}, "selector": {"id": "pressed"}}]
        o['outline'] = [{"properties": {"show": B(False)}}]
        o['shape'] = [{"properties": {"roundEdge": N(12)}, "selector": {"id": "default"}}]
        o['icon'] = [{"properties": {"shapeType": S('blank')}, "selector": {"id": "default"}}, {"properties": {"show": B(False)}}]
        sv['vcObjects']['general'] = [{"properties": {"altText": S('Alternar para ' + label)}}]
    edit(cont, f)
tgl(b1, 'Barras', GS_W - 156, 3050); tgl(b2, 'Pizza', GS_W - 78, 3060)
new += [b1, b2]

# --- product bar (absolute)
R3 = 454; R3H = 246
new.append(shape(CX, R3, GT_W, R3H, 4000, 4000, PANEL, PANEL_T, 14))
new.append(textbox(CX + 16, R3 + 10, 400, 28, 4010, 4010, 'Vendas por Produto', 14, True, WHITE, 'left'))
pb = g('d94e32c9b2032b3e7ea8'); set_pos(pb, CX + 8, R3 + 40, GT_W - 16, R3H - 48, 4020, 4020)
def style_pb(c):
    o = c['singleVisual']['objects']
    o['dataPoint'] = [{"properties": {"fill": C(PINK)}}]
    o['valueAxis'] = [{"properties": {"show": B(False), "labelColor": C(WHITE), "showAxisTitle": B(False)}}]
    o['categoryAxis'] = [{"properties": {"labelColor": C(WHITE), "showAxisTitle": B(False)}}]
    c['singleVisual']['vcObjects']['title'] = [{"properties": {"show": B(False)}}]
edit(pb, style_pb); new.append(pb)

# --- country group (treemap/map toggle)
gp = group(G_PAIS, 'Sales x país', GS_X, R3, GS_W, R3H, 5000, 5000); new.append(gp)
new.append(shape(0, 0, GS_W, R3H, 5010, 5010, PANEL, PANEL_T, 14, parent=G_PAIS))
new.append(textbox(16, 10, 230, 28, 5020, 5020, 'Vendas por País', 14, True, WHITE, 'left', G_PAIS))
mp = g('5a79c9a2a4e654b6c313'); set_pos(mp, 8, 40, GS_W - 16, R3H - 48, 5030, 5030); set_parent(mp, G_PAIS); new.append(mp)
tm = g('e5c9ba3eca9235c4fe2a'); set_pos(tm, 8, 40, GS_W - 16, R3H - 48, 5040, 5040); set_parent(tm, G_PAIS)
def style_tm(c):
    o = c['singleVisual']['objects']
    o['dataPoint'] = [{"properties": {"fillRule": {"linearGradient2": {
        "min": {"color": {"expr": {"Literal": {"Value": "'#7B5BE0'"}}}}, "max": {"color": {"expr": {"Literal": {"Value": "'#F06BA0'"}}}},
        "nullColoringStrategy": {"strategy": {"expr": {"Literal": {"Value": "'asZero'"}}}}}}}}]
    o['categoryLabels'] = [{"properties": {"show": B(True), "color": C(WHITE), "fontSize": D(10)}}]
edit(tm, style_tm); new.append(tm)
c1 = g('c37342250f8692fb4fc1'); c2 = g('fb7b0246ff2289ef7707')
def tgl2(cont, label, x, z):
    set_pos(cont, x, 10, 70, 26, z, z); set_parent(cont, G_PAIS)
    def f(c):
        sv = c['singleVisual']; o = sv['objects']
        o['text'] = [{"properties": {"show": B(True)}}, {"properties": {"text": S(label), "fontSize": D(10), "fontColor": C(WHITE)}, "selector": {"id": "default"}}]
        o['fill'] = [{"properties": {"show": B(True), "fillColor": C(WHITE), "transparency": D(86)}, "selector": {"id": "default"}},
                     {"properties": {"show": B(True), "fillColor": C(PINK), "transparency": D(0)}, "selector": {"id": "hover"}},
                     {"properties": {"show": B(True), "fillColor": C(PINK_D), "transparency": D(0)}, "selector": {"id": "pressed"}}]
        o['outline'] = [{"properties": {"show": B(False)}}]
        o['shape'] = [{"properties": {"roundEdge": N(12)}, "selector": {"id": "default"}}]
        o['icon'] = [{"properties": {"shapeType": S('blank')}, "selector": {"id": "default"}}, {"properties": {"show": B(False)}}]
        sv['vcObjects']['general'] = [{"properties": {"altText": S('Alternar para ' + label)}}]
    edit(cont, f)
tgl2(c2, 'Treemap', GS_W - 156, 5050); tgl2(c1, 'Mapa', GS_W - 78, 5060)
new += [c1, c2]

new += sidebar(PG_OVER, 20000, 20000)
ov['visualContainers'] = new
ov['displayName'] = 'Visão Geral'

# =====================================================================
# PAGE 3: DETALHAMENTO (id reused: original file already pointed here)
# =====================================================================
d = []
bg3 = g('5cca43fb4a592e1ed969'); set_pos(bg3, 0, 0, 1280, 720, 0, 0)
edit(bg3, lambda c: c.__setitem__('name', newid())); d.append(bg3)
d.append(textbox(CX, 24, 460, 48, 1000, 1000, 'Detalhamento de Vendas', 26, True, WHITE, 'left'))
d.append(textbox(CX + 462, 34, 76, 28, 1010, 1010, 'Segmento', 12, False, SOFT, 'right'))
s_seg = slicer(CX + 546, 26, 200, 44, 1020, 1020, 'Segment'); d.append(s_seg)
d.append(textbox(CX + 758, 34, 40, 28, 1030, 1030, 'Ano', 12, False, SOFT, 'right'))
s_year = slicer(CX + 802, 26, 222, 44, 1040, 1040, 'Year'); d.append(s_year)
BM_CLEAN_DET = 'Bookmark' + newid()
d.append(button(CX + 1036, 26, 88, 44, 1050, 1050, ('bookmark', BM_CLEAN_DET), 'Limpar', 11, WHITE, base=PINK, base_t=0,
                hover=(PINK_D, 0), press=(WHITE, 60), rnd=12, bold=True, alt='Limpar filtros de segmento e ano'))
MY = 84; MH = 616
MW = GT_W
d.append(shape(CX, MY, MW, MH, 1100, 1100, PANEL, PANEL_T, 14))
d.append(textbox(CX + 16, MY + 10, 500, 28, 1110, 1110, 'Descrição de Vendas e Lucro', 14, True, WHITE, 'left'))
d.append(matrix(CX + 8, MY + 42, MW - 16, MH - 50, 1120, 1120))
half = (MH - 14) / 2
d.append(shape(GS_X, MY, GS_W, half, 1200, 1200, PANEL, PANEL_T, 14))
d.append(textbox(GS_X + 16, MY + 10, 300, 28, 1210, 1210, 'Lucro por Produto', 14, True, WHITE, 'left'))
d.append(chart('clusteredBarChart', GS_X + 8, MY + 40, GS_W - 16, half - 48, 1220, 1220, 'Product', 'Profit', '#F5C518'))
y2 = MY + half + 14
d.append(shape(GS_X, y2, GS_W, half, 1300, 1300, PANEL, PANEL_T, 14))
d.append(textbox(GS_X + 16, y2 + 10, 300, 28, 1310, 1310, 'Vendas por Semestre', 14, True, WHITE, 'left'))
d.append(chart('clusteredColumnChart', GS_X + 8, y2 + 40, GS_W - 16, half - 48, 1320, 1320, 'Semestres', ' Sales', '#8F7CF0'))
d += sidebar(PG_DET, 20000, 20000)

sec3 = {"name": PG_DET, "displayName": "Detalhamento", "filters": "[]", "ordinal": 2, "config": "{}", "displayOption": 1,
        "width": 1280, "height": 720, "visualContainers": d}
j['sections'].append(sec3)
j['sections'][0]['ordinal'] = 0; ov['ordinal'] = 1

# =====================================================================
# BOOKMARKS
# =====================================================================
def clear_bm(name, display, page, slicer_names):
    vcs = {n: {"singleVisual": {"visualType": "slicer", "objects": {}}} for n in slicer_names}
    return {"displayName": display, "name": name,
            "explorationState": {"version": "1.3", "activeSection": page, "sections": {page: {"visualContainers": vcs}},
                                 "objects": {"merge": {"outspacePane": [{"properties": {"expanded": {"expr": {"Literal": {"Value": "false"}}}}}]}}},
            "options": {"targetVisualNames": slicer_names, "suppressActiveSection": True, "suppressDisplay": True}}
bms = [b for b in cfg['bookmarks'] if b['displayName'] not in ('Distribuição por semestre', 'Distribuição por meses', 'Clean data', 'Home page')]
bms.append(clear_bm(BM_CLEAN_OVER, 'Limpar período - Visão Geral', PG_OVER, ['ae85209b2ee41bd6e209']))
sn = lambda cont: json.loads(cont['config'])['name']
bms.append(clear_bm(BM_CLEAN_DET, 'Limpar filtros - Detalhamento', PG_DET, [sn(s_seg), sn(s_year)]))
cfg['bookmarks'] = bms
cfg['activeSectionIndex'] = 0
j['config'] = dumps(cfg)

# resource packages
for rp in j['resourcePackages']:
    if rp['resourcePackage']['name'] == 'RegisteredResources':
        for k in RES.values():
            rp['resourcePackage']['items'].append({"type": 100, "path": k, "name": k})

# ---------- write layout + package ----------
os.makedirs('/home/claude/out', exist_ok=True)
layout = json.dumps(j, separators=(',', ':')).encode('utf-16-le')
zin = zipfile.ZipFile(ORIG)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename == 'SecurityBindings': continue
    if info.filename == 'Report/Layout': data = layout
    if info.filename == '[Content_Types].xml':
        data = re.sub(rb'<Override PartName="/SecurityBindings"[^>]*/>', b'', data)
    zout.writestr(info.filename, data, compress_type=info.compress_type)
for key, fn in [('home', 'icon_home'), ('overview', 'icon_overview'), ('detail', 'icon_detail'), ('logo', 'logo_dio')]:
    zout.writestr('Report/StaticResources/RegisteredResources/' + RES[key], open(f'/home/claude/build/assets/{fn}.png', 'rb').read())
zout.close()
print('built', OUT, os.path.getsize(OUT))
