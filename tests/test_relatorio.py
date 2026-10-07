from datetime import date
import pytest
from financeiro.categoria import Categoria
from financeiro.conta import ContaBancaria
from financeiro.fechamento import Fechamento
from financeiro.forma_pagamento import Pix
from financeiro.lancamento import ContaRecorrente, GastoFixo, Investimento, Receita
from financeiro.relatorio import RelatorioExtrato


@pytest.fixture(autouse=True)
def reset_categorias():
    Categoria.limpar_cadastros()


@pytest.fixture
def conta():
    return ContaBancaria(nome="Nubank", instituicao="Nubank", saldo_inicial=20000.0)


def test_relatorio_dados_graficos_perfil_despesas_e_carteira(conta):
    fechamento = Fechamento(mes=10, ano=2026)
    cat_moradia = Categoria.criar_ou_obter("Moradia")
    cat_invest = Categoria.criar_ou_obter("Investimentos")

    fechamento.adicionar_lancamento(
        GastoFixo(
            valor_pago=1000.0,
            valor_esperado=1000.0,
            numero_parcela=1,
            total_parcelas=10,
            data=date(2026, 10, 2),
            conta=conta,
            forma_pagamento=Pix(),
            categoria=cat_moradia,
        )
    )
    fechamento.adicionar_lancamento(
        ContaRecorrente(
            valor_pago=200.0,
            data_vencimento=date(2026, 10, 10),
            mes_competencia=9,
            ano_competencia=2026,
            data_pagamento=date(2026, 10, 5),
            conta=conta,
            forma_pagamento=Pix(),
            categoria=cat_moradia,
        )
    )
    fechamento.adicionar_lancamento(
        Investimento(
            valor_aplicado=3000.0,
            data_aplicacao=date(2026, 10, 2),
            conta=conta,
            categoria=cat_invest,
            produto="Tesouro Selic",
        )
    )

    relatorio = RelatorioExtrato(fechamento=fechamento)
    dados = relatorio.dados_graficos()

    assert dados["perfil_despesas"]["valores"] == [1000.0, 200.0, 0.0]
    assert dados["carteira_investimentos"]["labels"] == ["Tesouro Selic"]
    assert dados["carteira_investimentos"]["aportado"] == [3000.0]


def test_extrato_texto_contem_detalhes_especializados(conta):
    fechamento = Fechamento(mes=10, ano=2026)
    cat_moradia = Categoria.criar_ou_obter("Moradia")
    cat_invest = Categoria.criar_ou_obter("Investimentos")

    fechamento.adicionar_lancamento(
        Receita(valor=8000.0, data=date(2026, 10, 1), conta=conta, categoria=cat_moradia)
    )
    fechamento.adicionar_lancamento(
        GastoFixo(
            valor_pago=1550.0,
            valor_esperado=1500.0,
            numero_parcela=12,
            total_parcelas=360,
            data=date(2026, 10, 2),
            conta=conta,
            forma_pagamento=Pix(),
            categoria=cat_moradia,
        )
    )
    fechamento.adicionar_lancamento(
        ContaRecorrente(
            valor_pago=180.0,
            data_vencimento=date(2026, 10, 1),
            mes_competencia=9,
            ano_competencia=2026,
            data_pagamento=date(2026, 10, 3),
            conta=conta,
            forma_pagamento=Pix(),
            categoria=cat_moradia,
        )
    )
    inv = Investimento(
        valor_aplicado=2000.0,
        data_aplicacao=date(2026, 10, 2),
        conta=conta,
        categoria=cat_invest,
        produto="LCI Caixa",
        indexador="95% CDI",
    )
    inv.atualizar_rendimento(2050.0)
    fechamento.adicionar_lancamento(inv)

    relatorio = RelatorioExtrato(fechamento=fechamento)
    texto = relatorio.gerar_extrato_texto()

    assert "Parc. 12/360" in texto
    assert "Variação: R$ 50,00" in texto
    assert "Comp. 09/2026" in texto
    assert "[PAGO COM ATRASO]" in texto
    assert "LCI Caixa (95% CDI)" in texto
    assert "Rendimento: R$ 50,00 (2.5%)" in texto