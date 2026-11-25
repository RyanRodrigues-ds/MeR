"""Banco de dados e regras de negócio do sistema MeR pegue e monte.

Regras principais:
- Um item só pode ser reservado se houver quantidade livre naquele intervalo.
- Dois eventos no mesmo dia não podem ter horários sobrepostos (aviso, com opção de forçar).
"""
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("mer.db")


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def iniciar_banco():
    with conectar() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                categoria TEXT,
                quantidade_total INTEGER NOT NULL CHECK (quantidade_total >= 0),
                valor_locacao REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                data TEXT NOT NULL,          -- AAAA-MM-DD
                hora_inicio TEXT NOT NULL,   -- HH:MM (entrega)
                hora_fim TEXT NOT NULL,      -- HH:MM (retirada)
                endereco TEXT,
                valor_cobrado REAL NOT NULL DEFAULT 0,
                observacoes TEXT
            );
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                categoria TEXT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                pago INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS reservas (
                evento_id INTEGER NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
                item_id INTEGER NOT NULL REFERENCES itens(id),
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                PRIMARY KEY (evento_id, item_id)
            );
            """
        )
        colunas = [r["name"] for r in con.execute("PRAGMA table_info(eventos)")]
        if "status" not in colunas:
            con.execute("ALTER TABLE eventos ADD COLUMN status TEXT NOT NULL DEFAULT 'Agendado'")
        if "valor_recebido" not in colunas:
            con.execute("ALTER TABLE eventos ADD COLUMN valor_recebido REAL NOT NULL DEFAULT 0")


# ---------- Itens ----------
def adicionar_item(nome, categoria, quantidade_total, valor_locacao):
    with conectar() as con:
        con.execute(
            "INSERT INTO itens (nome, categoria, quantidade_total, valor_locacao) VALUES (?,?,?,?)",
            (nome.strip(), categoria.strip(), int(quantidade_total), float(valor_locacao)),
        )


def atualizar_quantidade(item_id, quantidade_total):
    with conectar() as con:
        con.execute("UPDATE itens SET quantidade_total=? WHERE id=?", (int(quantidade_total), item_id))


def listar_itens():
    with conectar() as con:
        return [dict(r) for r in con.execute("SELECT * FROM itens ORDER BY categoria, nome")]


# ---------- Verificações ----------
def _sobrepoe(ini_a, fim_a, ini_b, fim_b):
    return ini_a < fim_b and fim_a > ini_b


def disponivel(item_id, data, hora_inicio, hora_fim, ignorar_evento=None):
    """Quantidade livre do item no intervalo (total menos reservas que se sobrepõem)."""
    with conectar() as con:
        total = con.execute(
            "SELECT quantidade_total FROM itens WHERE id=?", (item_id,)
        ).fetchone()["quantidade_total"]
        linhas = con.execute(
            """SELECT e.id, e.hora_inicio, e.hora_fim, r.quantidade
               FROM reservas r JOIN eventos e ON e.id = r.evento_id
               WHERE r.item_id=? AND e.data=? AND e.status != 'Cancelado'""",
            (item_id, data),
        ).fetchall()
    usado = sum(
        l["quantidade"]
        for l in linhas
        if l["id"] != ignorar_evento
        and _sobrepoe(hora_inicio, hora_fim, l["hora_inicio"], l["hora_fim"])
    )
    return total - usado


def conflitos_de_horario(data, hora_inicio, hora_fim, ignorar_evento=None):
    with conectar() as con:
        eventos = con.execute("SELECT * FROM eventos WHERE data=? AND status != 'Cancelado'", (data,)).fetchall()
    return [
        dict(e)
        for e in eventos
        if e["id"] != ignorar_evento
        and _sobrepoe(hora_inicio, hora_fim, e["hora_inicio"], e["hora_fim"])
    ]


def verificar_estoque(itens_pedidos, data, hora_inicio, hora_fim, ignorar_evento=None):
    """itens_pedidos: {item_id: quantidade}. Retorna lista de faltas (vazia = tudo ok)."""
    nomes = {i["id"]: i["nome"] for i in listar_itens()}
    faltas = []
    for item_id, qtd in itens_pedidos.items():
        livre = disponivel(item_id, data, hora_inicio, hora_fim, ignorar_evento)
        if qtd > livre:
            faltas.append(
                f"{nomes[item_id]}: pedido {qtd}, disponível {max(livre, 0)} em {data}"
            )
    return faltas


# ---------- Eventos ----------
def agendar_evento(cliente, data, hora_inicio, hora_fim, endereco, valor_cobrado,
                   itens_pedidos, observacoes="", forcar_horario=False):
    """Tenta agendar. Retorna (ok, mensagens)."""
    if hora_fim <= hora_inicio:
        return False, ["A hora de retirada deve ser depois da hora de entrega."]
    if not itens_pedidos:
        return False, ["Selecione ao menos um item."]

    faltas = verificar_estoque(itens_pedidos, data, hora_inicio, hora_fim)
    if faltas:
        return False, ["Falta de material:"] + faltas

    conflitos = conflitos_de_horario(data, hora_inicio, hora_fim)
    if conflitos and not forcar_horario:
        msgs = ["Conflito de horário com:"]
        msgs += [f"{c['cliente']} ({c['hora_inicio']}–{c['hora_fim']})" for c in conflitos]
        return False, msgs

    with conectar() as con:
        cur = con.execute(
            """INSERT INTO eventos (cliente, data, hora_inicio, hora_fim, endereco,
                                    valor_cobrado, observacoes) VALUES (?,?,?,?,?,?,?)""",
            (cliente.strip(), data, hora_inicio, hora_fim, endereco.strip(),
             float(valor_cobrado), observacoes.strip()),
        )
        for item_id, qtd in itens_pedidos.items():
            con.execute(
                "INSERT INTO reservas (evento_id, item_id, quantidade) VALUES (?,?,?)",
                (cur.lastrowid, item_id, qtd),
            )
    return True, ["Evento agendado."]


def cancelar_evento(evento_id):
    with conectar() as con:
        con.execute("DELETE FROM eventos WHERE id=?", (evento_id,))


def eventos_no_periodo(data_ini, data_fim):
    with conectar() as con:
        eventos = [dict(e) for e in con.execute(
            "SELECT * FROM eventos WHERE data BETWEEN ? AND ? ORDER BY data, hora_inicio",
            (data_ini, data_fim),
        )]
        for e in eventos:
            e["itens"] = [dict(r) for r in con.execute(
                """SELECT i.nome, r.quantidade FROM reservas r
                   JOIN itens i ON i.id = r.item_id WHERE r.evento_id=?""",
                (e["id"],),
            )]
    return eventos


def semana_de(d: date):
    ini = d - timedelta(days=d.weekday())
    return ini, ini + timedelta(days=6)


# ---------- Status, recebimentos e financeiro ----------
STATUS_EVENTO = ["Agendado", "Concluído", "Cancelado"]


def status_pagamento(valor_cobrado, valor_recebido):
    if valor_recebido <= 0:
        return "Não pago"
    return "Pago total" if valor_recebido >= valor_cobrado else "Pago parcial"


def atualizar_evento(evento_id, status, valor_recebido):
    with conectar() as con:
        con.execute("UPDATE eventos SET status=?, valor_recebido=? WHERE id=?",
                    (status, float(valor_recebido), evento_id))


def adicionar_despesa(data, categoria, descricao, valor, pago=True):
    with conectar() as con:
        con.execute("INSERT INTO despesas (data, categoria, descricao, valor, pago) VALUES (?,?,?,?,?)",
                    (data, categoria.strip(), descricao.strip(), float(valor), int(pago)))


def excluir_despesa(despesa_id):
    with conectar() as con:
        con.execute("DELETE FROM despesas WHERE id=?", (despesa_id,))


def lancamentos(data_ini, data_fim):
    """Receitas (valores recebidos dos eventos) e despesas do período, mais recentes primeiro."""
    with conectar() as con:
        rec = [dict(r) for r in con.execute(
            """SELECT id, data, 'Receita' AS tipo, 'Eventos' AS categoria,
                      'Evento de ' || cliente AS descricao, valor_recebido AS valor, 1 AS pago
               FROM eventos WHERE valor_recebido > 0 AND status != 'Cancelado'
                    AND data BETWEEN ? AND ?""", (data_ini, data_fim))]
        desp = [dict(r) for r in con.execute(
            """SELECT id, data, 'Despesa' AS tipo, categoria, descricao, valor, pago
               FROM despesas WHERE data BETWEEN ? AND ?""", (data_ini, data_fim))]
    return sorted(rec + desp, key=lambda x: x["data"], reverse=True)


def resumo_financeiro(data_ini, data_fim):
    l = lancamentos(data_ini, data_fim)
    receitas = sum(x["valor"] for x in l if x["tipo"] == "Receita")
    despesas = sum(x["valor"] for x in l if x["tipo"] == "Despesa")
    pendente = sum(x["valor"] for x in l if x["tipo"] == "Despesa" and not x["pago"])
    return {"receitas": receitas, "despesas": despesas, "pendente": pendente,
            "lucro": receitas - despesas}