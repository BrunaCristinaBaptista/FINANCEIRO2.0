import pytest
from financeiro.categoria import Categoria


@pytest.fixture(autouse=True)
def reset_memoria():
    Categoria.limpar_cadastros()


def test_cria_categoria_com_nome():
    cat = Categoria("Alimentação")
    assert cat.nome == "Alimentação"


def test_criar_categoria_com_sucesso_apenas_nome():
    cat = Categoria(nome="Alimentação")
    assert cat.nome == "Alimentação"
    assert cat.descricao is None


def test_criar_categoria_com_nome_e_descricao():
    cat = Categoria(
        nome="Salário",
        descricao="Entradas provenientes do emprego principal",
    )
    assert cat.nome == "Salário"
    assert cat.descricao == "Entradas provenientes do emprego principal"


def test_erro_ao_criar_categoria_com_nome_vazio():
    with pytest.raises(ValueError, match="O nome da categoria não pode ser vazio."):
        Categoria(nome="   ")


def test_impede_duplicacao_com_mesmo_nome_ou_acentos():
    Categoria.criar("Alimentação")
    with pytest.raises(ValueError, match="já está cadastrada"):
        Categoria.criar("alimentacao")


def test_criar_ou_obter_reaproveita_instancia():
    cat1 = Categoria.criar_ou_obter("Saúde")
    cat2 = Categoria.criar_ou_obter("saude")

    assert cat1 is cat2
    assert cat2.nome == "Saúde"