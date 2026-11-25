"""MeR pegue e monte — rodar com: python -m streamlit run index.py"""
import calendar
from pathlib import Path
from datetime import date, time, timedelta
from html import escape

import streamlit as st
from PIL import Image

import db
import logistica

st.set_page_config(page_title="MeR pegue e monte", page_icon=Image.open(Path(__file__).with_name("logo.png")), layout="wide")
db.iniciar_banco()

VERSAO = "25/11/2026 · logística de entrega"
PAGINAS = ["Início", "Agendamentos", "Estoque", "Financeiro", "Configurações"]
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
.stApp, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) p, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) label, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) input, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) textarea,
table.mer { font-family: 'Nunito', 'Segoe UI', sans-serif; color: var(--navy); }
h1, h2, h3, .marca { font-family: 'Fredoka', 'Nunito', 'Segoe UI', sans-serif !important; color: var(--navy); }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"], footer { display: none; }
.block-container { max-width: 1100px; padding-top: 1rem; }

/* topo */
.marca { font-size: 26px; font-weight: 700; }
.marca .m { color: var(--azul); } .marca .p { color: var(--rosa); }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-nav_"] button { background: transparent !important; border: none !important;
    box-shadow: none !important; border-radius: 0 !important; padding: 8px 4px !important;
    border-bottom: 3px solid transparent !important; min-height: 0; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-nav_"] button p { color: var(--muted); font-weight: 700; font-size: 15px; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-nav_"] button:hover p { color: var(--rosa); }
.linha-topo { border-bottom: 2px solid var(--borda); margin: 4px 0 22px; }

