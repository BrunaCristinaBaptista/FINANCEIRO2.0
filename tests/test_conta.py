import pytest
from financeiro.conta import CarteiraFisica, ContaBancaria


def test_cria_carteira_fisica_com_sucesso():
    carteira = CarteiraFisica(nome="Bolso", saldo_inicial=50.0)
    assert carteira.nome == "Bolso"
    assert carteira.saldo_atual == 50.0
    assert carteira.permite_pagamento_eletronico is False


def test_cria_conta_bancaria_com_sucesso():
    banco = ContaBancaria(
        nome="Principal",
        instituicao="Nubank",
        saldo_inicial=1200.0,
        agencia="0001",
        numero_conta="12345-6",
    )
    assert banco.nome == "Principal"
    assert banco.instituicao == "Nubank"
    assert banco.saldo_atual == 1200.0
    assert banco.agencia == "0001"
    assert banco.numero_conta == "12345-6"
    assert banco.permite_pagamento_eletronico is True


def test_creditar_aumenta_saldo():
    carteira = CarteiraFisica(nome="Bolso", saldo_inicial=20.0)
    carteira.creditar(30.0)
    assert carteira.saldo_atual == 50.0


def test_debitar_reduz_saldo():
    banco = ContaBancaria(nome="Inter", instituicao="Inter", saldo_inicial=100.0)
    banco.debitar(40.0)
    assert banco.saldo_atual == 60.0


def test_erro_debitar_saldo_insuficiente():
    banco = ContaBancaria(nome="Inter", instituicao="Inter", saldo_inicial=50.0)
    with pytest.raises(ValueError, match="Saldo insuficiente"):
        banco.debitar(60.0)


def test_transferencia_entre_contas_com_sucesso():
    origem = ContaBancaria(nome="Itaú", instituicao="Itaú", saldo_inicial=500.0)
    destino = CarteiraFisica(nome="Carteira", saldo_inicial=50.0)

    origem.transferir(valor=100.0, destino=destino)

    assert origem.saldo_atual == 400.0
    assert destino.saldo_atual == 150.0


def test_erro_transferir_para_si_mesma():
    conta = ContaBancaria(nome="Nubank", instituicao="Nubank", saldo_inicial=200.0)
    with pytest.raises(ValueError, match="mesma conta"):
        conta.transferir(valor=50.0, destino=conta)


def test_erro_transferir_destino_invalido():
    conta = ContaBancaria(nome="Nubank", instituicao="Nubank", saldo_inicial=200.0)
    with pytest.raises(TypeError, match="instância válida de Conta"):
        conta.transferir(valor=50.0, destino="chave_pix_qualquer")  # type: ignore


def test_erro_transferir_saldo_insuficiente_preserva_destino():
    origem = ContaBancaria(nome="Origem", instituicao="Banco A", saldo_inicial=30.0)
    destino = CarteiraFisica(nome="Destino", saldo_inicial=10.0)

    with pytest.raises(ValueError, match="Saldo insuficiente"):
        origem.transferir(valor=50.0, destino=destino)

    assert origem.saldo_atual == 30.0
    assert destino.saldo_atual == 10.0


def test_formatacao_saldo_brasileiro():
    conta = ContaBancaria(nome="Reserva", instituicao="Caixa", saldo_inicial=1500.75)
    assert conta.saldo_formatado == "R$ 1.500,75"
    