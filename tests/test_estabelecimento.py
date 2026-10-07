import pytest
from financeiro.categoria import Categoria
from financeiro.estabelecimento import Estabelecimento


def test_cria_estabelecimento_apenas_com_nome():
    est = Estabelecimento(nome="Restaurante do João")
    assert est.nome == "Restaurante do João"
    assert est.categoria_padrao is None
    assert est.cnpj is None
    assert est.cnpj_formatado is None
    assert est.telefone is None
    assert est.telefone_formatado is None
    assert est.endereco is None
    assert est.endereco_formatado is None


def test_cria_estabelecimento_com_categoria_padrao():
    categoria = Categoria.criar_ou_obter(nome="Alimentação")
    est = Estabelecimento(nome="Restaurante do João", categoria_padrao=categoria)

    assert est.categoria_padrao == categoria
    assert est.categoria_padrao.nome == "Alimentação"


def test_sanitizacao_e_mascara_cnpj():
    est = Estabelecimento(nome="Empresa X", cnpj="12.345.678/0001-95")
    assert est.cnpj == "12345678000195"
    assert est.cnpj_formatado == "12.345.678/0001-95"


def test_erro_ao_informar_cnpj_invalido():
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Estabelecimento(nome="Empresa X", cnpj="123")


def test_sanitizacao_e_mascara_telefone_celular_e_fixo():
    cel = Estabelecimento(nome="Farmácia 24h", telefone="(11) 98765-4321")
    fixo = Estabelecimento(nome="Consultório", telefone="4132221111")

    assert cel.telefone == "11987654321"
    assert cel.telefone_formatado == "(11) 98765-4321"
    assert fixo.telefone == "4132221111"
    assert fixo.telefone_formatado == "(41) 3222-1111"


def test_erro_ao_informar_telefone_invalido():
    with pytest.raises(ValueError, match="Telefone inválido"):
        Estabelecimento(nome="Loja Teste", telefone="1234567")


def test_composicao_endereco_completo():
    est = Estabelecimento(
        nome="Padaria Pão Quente",
        logradouro="Rua das Flores",
        numero="123",
        bairro="Centro",
        cidade="Curitiba",
        estado="pr",
        complemento="Loja A",
        cep="80010-000",
    )
    assert est.endereco is not None
    assert est.endereco.cidade == "Curitiba"
    assert est.endereco.estado == "PR"
    assert est.endereco_formatado == (
        "Rua das Flores, 123, Loja A - Centro, Curitiba/PR - CEP: 80010-000"
    )


def test_erro_ao_passar_endereco_incompleto():
    with pytest.raises(ValueError, match="Para cadastrar o endereço, forneça"):
        Estabelecimento(
            nome="Banca Sem Endereço Completo",
            logradouro="Rua Sem Fim",
            numero="10",
        )


def test_erro_ao_criar_sem_nome():
    with pytest.raises(ValueError, match="O nome do estabelecimento não pode ser vazio."):
        Estabelecimento(nome="   ")