/* botões e campos */
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[kind="primary"], :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[data-testid="stBaseButton-primary"] {
    background: var(--rosa) !important; border: none !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[kind="primary"] *, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[data-testid="stBaseButton-primary"] * {
    color: #fff !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[kind="primary"]:hover, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[data-testid="stBaseButton-primary"]:hover {
    background: var(--rosa-esc) !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[kind="secondary"], :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[data-testid="stBaseButton-secondary"] {
    background: var(--azul-claro); border: 1px solid #BFDDF7; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[kind="secondary"]:hover, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) button[data-testid="stBaseButton-secondary"]:hover {
    background: #D3EAFB; border-color: var(--azul); }
/* campos sempre brancos, com texto preto (ignora o tema escuro do navegador) */
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) :is([data-testid="stTextInput"], [data-testid="stNumberInput"], [data-testid="stTextArea"],
           [data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"],
           [data-testid="stMultiSelect"]) *:not(label):not([data-testid="stWidgetLabel"]):not([data-testid="stWidgetLabel"] *),
[data-baseweb="popover"], [data-baseweb="popover"] * {
    background-color: #fff !important; color: #111 !important; -webkit-text-fill-color: #111 !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) :is([data-testid="stTextInput"], [data-testid="stNumberInput"], [data-testid="stTextArea"],
           [data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"]) [data-baseweb] {
    border-color: #D9CBA3 !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) [data-baseweb="input"], :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) [data-baseweb="select"] > div, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) [data-baseweb="textarea"] {
    border: 1px solid #D9CBA3 !important; border-radius: 8px !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) input::placeholder, :is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) textarea::placeholder { color: #6B7280 !important;
    -webkit-text-fill-color: #6B7280 !important; opacity: 1; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) :is([data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTimeInput"]) svg,
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
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button {
    min-height: 34px; height: 34px; width: 100%; padding: 0; border-radius: 50%;
    background: transparent !important; border: none !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button p {
    color: #111 !important; font-size: 13px; font-weight: 600; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button:hover { background: #F1F1F1 !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button[kind="primary"],
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button[data-testid="stBaseButton-primary"] {
    background: #F0357F !important; }
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button[kind="primary"] p,
:is(.stApp, [data-testid="stDialog"], [data-testid="stPopoverBody"]) div[class*="st-key-cal_"] button[data-testid="stBaseButton-primary"] p {
    color: #fff !important; }

.rotulo-campo { font-size: 14px; color: #1C3A7A; margin-bottom: 4px; }
[data-testid="stPopoverButton"] { background: #fff !important; border: 1px solid #D9CBA3 !important;
    border-radius: 8px !important; justify-content: flex-start; min-width: 230px; }
[data-testid="stPopoverButton"] * { color: #111 !important; }
[data-testid="stPopoverBody"], [data-testid="stPopoverBody"] > div { background: #fff !important;
    min-width: 330px; border-radius: 14px; }
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] label { color: #1C3A7A; }

/* janelas (modais): fundo creme em todas as camadas, texto azul-marinho */
div[role="dialog"]:not([data-baseweb="popover"]):not([data-baseweb="popover"] *),
div[role="dialog"]:not([data-baseweb="popover"]):not([data-baseweb="popover"] *) > div,
div[role="dialog"]:not([data-baseweb="popover"]):not([data-baseweb="popover"] *) > div > div,
div[role="dialog"]:not([data-baseweb="popover"]):not([data-baseweb="popover"] *) > div > div > div {
    background-color: #FFF9E6 !important; }
div[role="dialog"]:not([data-baseweb="popover"]) h1, div[role="dialog"]:not([data-baseweb="popover"]) h2,
div[role="dialog"]:not([data-baseweb="popover"]) h3, div[role="dialog"]:not([data-baseweb="popover"]) label,
div[role="dialog"]:not([data-baseweb="popover"]) p { color: #1C3A7A !important; }
div[role="dialog"]:not([data-baseweb="popover"]) button[aria-label="Close"] svg { fill: #1C3A7A !important; }

/* campos: cantos internos não aparecem por cima do arredondado */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] { overflow: hidden; }

/* avisos (sucesso, erro, atenção) */
[data-testid="stAlert"], [data-testid="stAlert"] > div { background-color: #fff !important;
    border: 1px solid #EFE2C2 !important; border-radius: 10px !important; }
[data-testid="stAlert"] * { color: #1C3A7A !important; }
.mes-titulo { white-space: nowrap; font-size: 16px !important; }

/* formulários abertos na própria página */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border: 1px solid #EFE2C2 !important;
    border-radius: 14px !important; }
.painel-titulo { font-family: 'Fredoka', 'Nunito', sans-serif; font-weight: 600; font-size: 20px; color: #1C3A7A; }
.versao { margin-top: 32px; color: #9AA5C4; font-size: 11px; text-align: right; }
.ent-resumo { background: #FFF9E6; border: 1px solid #EFE2C2; border-radius: 12px;
              padding: 12px 14px; margin: 8px 0; font-size: 14px; line-height: 1.7; }
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
    st.session_state["painel"] = None


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def _mover_mes(chave, delta):
    m = st.session_state[chave]
    total = m.year * 12 + m.month - 1 + delta
    st.session_state[chave] = date(total // 12, total % 12 + 1, 1)


def _escolher_dia(chave, dia):
    st.session_state[f"{chave}_sel"] = dia


def _limpar_dia(chave):
    st.session_state[f"{chave}_sel"] = None


def seletor_dia(chave, opcional=False):
    """Calendário de botões. Com opcional=True é possível ficar sem dia escolhido (mês inteiro)."""
    sel_key, mes_key = f"{chave}_sel", f"{chave}_mes"
    sel = st.session_state.setdefault(sel_key, None if opcional else date.today())
    mes = st.session_state.setdefault(mes_key, (sel or date.today()).replace(day=1))
    texto = f"Dia: {sel:%d/%m/%Y}" if sel else "Mostrando o mês inteiro"
    st.markdown(f'<div class="cal-data">{texto if opcional else f"Data: {sel:%d/%m/%Y}"}</div>',
                unsafe_allow_html=True)
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
    if opcional:
        st.button("Ver o mês inteiro", key=f"{chave}_limpar", on_click=_limpar_dia, args=(chave,),
                  use_container_width=True)
    return sel


def filtro_data(chave):
    """Botão que abre um calendário. Retorna (data inicial, data final) do filtro."""
    sel = st.session_state.get(f"{chave}_sel")
    mes = st.session_state.get(f"{chave}_mes") or date.today().replace(day=1)
    rotulo = f"{sel:%d/%m/%Y}" if sel else f"{MESES[mes.month - 1].capitalize()} de {mes.year}"
    st.markdown('<div class="rotulo-campo">Data</div>', unsafe_allow_html=True)
    with st.popover("📅  " + rotulo):
        seletor_dia(chave, opcional=True)
    if sel:
        return sel, sel
    return mes, mes.replace(day=calendar.monthrange(mes.year, mes.month)[1])


def abrir_painel(nome):
    """Abre o formulário na própria página, com o calendário começando em hoje."""
    st.session_state["painel"] = nome
    st.session_state.pop("ent", None)
    for chave in ("ev", "desp"):
        st.session_state.pop(f"{chave}_sel", None)
        st.session_state.pop(f"{chave}_mes", None)


def fechar_painel():
    st.session_state["painel"] = None


def aviso_pendente():
    if "msg" in st.session_state:
        tipo, texto = st.session_state.pop("msg")
        (st.success if tipo == "ok" else st.error)(texto)


# ---------------------------------------------------------------- diálogos
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
    endereco = st.text_input("Endereço do evento", help="Rua, número, bairro e cidade.")
    if st.button("Calcular distância e combustível", key="calc_ent"):
        try:
            st.session_state["ent"] = logistica.calcular_entrega(endereco, db.todas_config())
        except logistica.ErroLogistica as erro:
            st.session_state["ent"] = {"ok": False, "erro": str(erro)}
    ent = st.session_state.get("ent")
    if ent and not ent["ok"]:
        st.error(ent["erro"])
    elif ent and ent["endereco"] != endereco:
        st.caption("O endereço mudou. Calcule de novo para atualizar a distância.")
        ent = None
    elif ent:
        lucro = valor - ent["custo"]
        cor = "#3DBE72" if lucro >= 0 else "#F0357F"
        st.markdown(
            f'<div class="ent-resumo">📍 {escape(ent["rotulo"])}<br>'
            f'{ent["km_ida"]:.1f} km por trajeto ({ent["minutos_ida"]:.0f} min) · '
            f'{ent["viagens"]} viagem(ns) de ida e volta = {ent["km_total"]:.1f} km · '
            f'{ent["litros"]:.1f} L<br>Combustível: <b>{brl(ent["custo"])}</b> · '
            f'Sobra após combustível: <b style="color:{cor}">{brl(lucro)}</b></div>',
            unsafe_allow_html=True)
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
        calculado = ent if ent and ent.get("ok") and ent["endereco"] == endereco else None
        ok, msgs = db.agendar_evento(
            cliente, ds, i_s, f_s, endereco, valor, pedidos, obs, forcar,
            distancia_km=calculado["km_ida"] if calculado else None,
            custo_combustivel=calculado["custo"] if calculado else None)
        if ok:
            st.session_state["painel"] = None
            st.session_state["msg"] = ("ok", "Evento agendado.")
            st.rerun()
        st.error("\n\n".join(msgs))


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
        st.session_state["painel"] = None
        st.session_state["msg"] = ("ok", "Item salvo.")
        st.rerun()


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
        st.session_state["painel"] = None
        st.session_state["msg"] = ("ok", "Despesa salva.")
        st.rerun()


def mostrar_painel(nome):
    titulos = {"ev": ("Novo agendamento", dialogo_evento), "item": ("Adicionar item", dialogo_item),
               "desp": ("Nova despesa", dialogo_despesa)}
    if st.session_state.get("painel") != nome:
        return
    titulo, formulario = titulos[nome]
    with st.container(border=True):
        c1, c2 = st.columns([6, 1], vertical_alignment="center")
        c1.markdown(f'<div class="painel-titulo">{titulo}</div>', unsafe_allow_html=True)
        c2.button("Fechar", key="fechar_painel", on_click=fechar_painel, use_container_width=True)
        formulario()


# ---------------------------------------------------------------- topo
st.session_state.setdefault("pagina", "Início")
CHAVES = {"Início": "inicio", "Agendamentos": "agendamentos", "Estoque": "estoque",
          "Financeiro": "financeiro", "Configurações": "configuracoes"}
ativa = CHAVES[st.session_state["pagina"]]
st.markdown(f"<style>.stApp div[class*='st-key-nav_'].st-key-nav_{ativa} button "
            "{ border-bottom: 4px solid #C2185B !important; }"
            f".stApp div[class*='st-key-nav_'].st-key-nav_{ativa} button p "
            "{ color: #1C3A7A !important; font-weight: 800 !important; }"
            "</style>", unsafe_allow_html=True)
cols_topo = st.columns([2.6, 1, 1.5, 1, 1.3, 1.6], vertical_alignment="center")
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
    a.button("Novo agendamento", type="primary", use_container_width=True, on_click=abrir_painel, args=("ev",))
    b.button("Ver estoque", use_container_width=True, on_click=ir_para, args=("Estoque",))
    mostrar_painel("ev")

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
    st.button("Novo agendamento", type="primary", on_click=abrir_painel, args=("ev",))
    mostrar_painel("ev")

    f1, f2 = st.columns([3, 1])
    with f1:
        ini, fim = filtro_data("ag")
    filtro = f2.selectbox("Status", ["Todos"] + db.STATUS_EVENTO)
    eventos = [e for e in db.eventos_no_periodo(ini.isoformat(), fim.isoformat())
               if filtro == "Todos" or e["status"] == filtro]

    NUM = {6, 7, 8, 9}
    linhas = []
    for e in eventos:
        d = date.fromisoformat(e["data"])
        itens_txt = ", ".join(f"{i['quantidade']}× {escape(i['nome'])}" for i in e["itens"])
        custo = e.get("custo_combustivel")
        comb_txt = "—" if custo is None else (
            f"{brl(custo)}<div class='sub'>{e['distancia_km']:.1f} km por trajeto</div>")
        lucro_txt = "—" if custo is None else brl(e["valor_cobrado"] - custo)
        linhas.append([
            e["id"], badge(e["status"]), f"{DIAS[d.weekday()]} {d:%d/%m/%Y}",
            f"{e['hora_inicio']}–{e['hora_fim']}",
            f"<b>{escape(e['cliente'])}</b><div class='sub'>{escape(e['endereco'] or '')}</div>",
            itens_txt, brl(e["valor_cobrado"]), comb_txt, lucro_txt, brl(e["valor_recebido"]),
            badge(db.status_pagamento(e["valor_cobrado"], e["valor_recebido"]))])
    tabela(["ID", "Status", "Data", "Horário", "Cliente", "Itens",
            ("Valor", "num"), ("Combustível", "num"), ("Sobra", "num"), ("Recebido", "num"),
            "Pagamento"], linhas,
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
                st.session_state["painel"] = None
                st.session_state["msg"] = ("ok", "Agendamento atualizado.")
                st.rerun()
            st.caption("Eventos cancelados liberam os itens reservados.")

# ---------------------------------------------------------------- Estoque
elif pagina == "Estoque":
    st.title("Estoque")
    st.button("Adicionar item", type="primary", on_click=abrir_painel, args=("item",))
    mostrar_painel("item")

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
                st.session_state["painel"] = None
                st.session_state["msg"] = ("ok", "Quantidade atualizada.")
                st.rerun()

# ---------------------------------------------------------------- Financeiro
elif pagina == "Financeiro":
    st.title("Financeiro")
    st.button("Nova despesa", type="primary", on_click=abrir_painel, args=("desp",))
    mostrar_painel("desp")

    ini, fim = filtro_data("fin")
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
                st.session_state["painel"] = None
                st.session_state["msg"] = ("ok", "Despesa excluída.")
                st.rerun()

# ---------------------------------------------------------------- Configurações
else:
    st.title("Configurações")
    st.caption("Usadas para calcular a distância e o custo de combustível de cada entrega.")
    cfg = db.todas_config()
    with st.container(border=True):
        a, b = st.columns(2)
        base = a.text_input("Endereço da base (de onde saem as entregas)",
                            value=cfg.get("base_endereco", ""), help="Rua, número, bairro e cidade.")
        consumo = b.number_input("Consumo do veículo (km por litro)", min_value=1.0, step=0.5,
                                 value=float(cfg.get("consumo_kml", 10)))
        preco = a.number_input("Preço do litro (R$)", min_value=0.0, step=0.1,
                               value=float(cfg.get("preco_litro", 6.0)))
        viagens = b.number_input("Viagens de ida e volta por evento", min_value=1, max_value=4, step=1,
                                 value=int(float(cfg.get("viagens", 2))),
                                 help="2 = uma viagem para entregar e outra para retirar.")
        chave = st.text_input("Chave do OpenRouteService", type="password",
                              placeholder="Já configurada. Deixe em branco para manter."
                              if cfg.get("ors_chave") else "Cole aqui a chave")
        st.caption("Para obter a chave: crie uma conta gratuita em openrouteservice.org, abra o "
                   "Dashboard e peça um token do tipo Basic.")
        if st.button("Salvar configurações", type="primary"):
            chave_final = chave.strip() or cfg.get("ors_chave", "")
            novos = {"base_endereco": base.strip(), "consumo_kml": consumo, "preco_litro": preco,
                     "viagens": viagens, "ors_chave": chave_final}
            msg = ("ok", "Configurações salvas.")
            if base.strip() and chave_final and (base.strip() != cfg.get("base_endereco")
                                                 or not cfg.get("base_lat") or chave.strip()):
                try:
                    lat, lon, rotulo = logistica.geocodificar(base, chave_final)
                    novos.update({"base_lat": lat, "base_lon": lon, "base_rotulo": rotulo})
                    msg = ("ok", f"Configurações salvas. Base localizada: {rotulo}")
                except logistica.ErroLogistica as erro:
                    novos.update({"base_lat": "", "base_lon": "", "base_rotulo": ""})
                    msg = ("erro", f"Configurações salvas, mas a base não foi localizada: {erro}")
            db.salvar_config(novos)
            st.session_state["msg"] = msg
            st.rerun()

    situacao = []
    situacao.append("Chave: configurada ✓" if cfg.get("ors_chave") else "Chave: ainda não configurada")
    situacao.append(f"Base localizada: {escape(cfg['base_rotulo'])}" if cfg.get("base_rotulo")
                    else "Base: ainda não localizada")
    st.markdown("<br>".join(situacao), unsafe_allow_html=True)

st.markdown(f'<div class="versao">versão: {VERSAO}</div>', unsafe_allow_html=True)