import unicodedata
from typing import ClassVar, Dict, Optional


def _normalizar(texto: str) -> str:
    """Remove acentos, espaços extras e transforma em minúsculas."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acento.strip().lower()


class Categoria:
    _cadastradas: ClassVar[Dict[str, "Categoria"]] = {}

    def __init__(self, nome: str, descricao: Optional[str] = None) -> None:
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria não pode ser vazio.")

        self.nome = nome.strip()
        self.descricao = descricao.strip() if descricao else None

    @classmethod
    def criar(cls, nome: str, descricao: Optional[str] = None) -> "Categoria":
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria não pode ser vazio.")

        chave = _normalizar(nome)
        if chave in cls._cadastradas:
            existente = cls._cadastradas[chave]
            raise ValueError(
                f"A categoria '{nome.strip()}' já está cadastrada como '{existente.nome}'."
            )

        nova = cls(nome=nome, descricao=descricao)
        cls._cadastradas[chave] = nova
        return nova

    @classmethod
    def criar_ou_obter(cls, nome: str, descricao: Optional[str] = None) -> "Categoria":
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria não pode ser vazio.")

        chave = _normalizar(nome)
        if chave not in cls._cadastradas:
            nova = cls(nome=nome, descricao=descricao)
            cls._cadastradas[chave] = nova

        return cls._cadastradas[chave]

    @classmethod
    def limpar_cadastros(cls) -> None:
        cls._cadastradas.clear()