from datetime import date
import pytest
from financeiro.categoria import Categoria
from financeiro.conta import ContaBancaria
from financeiro.fechamento import Fechamento
from financeiro.forma_pagamento import Pix
from financeiro.lancamento import ContaRecorrente, GastoFixo, Investimento, Receita


@pytest.fixture(autouse=True)
def reset_categorias():
    Categoria.limpar_cadastros()


@pytest.fixture
def conta():
    return ContaBancaria(nome="Nubank", instituicao="Nubank", saldo_inicial=20000.0)


def test_cria_fechamento_com_sucesso():
    fechamento = Fechamento(mes=10, ano=2026)
    assert fechamento.mes == 10
    assert fechamento.ano == 2026
    assert fechamento.total_receitas == 0.0
    assert fechamento.total_despesas == 0.0


def test_fechamento_calcula_encargos_e_contas_atrasadas(conta):
    fechamento = Fechamento(mes=10, ano=2026)
    cat_moradia = Categoria.criar_ou_obter("Moradia")

    gf = GastoFixo(
        valor_pago=1530.0,
        valor_esperado=1500.0,
        numero_parcela=5,
        total_parcelas=120,
        data=date(2026, 10, 2),
        conta=conta,
        forma_pagamento=Pix(),
        categoria=cat_moradia,
    )
    cr = ContaRecorrente(
        valor_pago=250.0,
        data_vencimento=date(2026, 10, 1),
        mes_competencia=9,
        ano_competencia=2026,
        data_pagamento=date(2026, 10, 5),
        conta=conta,
        forma_pagamento=Pix(),
        categoria=cat_moradia,
    )

    fechamento.adicionar_lancamento(gf)
    fechamento.adicionar_lancamento(cr)

    assert len(fechamento.gastos_fixos) == 1
    assert fechamento.total_encargos_gastos_fixos == 30.0
    assert len(fechamento.contas_recorrentes) == 1
    assert fechamento.total_contas_atrasadas == 1


def test_fechamento_consolida_patrimonio_e_lucro_investimentos(conta):
    fechamento = Fechamento(mes=10, ano=2026)
    cat_invest = Categoria.criar_ou_obter("Investimentos")

    cdb = Investimento(
        valor_aplicado=5000.0,
        data_aplicacao=date(2026, 10, 2),
        conta=conta,
        categoria=cat_invest,
        produto="CDB 110% CDI",
    )
    cdb.atualizar_rendimento(5120.0)
    fechamento.adicionar_lancamento(cdb)

    assert fechamento.total_investimentos_aportados == 5000.0
    assert fechamento.patrimonio_investido_total == 5120.0
    assert fechamento.rendimento_total_acumulado == 120.0


def test_erro_adicionar_lancamento_de_outro_mes_ou_ano(conta):
    fechamento = Fechamento(mes=10, ano=2026)
    cat = Categoria.criar_ou_obter("Geral")
    lancamento_setembro = Receita(
        valor=100.0,
        data=date(2026, 9, 30),
        conta=conta,
        categoria=cat,
    )
    with pytest.raises(ValueError, match="não pertence ao fechamento"):
        fechamento.adicionar_lancamento(lancamento_setembro)