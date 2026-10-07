from typing import Any, Dict, List, Optional
from financeiro.conciliador import ConciliadorBancario, ItemExtrato
from financeiro.fechamento import Fechamento
from financeiro.lancamento import Despesa


class RelatorioExtrato:
    """Consolida os dados de Fechamento e Conciliação em relatórios analíticos e dados gráficos."""

    def __init__(
        self,
        fechamento: Fechamento,
        conciliador: Optional[ConciliadorBancario] = None,) -> None:
        if not isinstance(fechamento, Fechamento):
            raise TypeError("O relatório exige uma instância válida de Fechamento.")

        self.fechamento = fechamento
        self.conciliador = conciliador

    def gastos_por_categoria(self) -> Dict[str, Dict[str, float]]:
        totais: Dict[str, float] = {}
        for l in self.fechamento._lancamentos:
            if isinstance(l, Despesa):
                nome_cat = l.categoria.nome
                totais[nome_cat] = totais.get(nome_cat, 0.0) + l.valor

        total_geral = self.fechamento.total_despesas
        resultado = {}
        for cat, valor in totais.items():
            pct = round((valor / total_geral) * 100, 2) if total_geral > 0 else 0.0
            resultado[cat] = {
                "valor_total": valor,
                "percentual": pct,
            }
        return resultado

    def movimentacoes_nao_contabilizadas(self) -> List[ItemExtrato]:
        if not self.conciliador:
            return []
        resultado_conciliacao = self.conciliador.conciliar()
        return resultado_conciliacao["pendentes"]

    @property
    def total_saidas_nao_contabilizadas(self) -> float:
        itens = self.movimentacoes_nao_contabilizadas()
        return abs(sum(i.valor for i in itens if i.valor < 0))

    @property
    def total_entradas_nao_contabilizadas(self) -> float:
        itens = self.movimentacoes_nao_contabilizadas()
        return sum(i.valor for i in itens if i.valor > 0)

    def dados_graficos(self) -> Dict[str, Any]:
        gastos_cat = self.gastos_por_categoria()
        total_fixo = sum(g.valor for g in self.fechamento.gastos_fixos)
        total_recorrente = sum(c.valor for c in self.fechamento.contas_recorrentes)
        total_variavel = self.fechamento.total_despesas - (total_fixo + total_recorrente)

        return {
            "comparativo_mensal": {
                "labels": ["Receitas", "Despesas", "Aportes Invest."],
                "valores": [
                    self.fechamento.total_receitas,
                    self.fechamento.total_despesas,
                    self.fechamento.total_investimentos_aportados,
                ],
            },
            "perfil_despesas": {
                "labels": ["Gastos Fixos", "Contas Recorrentes", "Gastos Variáveis"],
                "valores": [total_fixo, total_recorrente, max(0.0, total_variavel)],
            },
            "despesas_por_categoria": {
                "labels": list(gastos_cat.keys()),
                "valores": [dados["valor_total"] for dados in gastos_cat.values()],
                "percentuais": [dados["percentual"] for dados in gastos_cat.values()],
            },
            "carteira_investimentos": {
                "labels": [inv.produto for inv in self.fechamento.investimentos],
                "aportado": [inv.valor for inv in self.fechamento.investimentos],
                "saldo_atual": [inv.saldo_atualizado for inv in self.fechamento.investimentos],
            },
            "status_conciliacao": {
                "labels": ["Lançados no Sistema", "Pendentes no Extrato"],
                "valores": [
                    len(self.fechamento._lancamentos),
                    len(self.movimentacoes_nao_contabilizadas()),
                ],
            },
        }

    def _formatar_moeda(self, valor: float) -> str:
        sinal = "-" if valor < 0 else ""
        valor_abs = abs(valor)
        texto = f"{valor_abs:,.2f}"
        texto_br = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        prefixo = f"{sinal} R$ " if sinal else "R$ "
        return f"{prefixo}{texto_br}"

    def gerar_extrato_texto(self) -> str:
        linhas = [
            "==================================================",
            f"          EXTRATO CONSOLIDADO: {self.fechamento.mes:02d}/{self.fechamento.ano}",
            "==================================================",
            f"Receitas Totais:       {self.fechamento.total_receitas_formatado}",
            f"Despesas Totais:       {self.fechamento.total_despesas_formatado}",
            f"Resultado Líquido:     {self.fechamento.resultado_liquido_formatado}",
            f"Taxa de Poupança:      {self.fechamento.taxa_poupanca_percentual}%",
            "--------------------------------------------------",
            "GASTOS CONTRATUAIS / FIXOS:",
        ]

        if not self.fechamento.gastos_fixos:
            linhas.append("  (Nenhum gasto fixo/parcelado registrado)")
        else:
            for gf in self.fechamento.gastos_fixos:
                encargo_str = f" [Variação: {self._formatar_moeda(gf.diferenca_encargos)}]" if gf.diferenca_encargos != 0 else ""
                linhas.append(
                    f"  • {gf.categoria.nome} (Parc. {gf.indicador_parcela}): "
                    f"{self._formatar_moeda(gf.valor)}{encargo_str}"
                )

        linhas.append("--------------------------------------------------")
        linhas.append("CONTAS RECORRENTES (CONSUMO):")
        if not self.fechamento.contas_recorrentes:
            linhas.append("  (Nenhuma conta recorrente registrada)")
        else:
            for cr in self.fechamento.contas_recorrentes:
                status_atraso = " [PAGO COM ATRASO]" if cr.pago_com_atraso else " [EM DIA]"
                linhas.append(
                    f"  • {cr.categoria.nome} (Comp. {cr.competencia_formatada}): "
                    f"{self._formatar_moeda(cr.valor)}{status_atraso}"
                )

        linhas.append("--------------------------------------------------")
        linhas.append("POSIÇÃO DE INVESTIMENTOS:")
        if not self.fechamento.investimentos:
            linhas.append("  (Nenhum aporte no mês)")
        else:
            for inv in self.fechamento.investimentos:
                linhas.append(
                    f"  • {inv.produto} ({inv.indexador}): "
                    f"Aporte: {self._formatar_moeda(inv.valor)} | "
                    f"Saldo Atual: {self._formatar_moeda(inv.saldo_atualizado)} | "
                    f"Rendimento: {self._formatar_moeda(inv.rendimento_total)} ({inv.rentabilidade_percentual}%)"
                )
            linhas.append(
                f"  Total Aportado: {self._formatar_moeda(self.fechamento.total_investimentos_aportados)} | "
                f"Patrimônio Atual: {self._formatar_moeda(self.fechamento.patrimonio_investido_total)}"
            )

        linhas.append("--------------------------------------------------")
        linhas.append("AUDITORIA BANCÁRIA (NÃO CONTABILIZADOS):")
        pendentes = self.movimentacoes_nao_contabilizadas()
        if not pendentes:
            linhas.append("  [OK] Todas as movimentações bancárias estão registradas.")
        else:
            linhas.append(f"  [ALERTA] {len(pendentes)} movimentações pendentes no extrato:")
            for p in pendentes:
                sinal = "+" if p.valor > 0 else "-"
                v_fmt = self._formatar_moeda(abs(p.valor))
                linhas.append(f"    - {p.data.strftime('%d/%m')} | {p.descricao_bruta:<20} | {sinal} {v_fmt}")

        linhas.append("==================================================")
        return "\n".join(linhas)