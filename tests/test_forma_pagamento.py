import pytest
from financeiro.conta import CarteiraFisica, ContaBancaria
from financeiro.forma_pagamento import CartaoDebito, Dinheiro, Pix, Transferencia


@pytest.fixture
def carteira():
    return CarteiraFisica(nome="Carteira de Bolso", saldo_inicial=80.0)


@pytest.fixture
def conta_bancaria():
    return ContaBancaria(
        nome="Conta Corrente",
        instituicao="Nubank",
        saldo_inicial=500.0,
    )


def test_dinheiro_valido_com_carteira_fisica(carteira):
    forma = Dinheiro()
    assert forma.descricao == "Dinheiro"
    forma.validar_conta(carteira)


def test_erro_dinheiro_com_conta_bancaria(conta_bancaria):
    forma = Dinheiro()
    with pytest.raises(ValueError, match="exigem uma Carteira Física"):
        forma.validar_conta(conta_bancaria)


def test_pix_valido_com_conta_bancaria(conta_bancaria):
    forma = Pix()
    assert forma.descricao == "Pix"
    forma.validar_conta(conta_bancaria)


def test_erro_pix_com_carteira_fisica(carteira):
    forma = Pix()
    with pytest.raises(ValueError, match="não suporta transações via Pix"):
        forma.validar_conta(carteira)


def test_cartao_debito_valido_com_conta_bancaria(conta_bancaria):
    forma = CartaoDebito()
    assert forma.descricao == "Cartão de Débito"
    forma.validar_conta(conta_bancaria)


def test_erro_cartao_debito_com_carteira_fisica(carteira):
    forma = CartaoDebito()
    with pytest.raises(ValueError, match="exige vínculo com Conta Bancária"):
        forma.validar_conta(carteira)


def test_transferencia_valida_com_conta_eletronica(conta_bancaria):
    forma = Transferencia()
    assert forma.descricao == "Transferência"
    forma.validar_conta(conta_bancaria)


def test_igualdade_entre_formas_pagamento():
    p1 = Pix()
    p2 = Pix()
    d1 = Dinheiro()
    assert p1 == p2
    assert p1 != d1