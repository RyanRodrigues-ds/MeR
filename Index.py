"""MeR pegue e monte — rodar com: python -m streamlit run index.py"""
import calendar
from pathlib import Path
from datetime import date, time, timedelta
from html import escape

import streamlit as st
from PIL import Image

import db

st.set_page_config(page_title="MeR pegue e monte", page_icon=Image.open(Path(__file__).with_name("logo.png")), layout="wide")
db.iniciar_banco()

PAGINAS = ["Início", "Agendamentos", "Estoque", "Financeiro"]
DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
BADGE = {"Agendado": "blue", "Concluído": "green", "Cancelado": "gray",
         "Pago total": "green", "Pago parcial": "yellow", "Não pago": "gray",
         "Receita": "green", "Despesa": "red", "Pendente": "yellow", "Pago": "green"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap');
:root { --azul:#1B8FE0; --azul-claro:#E6F3FD; --linha:#C2185B; --rosa:#F0357F; --rosa-esc:#D6256B; --verde:#3DBE72; --amarelo:#FFC83D;
        --navy:#1C3A7A; --muted:#6B7AA6; --fundo:#FFF9E6; --borda:#EFE2C2; }
.stApp { background: var(--fundo); }
.stApp, :is(.stApp, [data-testid="stDialog"]) p, :is(.stApp, [data-testid="stDialog"]) label, :is(.stApp, [data-testid="stDialog"]) input, :is(.stApp, [data-testid="stDialog"]) button, :is(.stApp, [data-testid="stDialog"]) textarea,
table.mer { font-family: 'Nunito', 'Segoe UI', sans-serif; color: var(--navy); }
h1, h2, h3, .marca { font-family: 'Fredoka', 'Nunito', 'Segoe UI', sans-serif !important; color: var(--navy); }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"], footer { display: none; }
.block-container { max-width: 1100px; padding-top: 1rem; }

/* topo */
.marca { font-size: 26px; font-weight: 700; }
.marca .m { color: var(--azul); } .marca .p { color: var(--rosa); }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-nav_"] button { background: transparent !important; border: none !important;
    box-shadow: none !important; border-radius: 0 !important; padding: 8px 4px !important;
    border-bottom: 3px solid transparent !important; min-height: 0; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-nav_"] button p { color: var(--muted); font-weight: 700; font-size: 15px; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-nav_"] button:hover p { color: var(--rosa); }
.linha-topo { border-bottom: 2px solid var(--borda); margin: 4px 0 22px; }

/* botões e campos */
:is(.stApp, [data-testid="stDialog"]) button[kind="primary"], :is(.stApp, [data-testid="stDialog"]) button[data-testid="stBaseButton-primary"] {
    background: var(--rosa) !important; border: none !important; }
:is(.stApp, [data-testid="stDialog"]) button[kind="primary"] *, :is(.stApp, [data-testid="stDialog"]) button[data-testid="stBaseButton-primary"] * {
    color: #fff !important; }
:is(.stApp, [data-testid="stDialog"]) button[kind="primary"]:hover, :is(.stApp, [data-testid="stDialog"]) button[data-testid="stBaseButton-primary"]:hover {
    background: var(--rosa-esc) !important; }
:is(.stApp, [data-testid="stDialog"]) button[kind="secondary"], :is(.stApp, [data-testid="stDialog"]) button[data-testid="stBaseButton-secondary"] {
    background: var(--azul-claro); border: 1px solid #BFDDF7; }
:is(.stApp, [data-testid="stDialog"]) button[kind="secondary"]:hover, :is(.stApp, [data-testid="stDialog"]) button[data-testid="stBaseButton-secondary"]:hover {
    background: #D3EAFB; border-color: var(--azul); }
/* campos sempre brancos, com texto preto (ignora o tema escuro do navegador) */
:is(.stApp, [data-testid="stDialog"]) :is([data-testid="stTextInput"], [data-testid="stNumberInput"], [data-testid="stTextArea"],
           [data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"],
           [data-testid="stMultiSelect"]) *:not(label):not([data-testid="stWidgetLabel"]):not([data-testid="stWidgetLabel"] *),
[data-baseweb="popover"], [data-baseweb="popover"] * {
    background-color: #fff !important; color: #111 !important; -webkit-text-fill-color: #111 !important; }
:is(.stApp, [data-testid="stDialog"]) :is([data-testid="stTextInput"], [data-testid="stNumberInput"], [data-testid="stTextArea"],
           [data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"]) [data-baseweb] {
    border-color: #D9CBA3 !important; }
:is(.stApp, [data-testid="stDialog"]) [data-baseweb="input"], :is(.stApp, [data-testid="stDialog"]) [data-baseweb="select"] > div, :is(.stApp, [data-testid="stDialog"]) [data-baseweb="textarea"] {
    border: 1px solid #D9CBA3 !important; border-radius: 8px !important; }
:is(.stApp, [data-testid="stDialog"]) input::placeholder, :is(.stApp, [data-testid="stDialog"]) textarea::placeholder { color: #6B7280 !important;
    -webkit-text-fill-color: #6B7280 !important; opacity: 1; }
:is(.stApp, [data-testid="stDialog"]) :is([data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"]) svg,
[data-baseweb="popover"] svg { fill: #111 !important; }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] [aria-selected="true"] {
    background-color: var(--azul-claro) !important; }
div[role="dialog"] label, div[role="dialog"] p, div[role="dialog"] span,
div[role="dialog"] h1, div[role="dialog"] h2, div[role="dialog"] h3 { color: var(--navy); }
div[role="dialog"]:not([data-baseweb="popover"]):not([data-baseweb="popover"] *) { background: var(--fundo) !important; }

h1 a, h2 a, h3 a, [data-testid="stHeaderActionElements"] { display: none !important; }

/* cartões e tabelas */
h1 { font-size: 28px !important; font-weight: 600 !important; padding: 0 0 .6rem !important; }
.metrica { background: #fff; border: 1px solid var(--borda); border-radius: 14px; padding: 14px 18px;
           border-left: 6px solid var(--cor); }
.metrica small { color: var(--muted); font-size: 13px; font-weight: 600; }
.metrica div { font-size: 26px; font-weight: 800; color: var(--navy); }
.metrica span { color: var(--muted); font-size: 12px; }
.proximo { background: #fff; border: 1px solid var(--borda); border-left: 6px solid var(--azul);
           border-radius: 12px; padding: 12px 14px; height: 100%; }
.proximo .quando { display: flex; justify-content: space-between; font-weight: 800; font-size: 13px;
                   color: var(--rosa); }
.proximo .nome { margin-top: 8px; font-weight: 700; }
.proximo .sub { color: var(--muted); font-size: 13px; }
.tabela-wrap { background: #fff; border: 1px solid var(--borda); border-radius: 14px; overflow-x: auto; }
table.mer { width: 100%; border-collapse: collapse; font-size: 14px; }
table.mer th { text-align: left; color: var(--muted); font-weight: 700; font-size: 13px;
               padding: 12px 14px; border-bottom: 2px solid var(--borda); white-space: nowrap;
               background: #FFFDF5; }
table.mer td { padding: 12px 14px; border-bottom: 1px solid #F6EEDA; vertical-align: middle; }
table.mer tr:last-child td { border-bottom: none; }
table.mer .sub { color: var(--muted); font-size: 12px; }
table.mer .num { text-align: right; white-space: nowrap; }
.badge { display: inline-block; color: #fff; font-size: 12px; font-weight: 700;
         padding: 3px 10px; border-radius: 20px; white-space: nowrap; }
.b-green { background: var(--verde); } .b-blue { background: var(--azul); } .b-red { background: var(--rosa); }
.b-yellow { background: var(--amarelo); color: #4a3600; } .b-gray { background: #9AA5C4; }
.qtd { display: inline-block; min-width: 44px; text-align: center; color: #fff; font-weight: 700;
       border-radius: 20px; padding: 3px 10px; background: var(--verde); }
.qtd.zero { background: var(--amarelo); color: #4a3600; }
.vazio { background: #fff; border: 2px dashed var(--borda); border-radius: 14px; padding: 28px;
         text-align: center; color: var(--muted); }
.stButton > button, .stFormSubmitButton > button { border-radius: 10px; font-weight: 700; }

/* calendário próprio (botões) e navegação de mês */
.mes-titulo { font-family: 'Fredoka', 'Nunito', sans-serif; font-weight: 600; font-size: 18px;
              text-align: center; color: #1C3A7A; }
.cal-cab { text-align: center; color: #6B7AA6; font-weight: 700; font-size: 12px; }
.cal-data { font-weight: 700; margin-bottom: 2px; color: #1C3A7A; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button {
    min-height: 34px; height: 34px; width: 100%; padding: 0; border-radius: 50%;
    background: transparent !important; border: none !important; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button p {
    color: #111 !important; font-size: 13px; font-weight: 600; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button:hover { background: #F1F1F1 !important; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button[kind="primary"],
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button[data-testid="stBaseButton-primary"] {
    background: #F0357F !important; }
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button[kind="primary"] p,
:is(.stApp, [data-testid="stDialog"]) div[class*="st-key-cal_"] button[data-testid="stBaseButton-primary"] p {
    color: #fff !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def br_data(iso):
    return date.fromisoformat(iso).strftime("%d/%m/%Y")


def badge(texto):
    return f'<span class="badge b-{BADGE.get(texto, "gray")}">{escape(texto)}</span>'


def tabela(colunas, linhas, vazio):
    if not linhas:
        st.markdown(f'<div class="vazio">{vazio}</div>', unsafe_allow_html=True)
        return
    cab = "".join(f'<th class="{c[1]}">{c[0]}</th>' if isinstance(c, tuple) else f"<th>{c}</th>"
                  for c in colunas)
    corpo = "".join("<tr>" + "".join(f"<td{' class=num' if i in NUM else ''}>{v}</td>"
                    for i, v in enumerate(l)) + "</tr>" for l in linhas)
    st.markdown(f'<div class="tabela-wrap"><table class="mer"><tr>{cab}</tr>{corpo}</table></div>',
                unsafe_allow_html=True)


NUM = set()  # índices de colunas numéricas (alinhadas à direita), definido antes de cada tabela


def ir_para(pagina):
    st.session_state["pagina"] = pagina


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def _mover_mes(chave, delta):
    m = st.session_state[chave]
    total = m.year * 12 + m.month - 1 + delta
    st.session_state[chave] = date(total // 12, total % 12 + 1, 1)


def _escolher_dia(chave, dia):
    st.session_state[f"{chave}_sel"] = dia


def seletor_mes(chave):
    """Navegação por mês: ‹ novembro de 2026 ›. Retorna (primeiro dia, último dia)."""
    m = st.session_state.setdefault(chave, date.today().replace(day=1))
    a, b, c, _ = st.columns([0.7, 2.6, 0.7, 4], vertical_alignment="center")
    a.button("‹", key=f"{chave}_ant", on_click=_mover_mes, args=(chave, -1), use_container_width=True)
    b.markdown(f'<div class="mes-titulo">{MESES[m.month - 1].capitalize()} de {m.year}</div>',
               unsafe_allow_html=True)
    c.button("›", key=f"{chave}_prox", on_click=_mover_mes, args=(chave, 1), use_container_width=True)
    return m, m.replace(day=calendar.monthrange(m.year, m.month)[1])


def seletor_dia(chave):
    """Calendário de botões (sem popover). Retorna a data escolhida."""
    sel = st.session_state.setdefault(f"{chave}_sel", date.today())
    mes_key = f"{chave}_mes"
    mes = st.session_state.setdefault(mes_key, sel.replace(day=1))
    st.markdown(f'<div class="cal-data">Data: {sel:%d/%m/%Y}</div>', unsafe_allow_html=True)
    with st.container(key=f"cal_{chave}"):
        a, b, c = st.columns([1, 3, 1], vertical_alignment="center")
        a.button("‹", key=f"{chave}_ant", on_click=_mover_mes, args=(mes_key, -1))
        b.markdown(f'<div class="mes-titulo">{MESES[mes.month - 1].capitalize()} {mes.year}</div>',
                   unsafe_allow_html=True)
        c.button("›", key=f"{chave}_prox", on_click=_mover_mes, args=(mes_key, 1))
        for col, letra in zip(st.columns(7), "DSTQQSS"):
            col.markdown(f'<div class="cal-cab">{letra}</div>', unsafe_allow_html=True)
        for semana in calendar.Calendar(firstweekday=6).monthdayscalendar(mes.year, mes.month):
            for col, dia in zip(st.columns(7), semana):
                if dia:
                    d = date(mes.year, mes.month, dia)
                    col.button(str(dia), key=f"{chave}_{d.isoformat()}", on_click=_escolher_dia,
                               args=(chave, d), type="primary" if d == sel else "secondary")
    return sel


def abrir(chave, dialogo):
    """Abre uma janela com o calendário começando no dia de hoje."""
    st.session_state.pop(f"{chave}_sel", None)
    st.session_state.pop(f"{chave}_mes", None)
    dialogo()


def aviso_pendente():
    if "msg" in st.session_state:
        tipo, texto = st.session_state.pop("msg")
        (st.success if tipo == "ok" else st.error)(texto)


# ---------------------------------------------------------------- diálogos
@st.dialog("Novo agendamento", width="large")
def dialogo_evento():
    itens = db.listar_itens()
    if not itens:
        st.warning("Cadastre os itens no Estoque antes de agendar.")
        return
    esq, dir_ = st.columns(2)
    with esq:
        cliente = st.text_input("Cliente")
        h_ini = st.time_input("Entrega e montagem", value=time(8, 0))
        h_fim = st.time_input("Retirada", value=time(18, 0))
        valor = st.number_input("Valor cobrado (R$)", min_value=0.0, step=10.0)
    with dir_:
        data = seletor_dia("ev")
    endereco = st.text_input("Endereço do evento")
    obs = st.text_input("Observações")

    st.markdown("**Itens** (o número ao lado do nome é o que está livre nesse horário)")
    ds, i_s, f_s = data.isoformat(), h_ini.strftime("%H:%M"), h_fim.strftime("%H:%M")
    pedidos, cols = {}, st.columns(3)
    for n, item in enumerate(itens):
        livre = max(db.disponivel(item["id"], ds, i_s, f_s), 0)
        q = cols[n % 3].number_input(f"{item['nome']} ({livre} livres)", min_value=0, step=1,
                                     key=f"q_{item['id']}")
        if q:
            pedidos[item["id"]] = int(q)

    forcar = st.checkbox("Agendar mesmo com conflito de horário")
    if st.button("Agendar", type="primary"):
        if not cliente.strip():
            st.error("Informe o nome do cliente.")
            return
        ok, msgs = db.agendar_evento(cliente, ds, i_s, f_s, endereco, valor, pedidos, obs, forcar)
        if ok:
            st.session_state["msg"] = ("ok", "Evento agendado.")
            st.rerun()
        st.error("\n\n".join(msgs))


@st.dialog("Adicionar item")
def dialogo_item():
    nome = st.text_input("Nome")
    cat = st.text_input("Categoria")
    a, b = st.columns(2)
    qtd = a.number_input("Quantidade", min_value=0, step=1)
    val = b.number_input("Valor da locação (R$)", min_value=0.0, step=1.0)
    if st.button("Salvar item", type="primary"):
        if not nome.strip():
            st.error("Informe o nome do item.")
            return
        try:
            db.adicionar_item(nome, cat, qtd, val)
        except Exception:
            st.error("Já existe um item com esse nome.")
            return
        st.session_state["msg"] = ("ok", "Item salvo.")
        st.rerun()


@st.dialog("Nova despesa")
def dialogo_despesa():
    esq, dir_ = st.columns(2)
    with esq:
        desc = st.text_input("Descrição")
        cat = st.text_input("Categoria", value="Combustível")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=5.0)
        pago = st.checkbox("Já foi paga", value=True)
    with dir_:
        data = seletor_dia("desp")
    if st.button("Salvar despesa", type="primary"):
        if not desc.strip() or valor <= 0:
            st.error("Informe a descrição e um valor maior que zero.")
            return
        db.adicionar_despesa(data.isoformat(), cat, desc, valor, pago)
        st.session_state["msg"] = ("ok", "Despesa salva.")
        st.rerun()


# ---------------------------------------------------------------- topo
st.session_state.setdefault("pagina", "Início")
CHAVES = {"Início": "inicio", "Agendamentos": "agendamentos", "Estoque": "estoque",
          "Financeiro": "financeiro"}
ativa = CHAVES[st.session_state["pagina"]]
st.markdown(f"<style>.stApp div[class*='st-key-nav_'].st-key-nav_{ativa} button "
            "{ border-bottom: 4px solid #C2185B !important; }"
            f".stApp div[class*='st-key-nav_'].st-key-nav_{ativa} button p "
            "{ color: #1C3A7A !important; font-weight: 800 !important; }"
            "</style>", unsafe_allow_html=True)
cols_topo = st.columns([3.2, 1, 1.5, 1, 1.3], vertical_alignment="center")
cols_topo[0].markdown('<div class="marca"><span><span class="m">MeR</span> '
                      '<span class="p">pegue e monte</span></span></div>', unsafe_allow_html=True)
for col, nome in zip(cols_topo[1:], PAGINAS):
    col.button(nome, key=f"nav_{CHAVES[nome]}", on_click=ir_para, args=(nome,),
               use_container_width=True)
st.markdown('<div class="linha-topo"></div>', unsafe_allow_html=True)
pagina = st.session_state["pagina"]
hoje = date.today()
aviso_pendente()

# ---------------------------------------------------------------- Início
if pagina == "Início":
    st.title("Início")
    a, b, _ = st.columns([1, 1, 3])
    if a.button("Novo agendamento", type="primary", use_container_width=True):
        abrir("ev", dialogo_evento)
    b.button("Ver estoque", use_container_width=True, on_click=ir_para, args=("Estoque",))

    st.subheader("Próximos agendamentos")
    prox = [e for e in db.eventos_no_periodo(hoje.isoformat(), (hoje + timedelta(days=60)).isoformat())
            if e["status"] == "Agendado"][:4]
    if not prox:
        st.markdown('<div class="vazio">Nenhum evento agendado. Use "Novo agendamento" para começar.</div>',
                    unsafe_allow_html=True)
    cols = st.columns(4)
    for col, e in zip(cols, prox):
        d = date.fromisoformat(e["data"])
        quando = "Hoje" if d == hoje else ("Amanhã" if d == hoje + timedelta(days=1)
                                           else f"{DIAS[d.weekday()]} {d:%d/%m}")
        col.markdown(
            f'<div class="proximo"><div class="quando"><span>{quando}</span><span>{e["hora_inicio"]}</span></div>'
            f'<div class="nome">{escape(e["cliente"])}</div>'
            f'<div class="sub">{escape(e["endereco"] or "Sem endereço")}</div></div>',
            unsafe_allow_html=True)

    ini, fim = db.semana_de(hoje)
    na_semana = [e for e in db.eventos_no_periodo(ini.isoformat(), fim.isoformat())
                 if e["status"] == "Agendado"]
    st.markdown(f'<br><div class="metrica" style="--cor:#1B8FE0"><small>Eventos nesta semana</small>'
                f'<div>{len(na_semana)}</div><span>{ini:%d/%m} a {fim:%d/%m}</span></div>',
                unsafe_allow_html=True)

# ---------------------------------------------------------------- Agendamentos
elif pagina == "Agendamentos":
    st.title("Agendamentos")
    if st.button("Novo agendamento", type="primary"):
        abrir("ev", dialogo_evento)

    f1, f2 = st.columns([3, 1])
    with f1:
        ini, fim = seletor_mes("mes_ag")
    filtro = f2.selectbox("Status", ["Todos"] + db.STATUS_EVENTO)
    eventos = [e for e in db.eventos_no_periodo(ini.isoformat(), fim.isoformat())
               if filtro == "Todos" or e["status"] == filtro]

    NUM = {6, 7}
    linhas = []
    for e in eventos:
        d = date.fromisoformat(e["data"])
        itens_txt = ", ".join(f"{i['quantidade']}× {escape(i['nome'])}" for i in e["itens"])
        linhas.append([
            e["id"], badge(e["status"]), f"{DIAS[d.weekday()]} {d:%d/%m/%Y}",
            f"{e['hora_inicio']}–{e['hora_fim']}",
            f"<b>{escape(e['cliente'])}</b><div class='sub'>{escape(e['endereco'] or '')}</div>",
            itens_txt, brl(e["valor_cobrado"]), brl(e["valor_recebido"]),
            badge(db.status_pagamento(e["valor_cobrado"], e["valor_recebido"]))])
    tabela(["ID", "Status", "Data", "Horário", "Cliente", "Itens",
            ("Valor", "num"), ("Recebido", "num"), "Pagamento"], linhas,
           "Nenhum agendamento neste período.")

    if eventos:
        with st.expander("Editar agendamento"):
            ev = st.selectbox("Agendamento", eventos,
                              format_func=lambda e: f"#{e['id']} · {e['cliente']} · {br_data(e['data'])}")
            c1, c2 = st.columns(2)
            novo_status = c1.selectbox("Status", db.STATUS_EVENTO,
                                       index=db.STATUS_EVENTO.index(ev["status"]), key=f"st_{ev['id']}")
            recebido = c2.number_input("Valor recebido (R$)", min_value=0.0, step=10.0,
                                       value=float(ev["valor_recebido"]), key=f"rc_{ev['id']}")
            if st.button("Salvar alterações", type="primary"):
                db.atualizar_evento(ev["id"], novo_status, recebido)
                st.session_state["msg"] = ("ok", "Agendamento atualizado.")
                st.rerun()
            st.caption("Eventos cancelados liberam os itens reservados.")

# ---------------------------------------------------------------- Estoque
elif pagina == "Estoque":
    st.title("Estoque")
    if st.button("Adicionar item", type="primary"):
        dialogo_item()

    itens = db.listar_itens()
    busca = st.text_input("Buscar item", placeholder="Nome ou categoria")
    itens = [i for i in itens if busca.lower() in f"{i['nome']} {i['categoria']}".lower()]
    NUM = {2, 3, 4}
    linhas = []
    for i in itens:
        livre = max(db.disponivel(i["id"], hoje.isoformat(), "00:00", "23:59"), 0)
        linhas.append([escape(i["nome"]), escape(i["categoria"] or ""), i["quantidade_total"],
                       i["quantidade_total"] - livre,
                       f'<span class="qtd{" zero" if livre == 0 else ""}">{livre}</span>',
                       brl(i["valor_locacao"])])
    tabela(["Item", "Categoria", ("Total", "num"), ("Em uso hoje", "num"), ("Livre hoje", "num"),
            "Valor"], linhas, "Nenhum item cadastrado. Use \"Adicionar item\".")

    if itens:
        with st.expander("Ajustar quantidade"):
            esc = st.selectbox("Item", itens, format_func=lambda i: i["nome"])
            nova = st.number_input("Quantidade total", min_value=0, step=1,
                                   value=esc["quantidade_total"], key=f"nova_{esc['id']}")
            if st.button("Atualizar quantidade", type="primary"):
                db.atualizar_quantidade(esc["id"], nova)
                st.session_state["msg"] = ("ok", "Quantidade atualizada.")
                st.rerun()

# ---------------------------------------------------------------- Financeiro
else:
    st.title("Financeiro")
    if st.button("Nova despesa", type="primary"):
        abrir("desp", dialogo_despesa)

    ini, fim = seletor_mes("mes_fin")
    r = db.resumo_financeiro(ini.isoformat(), fim.isoformat())

    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metrica" style="--cor:#3DBE72"><small>Receitas</small>'
                f'<div>{brl(r["receitas"])}</div><span>&nbsp;</span></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metrica" style="--cor:#F0357F"><small>Despesas</small>'
                f'<div>{brl(r["despesas"])}</div><span>{brl(r["pendente"])} pendente</span></div>',
                unsafe_allow_html=True)
    m3.markdown(f'<div class="metrica" style="--cor:#1B8FE0"><small>Lucro</small>'
                f'<div>{brl(r["lucro"])}</div><span>&nbsp;</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    lanc = db.lancamentos(ini.isoformat(), fim.isoformat())
    NUM = {4}
    tabela(["Tipo", "Data", "Categoria", "Descrição", ("Valor", "num"), "Status"],
           [[badge(l["tipo"]), br_data(l["data"]), escape(l["categoria"] or ""),
             escape(l["descricao"]), brl(l["valor"]), badge("Pago" if l["pago"] else "Pendente")]
            for l in lanc], "Nenhum lançamento neste período.")
    st.caption("As receitas vêm do valor recebido, registrado em Agendamentos.")

    despesas = [l for l in lanc if l["tipo"] == "Despesa"]
    if despesas:
        with st.expander("Excluir despesa"):
            d = st.selectbox("Despesa", despesas,
                             format_func=lambda x: f"{br_data(x['data'])} · {x['descricao']} · {brl(x['valor'])}")
            if st.button("Excluir despesa"):
                db.excluir_despesa(d["id"])
                st.session_state["msg"] = ("ok", "Despesa excluída.")
                st.rerun()