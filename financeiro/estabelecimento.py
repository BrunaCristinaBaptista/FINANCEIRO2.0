import re
from typing import Optional
from financeiro.categoria import Categoria
from financeiro.endereco import Endereco


class Estabelecimento:
    def __init__(
        self,
        nome: str,
        categoria_padrao: Optional[Categoria] = None,
        cnpj: Optional[str] = None,
        telefone: Optional[str] = None,
        logradouro: Optional[str] = None,
        numero: Optional[str] = None,
        bairro: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        complemento: Optional[str] = None,
        cep: Optional[str] = None,) -> None:
        if not nome or not nome.strip():
            raise ValueError("O nome do estabelecimento não pode ser vazio.")

        self.nome = nome.strip()
        self.categoria_padrao = categoria_padrao
        self.cnpj = self._sanitizar_cnpj(cnpj) if cnpj and cnpj.strip() else None
        self.telefone = self._sanitizar_telefone(telefone) if telefone and telefone.strip() else None

        campos_principais_endereco = [logradouro, numero, bairro, cidade, estado]
        algum_preenchido = any(c and c.strip() for c in campos_principais_endereco)

        if algum_preenchido:
            if not all(c and c.strip() for c in campos_principais_endereco):
                raise ValueError(
                    "Para cadastrar o endereço, forneça logradouro, número, bairro, cidade e estado."
                )
            self.endereco: Optional[Endereco] = Endereco(
                logradouro=logradouro,  # type: ignore
                numero=numero,          # type: ignore
                bairro=bairro,          # type: ignore
                cidade=cidade,          # type: ignore
                estado=estado,          # type: ignore
                complemento=complemento,
                cep=cep,
            )
        else:
            self.endereco = None

    def _sanitizar_cnpj(self, cnpj: str) -> str:
        digitos = re.sub(r"\D", "", cnpj)
        if len(digitos) != 14:
            raise ValueError("CNPJ inválido: deve conter 14 dígitos numéricos.")
        return digitos

    def _sanitizar_telefone(self, telefone: str) -> str:
        digitos = re.sub(r"\D", "", telefone)
        if len(digitos) not in (10, 11):
            raise ValueError("Telefone inválido: deve conter 10 ou 11 dígitos com DDD.")
        return digitos

    @property
    def cnpj_formatado(self) -> Optional[str]:
        if not self.cnpj:
            return None
        return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"

    @property
    def telefone_formatado(self) -> Optional[str]:
        if not self.telefone:
            return None
        if len(self.telefone) == 11:
            return f"({self.telefone[:2]}) {self.telefone[2:7]}-{self.telefone[7:]}"
        return f"({self.telefone[:2]}) {self.telefone[2:6]}-{self.telefone[6:]}"

    @property
    def endereco_formatado(self) -> Optional[str]:
        return self.endereco.formatado if self.endereco else None