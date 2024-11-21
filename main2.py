import flet as ft
from fpdf import FPDF  # Biblioteca para gerar PDFs


def main(page: ft.Page):
    # Configuração da janela
    page.title = "Calculadora de Pedidos - CooperPlast"
    page.window_width = 400
    page.window_height = 600

    # Lista de produtos adicionados
    produtos_adicionados = []

    # Variáveis globais para seleção de produto
    produto_selecionado = ft.Ref[ft.Text]()
    quantidade = ft.Ref[ft.Text]()
    quantidade_valor = 0

    # Função para abrir a janela de seleção de produto
    def abrir_selecao_produto():
        nonlocal quantidade_valor

        def adicionar_produto(e):
            nonlocal quantidade_valor
            nonlocal produto_selecionado

            preco = {"Sacola Ref. 38x48": 25.0, "Sacola Ref. 40x50": 45.0}
            produto = produto_selecionado.current.value
            preco_total = preco[produto] * quantidade_valor

            if quantidade_valor > 0:
                produtos_adicionados.append((produto, quantidade_valor, f"R$ {preco_total:.2f}"))
                atualizar_tabela()

            # Fecha a janela
            page.dialog.open = False
            page.update()

        # Funções de incrementar e decrementar a quantidade
        def incrementar(e):
            nonlocal quantidade_valor
            quantidade_valor += 1
            quantidade.current.value = str(quantidade_valor)
            page.update()

        def decrementar(e):
            nonlocal quantidade_valor
            if quantidade_valor > 0:
                quantidade_valor -= 1
            quantidade.current.value = str(quantidade_valor)
            page.update()

        # Conteúdo da janela flutuante
        page.dialog = ft.AlertDialog(
            title=ft.Text("Selecione o Produto"),
            content=ft.Column(
                [
                    ft.Dropdown(
                        ref=produto_selecionado,
                        options=[
                            ft.dropdown.Option("Sacola Ref. 38x48"),
                            ft.dropdown.Option("Sacola Ref. 34x44")
                        ],
                        value="Sacola Ref. 38x48",
                        label="Produto"
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton("-", on_click=decrementar),
                            ft.Text("0", ref=quantidade, size=16, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("+", on_click=incrementar)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ]
            ),
            actions=[
                ft.ElevatedButton("Adicionar", on_click=adicionar_produto),
                ft.ElevatedButton("Cancelar", on_click=lambda e: fechar_janela())
            ],
            on_dismiss=lambda e: None,
        )
        quantidade_valor = 0
        quantidade.current.value = str(quantidade_valor)
        page.dialog.open = True
        page.update()

    def fechar_janela():
        page.dialog.open = False
        page.update()

    # Função para atualizar a tabela
    def atualizar_tabela():
        tabela.rows.clear()
        total = 0
        for item in produtos_adicionados:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item[0])),
                        ft.DataCell(ft.Text(str(item[1]))),
                        ft.DataCell(ft.Text(item[2])),
                    ]
                )
            )
            # Soma os valores totais
            total += float(item[2].replace("R$", "").strip())
        total_geral.value = f"Total Geral: R$ {total:.2f}"
        page.update()

    # Função para gerar o relatório na tela
    def gerar_relatorio_na_tela(e):
        if not produtos_adicionados:
            page.snack_bar = ft.SnackBar(ft.Text("Não há produtos na lista para gerar o relatório!"))
            page.snack_bar.open = True
            page.update()
            return

        relatorio = "Relatório de Produtos:\n\n"
        for item in produtos_adicionados:
            relatorio += f"{item[0]} - Quantidade: {item[1]} - Preço Total: {item[2]}\n"
        relatorio += f"\n{total_geral.value}"
        page.dialog = ft.AlertDialog(
            title=ft.Text("Relatório Final"),
            content=ft.Text(relatorio),
            on_dismiss=lambda e: None,
        )
        page.dialog.open = True
        page.update()

    # Função para gerar o relatório em PDF
    def gerar_pdf(e):
        if not produtos_adicionados:
            page.snack_bar = ft.SnackBar(ft.Text("Não há produtos na lista para gerar o relatório!"))
            page.snack_bar.open = True
            page.update()
            return

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 10, txt="Relatório de Produtos - CooperPlast", ln=True, align="C")
        pdf.ln(10)

        # Conteúdo
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Produtos adicionados:", ln=True)
        pdf.ln(5)

        # Cabeçalho da tabela
        pdf.cell(80, 10, "Produto", border=1)
        pdf.cell(40, 10, "Quantidade", border=1)
        pdf.cell(40, 10, "Preço Total", border=1, ln=True)

        # Adicionando os produtos
        total = 0
        for item in produtos_adicionados:
            pdf.cell(80, 10, item[0], border=1)
            pdf.cell(40, 10, str(item[1]), border=1)
            pdf.cell(40, 10, item[2], border=1, ln=True)
            total += float(item[2].replace("R$", "").strip())

        # Total geral
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt=f"Total Geral: R$ {total:.2f}", ln=True)

        # Salvar o PDF
        pdf.output("relatorio_produtos.pdf")
        page.snack_bar = ft.SnackBar(ft.Text("Relatório PDF gerado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    # Exibição da lista de produtos
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Produto")),
            ft.DataColumn(ft.Text("Quantidade")),
            ft.DataColumn(ft.Text("Preço Total")),
        ],
        rows=[]
    )

    # Valor total
    total_geral = ft.Text(value="Valor Total: R$ 0.00", size=18, color="blue", weight=ft.FontWeight.BOLD)

    # Botões
    adicionar_btn = ft.ElevatedButton("Adicionar Produto", on_click=lambda e: abrir_selecao_produto())
    gerar_relatorio_tela_btn = ft.ElevatedButton("Gerar Relatório na Tela", on_click=gerar_relatorio_na_tela)
    gerar_pdf_btn = ft.ElevatedButton("Gerar Relatório em PDF", on_click=gerar_pdf)

    # Adicionando elementos à página
    page.add(
        ft.Text(
            "Calculadora de Pedidos",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        adicionar_btn,
        tabela,
        total_geral,
        ft.Row([gerar_relatorio_tela_btn, gerar_pdf_btn], alignment=ft.MainAxisAlignment.CENTER)
    
    # Função para gerar o relatório em PDF
    def gerar_pdf(e):
        if not produtos_adicionados:
            page.snack_bar = ft.SnackBar(ft.Text("Não há produtos na lista para gerar o relatório!"))
            page.snack_bar.open = True
            page.update()
            return

        cliente = nome_cliente.current.value or "Não informado"
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
    )

# Executar a aplicação
ft.app(target=main)
