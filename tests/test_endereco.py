import pytest
from financeiro.endereco import Endereco


def test_cria_endereco_valido_minimo():
    end = Endereco(
        logradouro="Rua das Acácias",
        numero="45",
        bairro="Jardins",
        cidade="São Paulo",
        estado="sp",
    )
    assert end.logradouro == "Rua das Acácias"
    assert end.numero == "45"
    assert end.bairro == "Jardins"
    assert end.cidade == "São Paulo"
    assert end.estado == "SP"
    assert end.complemento is None
    assert end.cep is None
    assert end.cep_formatado is None
    assert end.formatado == "Rua das Acácias, 45 - Jardins, São Paulo/SP"


def test_cria_endereco_completo_com_mascara_cep():
    end = Endereco(
        logradouro="Av. Central",
        numero="100",
        bairro="Centro",
        cidade="Curitiba",
        estado="PR",
        complemento="Apto 101",
        cep="80010-000",
    )
    assert end.cep == "80010000"
    assert end.cep_formatado == "80010-000"
    assert end.formatado == "Av. Central, 100, Apto 101 - Centro, Curitiba/PR - CEP: 80010-000"


def test_converte_estado_para_maiusculo():
    end = Endereco(
        logradouro="Rua A",
        numero="1",
        bairro="Bairro B",
        cidade="Cidade C",
        estado="mg",
    )
    assert end.estado == "MG"


def test_erro_cep_com_tamanho_invalido():
    with pytest.raises(ValueError, match="CEP inválido"):
        Endereco(
            logradouro="Rua A",
            numero="1",
            bairro="Bairro B",
            cidade="Cidade C",
            estado="MG",
            cep="12345",
        )


@pytest.mark.parametrize(
    "campo_invalido",
    ["logradouro", "numero", "bairro", "cidade", "estado"],)
def test_erro_campos_obrigatorios_vazios(campo_invalido):
    dados = {
        "logradouro": "Rua Principal",
        "numero": "10",
        "bairro": "Centro",
        "cidade": "Porto Alegre",
        "estado": "RS",
    }
    dados[campo_invalido] = "   "

    with pytest.raises(ValueError):
        Endereco(**dados)