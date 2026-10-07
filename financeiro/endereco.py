import re
from typing import Optional


class Endereco:
    def __init__(
        self,
        logradouro: str,
        numero: str,
        bairro: str,
        cidade: str,
        estado: str,
        complemento: Optional[str] = None,
        cep: Optional[str] = None,) -> None:
        if not logradouro or not logradouro.strip():
            raise ValueError("O logradouro não pode ser vazio.")
        if not numero or not numero.strip():
            raise ValueError("O número não pode ser vazio.")
        if not bairro or not bairro.strip():
            raise ValueError("O bairro não pode ser vazio.")
        if not cidade or not cidade.strip():
            raise ValueError("A cidade não pode ser vazia.")
        if not estado or not estado.strip():
            raise ValueError("O estado não pode ser vazio.")

        self.logradouro = logradouro.strip()
        self.numero = numero.strip()
        self.bairro = bairro.strip()
        self.cidade = cidade.strip()
        self.estado = estado.strip().upper()
        self.complemento = complemento.strip() if complemento and complemento.strip() else None
        self.cep = self._sanitizar_cep(cep) if cep and cep.strip() else None

    def _sanitizar_cep(self, cep: str) -> str:
        digitos = re.sub(r"\D", "", cep)
        if len(digitos) != 8:
            raise ValueError("CEP inválido: deve conter 8 dígitos numéricos.")
        return digitos

    @property
    def cep_formatado(self) -> Optional[str]:
        if not self.cep:
            return None
        return f"{self.cep[:5]}-{self.cep[5:]}"

    @property
    def formatado(self) -> str:
        comp = f", {self.complemento}" if self.complemento else ""
        texto = f"{self.logradouro}, {self.numero}{comp} - {self.bairro}, {self.cidade}/{self.estado}"
        if self.cep_formatado:
            texto += f" - CEP: {self.cep_formatado}"
        return texto