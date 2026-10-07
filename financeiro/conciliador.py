from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List, Optional
from financeiro.categoria import Categoria
from financeiro.conta import ContaBancaria
from financeiro.forma_pagamento import Transferencia
from financeiro.lancamento import Despesa, Lancamento, Receita


class StatusConciliacao(Enum):
    CONCILIADO = "Conciliado"
    PENDENTE = "Pendente"
    DIVERGENTE = "Divergente"


@dataclass(frozen=True)
class ItemExtrato:
    id_transacao: str
    data: date
    valor: float
    descricao_bruta: str

    def __post_init__(self) -> None:
        if not self.id_transacao or not self.id_transacao.strip():
            raise ValueError("O identificador da transação bancária é obrigatório.")
        if self.valor == 0.0:
            raise ValueError("O valor da movimentação do extrato não pode ser zero.")


class ConciliadorBancario:
    def __init__(self, conta: ContaBancaria) -> None:
        if not isinstance(conta, ContaBancaria):
            raise TypeError("A conciliação bancária exige uma instância de ContaBancaria.")

        self.conta = conta
        self._extrato: List[ItemExtrato] = []
        self._lancamentos_sistema: List[Lancamento] = []

    def carregar_extrato(self, itens: List[ItemExtrato]) -> None:
        ids_vistos = set()
        for item in itens:
            if item.id_transacao in ids_vistos:
                raise ValueError(f"Transação duplicada no extrato: {item.id_transacao}")
            ids_vistos.add(item.id_transacao)
        self._extrato = list(itens)

    def sincronizar_lancamentos(self, lancamentos: List[Lancamento]) -> None:
        self._lancamentos_sistema = [l for l in lancamentos if l.conta is self.conta]

    def conciliar(self) -> Dict[str, List]:
        conciliados: List[ItemExtrato] = []
        pendentes: List[ItemExtrato] = []

        lancamentos_disponiveis = list(self._lancamentos_sistema)

        for item in self._extrato:
            par_encontrado: Optional[Lancamento] = None

            for lanc in lancamentos_disponiveis:
                mesmo_valor = abs(lanc.valor - abs(item.valor)) < 0.001
                mesma_data = lanc.data == item.data
                mesmo_tipo = (isinstance(lanc, Receita) and item.valor > 0) or (
                    isinstance(lanc, Despesa) and item.valor < 0
                )

                if mesmo_valor and mesma_data and mesmo_tipo:
                    par_encontrado = lanc
                    break

            if par_encontrado:
                conciliados.append(item)
                lancamentos_disponiveis.remove(par_encontrado)
            else:
                pendentes.append(item)

        return {
            "conciliados": conciliados,
            "pendentes": pendentes,
            "total_pendentes": len(pendentes),
        }

    def gerar_lancamento_sugerido(
        self,
        item: ItemExtrato,
        categoria_padrao: Categoria,) -> Lancamento:
        if item.valor > 0:
            return Receita(
                valor=item.valor,
                data=item.data,
                conta=self.conta,
                categoria=categoria_padrao,
                observacao=f"Conciliado automaticamente: {item.descricao_bruta}",
            )
        else:
            return Despesa(
                valor=abs(item.valor),
                data=item.data,
                conta=self.conta,
                forma_pagamento=Transferencia(),
                categoria=categoria_padrao,
                observacao=f"Conciliado automaticamente: {item.descricao_bruta}",
            )