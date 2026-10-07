from datetime import date
import pytest
from financeiro.categoria import Categoria
from financeiro.conciliador import ConciliadorBancario, ItemExtrato
from financeiro.conta import ContaBancaria
from financeiro.forma_pagamento import Pix
from financeiro.lancamento import Despesa, Receita


@pytest.fixture(autouse=True)
def reset_categorias():
    Categoria.limpar_cadastros()


@pytest.fixture
def conta_nubank():
    return ContaBancaria(nome="Nubank", instituicao="Nubank", saldo_inicial=3000.0)


@pytest.fixture
def categoria_geral():
    return Categoria.criar_ou_obter("Geral")


def test_conciliacao_total_quando_todos_lancamentos_batem(conta_nubank, categoria_geral):
    conciliador = ConciliadorBancario(conta=conta_nubank)

    l1 = Receita(valor=1000.0, data=date(2026, 10, 1), conta=conta_nubank, categoria=categoria_geral)
    d1 = Despesa(valor=50.0, data=date(2026, 10, 2), conta=conta_nubank, forma_pagamento=Pix(), categoria=categoria_geral)

    conciliador.sincronizar_lancamentos([l1, d1])

    extrato = [
        ItemExtrato(id_transacao="TX001", data=date(2026, 10, 1), valor=1000.0, descricao_bruta="TED RECEBIDA"),
        ItemExtrato(id_transacao="TX002", data=date(2026, 10, 2), valor=-50.0, descricao_bruta="PIX ENVIADO MERCADO"),
    ]
    conciliador.carregar_extrato(extrato)

    resultado = conciliador.conciliar()

    assert resultado["total_pendentes"] == 0
    assert len(resultado["conciliados"]) == 2


def test_detecta_movimentacoes_nao_lancadas_no_extrato(conta_nubank, categoria_geral):
    conciliador = ConciliadorBancario(conta=conta_nubank)

    l1 = Receita(valor=500.0, data=date(2026, 10, 1), conta=conta_nubank, categoria=categoria_geral)
    conciliador.sincronizar_lancamentos([l1])

    extrato = [
        ItemExtrato(id_transacao="TX001", data=date(2026, 10, 1), valor=500.0, descricao_bruta="DEPOSITO"),
        ItemExtrato(id_transacao="TX002", data=date(2026, 10, 2), valor=-35.0, descricao_bruta="FARMACIA"),
        ItemExtrato(id_transacao="TX003", data=date(2026, 10, 3), valor=-120.0, descricao_bruta="POSTO GASOLINA"),
    ]
    conciliador.carregar_extrato(extrato)

    resultado = conciliador.conciliar()

    assert resultado["total_pendentes"] == 2
    assert extrato[1] in resultado["pendentes"]
    assert extrato[2] in resultado["pendentes"]


def test_gerar_lancamento_sugerido_para_despesa_e_receita(conta_nubank, categoria_geral):
    conciliador = ConciliadorBancario(conta=conta_nubank)
    cat_pendente = Categoria.criar_ou_obter("A Classificar")

    item_saida = ItemExtrato(id_transacao="TX010", data=date(2026, 10, 2), valor=-45.0, descricao_bruta="PADARIA")
    item_entrada = ItemExtrato(id_transacao="TX011", data=date(2026, 10, 3), valor=150.0, descricao_bruta="PIX RECEBIDO")

    despesa_sugerida = conciliador.gerar_lancamento_sugerido(item_saida, categoria_padrao=cat_pendente)
    receita_sugerida = conciliador.gerar_lancamento_sugerido(item_entrada, categoria_padrao=cat_pendente)

    assert isinstance(despesa_sugerida, Despesa)
    assert despesa_sugerida.valor == 45.0
    assert despesa_sugerida.categoria == cat_pendente

    assert isinstance(receita_sugerida, Receita)
    assert receita_sugerida.valor == 150.0
    assert receita_sugerida.categoria == cat_pendente


def test_impede_itens_duplicados_no_extrato(conta_nubank):
    conciliador = ConciliadorBancario(conta=conta_nubank)
    extrato_duplicado = [
        ItemExtrato(id_transacao="TX_REPETIDA", data=date(2026, 10, 1), valor=100.0, descricao_bruta="PIX"),
        ItemExtrato(id_transacao="TX_REPETIDA", data=date(2026, 10, 1), valor=100.0, descricao_bruta="PIX"),
    ]
    with pytest.raises(ValueError, match="Transação duplicada"):
        conciliador.carregar_extrato(extrato_duplicado)