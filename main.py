import flet as ft
from fpdf import FPDF
from datetime import datetime
import re


def main(page: ft.Page):
    # Configuração da janela
    page.title = "Calculadora de Pedidos - CooperPlast"
    page.window.width = 400
    page.window.height = 600

    # Lista de produtos adicionados
    produtos_adicionados = []
    nome_cliente = ft.TextField(label="Nome do Cliente", width=300)

    def limpar_nome(nome):
        """Limpa o nome do cliente para uso no nome do arquivo."""
        return re.sub(r"[^\w\s]", "", nome).replace(" ", "_")

    # Função para atualizar a tabela
    def atualizar_tabela():
        tabela.rows.clear()
        total_valor = 0
        total_peso = 0
        for item in produtos_adicionados:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item[0])),  # Produto
                        ft.DataCell(ft.Text(str(item[1]))),  # Quantidade
                        ft.DataCell(ft.Text("Pct 5Kg")),  # Unidade
                        ft.DataCell(ft.Text(f"{item[2]} kg")),  # Peso Total
                        ft.DataCell(ft.Text(item[3])),  # Valor Total
                    ]
                )
            )
            total_valor += float(item[3].replace("R$", "").strip())
            total_peso += item[2]
        total_geral.value = f"Valor Total: R$ {total_valor:.2f}"
        total_peso_geral.value = f"Peso Total: {total_peso} kg"
        page.update()

    # Função para abrir a janela de seleção de produto
    def abrir_selecao_produto():
        quantidade_valor = 0  # Quantidade inicial

        def adicionar_produto(e):
            produto = produto_selecionado.value
            preco = {
                "Sacola Ref. 30x40": 20.0,
                "Sacola Ref. 40x50": 25.0,
                "Sacola Ref. 50x60": 30.0,
            }
            preco_total = preco[produto] * quantidade_valor
            peso_total = quantidade_valor * 5  # Cada pacote tem 5kg

            if quantidade_valor > 0:
                produtos_adicionados.append(
                    (produto, quantidade_valor, peso_total, f"R$ {preco_total:.2f}")
                )
                atualizar_tabela()

            # Fecha a janela
            page.dialog.open = False
            page.update()

        def incrementar(e):
            nonlocal quantidade_valor
            quantidade_valor += 1
            quantidade.value = str(quantidade_valor)
            page.update()

        def decrementar(e):
            nonlocal quantidade_valor
            if quantidade_valor > 0:
                quantidade_valor -= 1
            quantidade.value = str(quantidade_valor)
            page.update()

        # Conteúdo da janela flutuante
        produto_selecionado = ft.Dropdown(
            options=[
                ft.dropdown.Option("Sacola Ref. 30x40"),
                ft.dropdown.Option("Sacola Ref. 40x50"),
                ft.dropdown.Option("Sacola Ref. 50x60"),
            ],
            value="Sacola Ref. 30x40",
            label="Produto",
        )
        quantidade = ft.Text(value="0", size=16, weight=ft.FontWeight.BOLD)
        dialog = ft.AlertDialog(
            title=ft.Text("Selecione o Produto"),
            content=ft.Column(
                [
                    produto_selecionado,
                    ft.Row(
                        [
                            ft.ElevatedButton("-", on_click=decrementar),
                            quantidade,
                            ft.ElevatedButton("+", on_click=incrementar),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ]
            ),
            actions=[
                ft.ElevatedButton("Adicionar", on_click=adicionar_produto),
                ft.ElevatedButton("Cancelar", on_click=lambda e: page.dialog.close()),
            ],
        )
        page.dialog = dialog
        page.dialog.open = True
        page.update()

    # Função para gerar o PDF
    def gerar_pdf(e):
        if not produtos_adicionados:
            page.snack_bar = ft.SnackBar(ft.Text("Não há produtos na lista para gerar o relatório!"))
            page.snack_bar.open = True
            page.update()
            return

        cliente = nome_cliente.value or "Não informado"
        cliente_limpo = limpar_nome(cliente)
        data_atual = datetime.now().strftime("%d/%m/%Y")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Cabeçalho
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 10, txt="Relatório de Produtos - CooperPlast", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Data: {data_atual}", ln=True, align="C")
        pdf.ln(10)

        # Cabeçalho da tabela
        pdf.cell(80, 10, "Produto", border=1)
        pdf.cell(20, 10, "Qtd", border=1)
        pdf.cell(30, 10, "Und", border=1)
        pdf.cell(30, 10, "Peso", border=1)
        pdf.cell(30, 10, "Valor", border=1, ln=True)

        # Adicionando os produtos
        total_valor = 0
        total_peso = 0
        for item in produtos_adicionados:
            pdf.cell(80, 10, item[0], border=1)
            pdf.cell(20, 10, str(item[1]), border=1)
            pdf.cell(30, 10, "Pct 5Kg", border=1)
            pdf.cell(30, 10, f"{item[2]} kg", border=1)
            pdf.cell(30, 10, item[3], border=1, ln=True)
            total_valor += float(item[3].replace("R$", "").strip())
            total_peso += item[2]

        # Totais
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt=f"Peso Total: {total_peso} kg", ln=True)
        pdf.cell(200, 10, txt=f"Valor Total: R$ {total_valor:.2f}", ln=True)

        # Salvar o PDF
        pdf.output(f"relatorio_{cliente_limpo}.pdf")
        page.snack_bar = ft.SnackBar(ft.Text("Relatório PDF gerado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    # Exibição da lista de produtos
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Produto")),
            ft.DataColumn(ft.Text("Qtd")),
            ft.DataColumn(ft.Text("Und")),
            ft.DataColumn(ft.Text("Peso")),
            ft.DataColumn(ft.Text("Valor")),
        ],
        rows=[],
    )

    # Totais
    total_geral = ft.Text(value="Valor Total: R$ 0.00", size=18, color="blue", weight=ft.FontWeight.BOLD)
    total_peso_geral = ft.Text(value="Peso Total: 0 kg", size=18, color="blue", weight=ft.FontWeight.BOLD)

    # Botões
    adicionar_btn = ft.ElevatedButton("Adicionar Produto", on_click=lambda e: abrir_selecao_produto())
    gerar_pdf_btn = ft.ElevatedButton("Gerar Relatório em PDF", on_click=gerar_pdf)

    # Adicionando elementos à página
    page.add(
        nome_cliente,
        ft.Text(
            "Calculadora de Pedidos",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        ),
        adicionar_btn,
        tabela,
        total_peso_geral,
        total_geral,
        gerar_pdf_btn,
    )


# Executar a aplicação
ft.app(target=main)
