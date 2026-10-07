from datetime import date
import pytest
from financeiro.categoria import Categoria
from financeiro.conta import ContaBancaria
from financeiro.estabelecimento import Estabelecimento
from financeiro.forma_pagamento import Pix
from financeiro.lancamento import (
    ContaRecorrente,
    Despesa,
    GastoFixo,
    Investimento,
    Lancamento,
    Receita,
)


@pytest.fixture(autouse=True)
def reset_categorias():
    Categoria.limpar_cadastros()


@pytest.fixture
def conta_banco():
    return ContaBancaria(nome="Conta Principal", instituicao="Nubank", saldo_inicial=10000.0)


@pytest.fixture
def cat_alimentacao():
    return Categoria.criar_ou_obter("Alimentação")


@pytest.fixture
def cat_moradia():
    return Categoria.criar_ou_obter("Moradia")


def test_cria_despesa_debita_saldo_e_aplica_sinal_negativo(conta_banco, cat_alimentacao):
    desp = Despesa(
        valor=50.0,
        data=date(2026, 10, 2),
        conta=conta_banco,
        forma_pagamento=Pix(),
        categoria=cat_alimentacao,
    )
    assert conta_banco.saldo_atual == 9950.0
    assert desp.valor_formatado == "- R$ 50,00"


def test_cria_receita_credita_saldo_e_aplica_sinal_positivo(conta_banco):
    cat_salario = Categoria.criar_ou_obter("Salário")
    rec = Receita(
        valor=3500.0,
        data=date(2026, 10, 2),
        conta=conta_banco,
        categoria=cat_salario,
    )
    assert conta_banco.saldo_atual == 13500.0
    assert rec.valor_formatado == "+ R$ 3.500,00"


def test_cria_gasto_fixo_com_diferenca_de_encargos(conta_banco, cat_moradia):
    gasto = GastoFixo(
        valor_pago=1525.50,
        valor_esperado=1500.00,
        numero_parcela=12,
        total_parcelas=360,
        data=date(2026, 10, 2),
        conta=conta_banco,
        forma_pagamento=Pix(),
        categoria=cat_moradia,
    )
    assert gasto.indicador_parcela == "12/360"
    assert gasto.diferenca_encargos == 25.50
    assert conta_banco.saldo_atual == 8474.50


def test_erro_parcela_maior_que_total(conta_banco, cat_moradia):
    with pytest.raises(ValueError, match="não pode ser maior que o total"):
        GastoFixo(
            valor_pago=100.0,
            valor_esperado=100.0,
            numero_parcela=13,
            total_parcelas=12,
            data=date(2026, 10, 2),
            conta=conta_banco,
            forma_pagamento=Pix(),
            categoria=cat_moradia,
        )


def test_cria_conta_recorrente_e_detecta_atraso(conta_banco, cat_moradia):
    fatura = ContaRecorrente(
        valor_pago=215.30,
        data_vencimento=date(2026, 10, 1),
        mes_competencia=9,
        ano_competencia=2026,
        data_pagamento=date(2026, 10, 5),
        conta=conta_banco,
        forma_pagamento=Pix(),
        categoria=cat_moradia,
    )
    assert fatura.competencia_formatada == "09/2026"
    assert fatura.pago_com_atraso is True
    assert conta_banco.saldo_atual == 9784.70


def test_investimento_debita_conta_e_atualiza_rendimento(conta_banco):
    cat_invest = Categoria.criar_ou_obter("Investimentos")
    cdb = Investimento(
        valor_aplicado=5000.0,
        data_aplicacao=date(2026, 10, 2),
        conta=conta_banco,
        categoria=cat_invest,
        produto="CDB Banco Master",
        indexador="110% CDI",
    )
    assert conta_banco.saldo_atual == 5000.0
    assert cdb.rendimento_total == 0.0

    cdb.atualizar_rendimento(5350.0)
    assert cdb.saldo_atualizado == 5350.0
    assert cdb.rendimento_total == 350.0
    assert cdb.rentabilidade_percentual == 7.0
    