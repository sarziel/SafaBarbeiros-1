/**
 * Arquivo JavaScript para o sistema PDV (Ponto de Venda)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Array para armazenar os itens do carrinho
    let carrinhoItens = [];
    
    // Elementos do DOM
    const btnFinalizar = document.getElementById('btn-finalizar');
    const btnLimpar = document.getElementById('btn-limpar');
    const formVenda = document.getElementById('form-venda');
    const tabelaItens = document.getElementById('tabela-itens');
    const valorTotalEl = document.getElementById('valor-total');
    const resumoTotalEl = document.getElementById('resumo-total');
    const formaPagamentoSelect = document.getElementById('forma-pagamento');
    const linhaVazia = document.getElementById('linha-vazia');
    
    // Botões para adicionar serviços
    const botoesAdicionarServico = document.querySelectorAll('.adicionar-servico');
    
    // Botões para selecionar agendamento
    const botoesAgendamento = document.querySelectorAll('.selecionar-agendamento');
    
    // Modal de confirmação
    const confirmarVendaModal = new bootstrap.Modal(document.getElementById('confirmarVendaModal'));
    const btnConfirmarVenda = document.getElementById('btn-confirmar-venda');
    
    // Modal de venda concluída
    const vendaConcluidaModal = new bootstrap.Modal(document.getElementById('vendaConcluidaModal'));
    
    // Verificar se há um agendamento_id na URL
    const urlParams = new URLSearchParams(window.location.search);
    const agendamentoIdUrl = urlParams.get('agendamento_id');
    
    if (agendamentoIdUrl) {
        // Encontrar o botão de agendamento correspondente e clicar nele
        botoesAgendamento.forEach(botao => {
            if (botao.getAttribute('data-agendamento-id') === agendamentoIdUrl) {
                botao.click();
            }
        });
    }
    
    // Event Listeners
    
    // Adicionar serviço ao carrinho
    botoesAdicionarServico.forEach(botao => {
        botao.addEventListener('click', function() {
            const servicoId = this.getAttribute('data-servico-id');
            const servicoNome = this.getAttribute('data-servico-nome');
            const servicoPreco = parseFloat(this.getAttribute('data-servico-preco'));
            
            adicionarItemCarrinho(servicoId, servicoNome, servicoPreco);
        });
    });
    
    // Selecionar agendamento
    botoesAgendamento.forEach(botao => {
        botao.addEventListener('click', function() {
            // Limpar o carrinho
            carrinhoItens = [];
            
            // Obter dados do agendamento
            const agendamentoId = this.getAttribute('data-agendamento-id');
            const servicoId = this.getAttribute('data-servico-id');
            const servicoNome = this.getAttribute('data-servico-nome');
            const servicoPreco = parseFloat(this.getAttribute('data-servico-preco'));
            
            // Definir o agendamento_id no formulário
            document.getElementById('agendamento-id').value = agendamentoId;
            
            // Adicionar o serviço ao carrinho
            adicionarItemCarrinho(servicoId, servicoNome, servicoPreco);
            
            // Destacar o botão selecionado
            botoesAgendamento.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Botão de limpar carrinho
    btnLimpar.addEventListener('click', function() {
        limparCarrinho();
    });
    
    // Botão de finalizar venda
    btnFinalizar.addEventListener('click', function() {
        const formaPagamento = formaPagamentoSelect.value;
        
        if (!formaPagamento) {
            alert('Por favor, selecione uma forma de pagamento.');
            return;
        }
        
        // Preencher o modal de confirmação
        preencherModalConfirmacao();
        
        // Exibir o modal
        confirmarVendaModal.show();
    });
    
    // Botão de confirmar venda no modal
    btnConfirmarVenda.addEventListener('click', function() {
        registrarVenda();
    });
    
    // Alteração na forma de pagamento
    formaPagamentoSelect.addEventListener('change', verificarFormulario);
    
    /**
     * Adiciona um item ao carrinho
     * @param {string} id - ID do serviço
     * @param {string} nome - Nome do serviço
     * @param {number} preco - Preço do serviço
     */
    function adicionarItemCarrinho(id, nome, preco) {
        // Verificar se o item já está no carrinho
        const itemExistente = carrinhoItens.find(item => item.servico_id === id);
        
        if (itemExistente) {
            // Incrementar a quantidade
            itemExistente.quantidade += 1;
            itemExistente.total = itemExistente.quantidade * itemExistente.preco - itemExistente.desconto;
        } else {
            // Adicionar novo item
            carrinhoItens.push({
                servico_id: id,
                nome: nome,
                preco: preco,
                quantidade: 1,
                desconto: 0,
                total: preco
            });
        }
        
        // Atualizar a interface
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Atualiza a exibição do carrinho
     */
    function atualizarCarrinho() {
        // Limpar a tabela (exceto cabeçalho e rodapé)
        const tbody = tabelaItens.querySelector('tbody');
        tbody.innerHTML = '';
        
        if (carrinhoItens.length === 0) {
            // Adicionar linha vazia
            tbody.innerHTML = `
                <tr id="linha-vazia">
                    <td colspan="6" class="text-center">
                        <i class="bi bi-cart-x text-muted"></i> Nenhum item adicionado
                    </td>
                </tr>
            `;
        } else {
            // Adicionar itens à tabela
            carrinhoItens.forEach((item, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.nome}</td>
                    <td>
                        <div class="input-group input-group-sm">
                            <button type="button" class="btn btn-outline-secondary btn-diminuir" data-index="${index}">-</button>
                            <input type="number" class="form-control text-center input-quantidade" value="${item.quantidade}" data-index="${index}" min="1">
                            <button type="button" class="btn btn-outline-secondary btn-aumentar" data-index="${index}">+</button>
                        </div>
                    </td>
                    <td>R$ ${item.preco.toFixed(2)}</td>
                    <td>
                        <input type="number" class="form-control form-control-sm input-desconto" value="${item.desconto.toFixed(2)}" data-index="${index}" min="0" step="0.01">
                    </td>
                    <td>R$ ${item.total.toFixed(2)}</td>
                    <td>
                        <button type="button" class="btn btn-sm btn-danger btn-remover" data-index="${index}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            
            // Adicionar event listeners aos botões e inputs
            tbody.querySelectorAll('.btn-diminuir').forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    diminuirQuantidade(index);
                });
            });
            
            tbody.querySelectorAll('.btn-aumentar').forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    aumentarQuantidade(index);
                });
            });
            
            tbody.querySelectorAll('.input-quantidade').forEach(input => {
                input.addEventListener('change', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    alterarQuantidade(index, parseInt(this.value));
                });
            });
            
            tbody.querySelectorAll('.input-desconto').forEach(input => {
                input.addEventListener('change', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    alterarDesconto(index, parseFloat(this.value));
                });
            });
            
            tbody.querySelectorAll('.btn-remover').forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    removerItem(index);
                });
            });
        }
        
        // Atualizar valor total
        const valorTotal = calcularValorTotal();
        valorTotalEl.textContent = `R$ ${valorTotal.toFixed(2)}`;
        resumoTotalEl.textContent = `R$ ${valorTotal.toFixed(2)}`;
    }
    
    /**
     * Diminui a quantidade de um item
     * @param {number} index - Índice do item no array
     */
    function diminuirQuantidade(index) {
        if (carrinhoItens[index].quantidade > 1) {
            carrinhoItens[index].quantidade -= 1;
            carrinhoItens[index].total = carrinhoItens[index].quantidade * carrinhoItens[index].preco - carrinhoItens[index].desconto;
            atualizarCarrinho();
            verificarFormulario();
        }
    }
    
    /**
     * Aumenta a quantidade de um item
     * @param {number} index - Índice do item no array
     */
    function aumentarQuantidade(index) {
        carrinhoItens[index].quantidade += 1;
        carrinhoItens[index].total = carrinhoItens[index].quantidade * carrinhoItens[index].preco - carrinhoItens[index].desconto;
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Altera a quantidade de um item
     * @param {number} index - Índice do item no array
     * @param {number} quantidade - Nova quantidade
     */
    function alterarQuantidade(index, quantidade) {
        if (quantidade < 1) quantidade = 1;
        carrinhoItens[index].quantidade = quantidade;
        carrinhoItens[index].total = carrinhoItens[index].quantidade * carrinhoItens[index].preco - carrinhoItens[index].desconto;
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Altera o desconto de um item
     * @param {number} index - Índice do item no array
     * @param {number} desconto - Novo valor de desconto
     */
    function alterarDesconto(index, desconto) {
        const valorMaximo = carrinhoItens[index].quantidade * carrinhoItens[index].preco;
        
        if (desconto < 0) desconto = 0;
        if (desconto > valorMaximo) desconto = valorMaximo;
        
        carrinhoItens[index].desconto = desconto;
        carrinhoItens[index].total = carrinhoItens[index].quantidade * carrinhoItens[index].preco - carrinhoItens[index].desconto;
        
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Remove um item do carrinho
     * @param {number} index - Índice do item no array
     */
    function removerItem(index) {
        carrinhoItens.splice(index, 1);
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Limpa todos os itens do carrinho
     */
    function limparCarrinho() {
        carrinhoItens = [];
        document.getElementById('agendamento-id').value = '';
        formaPagamentoSelect.value = '';
        document.getElementById('observacoes').value = '';
        
        // Remover seleção de agendamento
        botoesAgendamento.forEach(b => b.classList.remove('active'));
        
        atualizarCarrinho();
        verificarFormulario();
    }
    
    /**
     * Calcula o valor total da venda
     * @returns {number} - Valor total
     */
    function calcularValorTotal() {
        return carrinhoItens.reduce((total, item) => total + item.total, 0);
    }
    
    /**
     * Verifica se o formulário está pronto para envio
     */
    function verificarFormulario() {
        const temItens = carrinhoItens.length > 0;
        const temFormaPagamento = formaPagamentoSelect.value !== '';
        
        btnFinalizar.disabled = !(temItens && temFormaPagamento);
    }
    
    /**
     * Preenche o modal de confirmação da venda
     */
    function preencherModalConfirmacao() {
        const modalItensEl = document.getElementById('modal-itens');
        const modalTotalEl = document.getElementById('modal-total');
        const modalPagamentoEl = document.getElementById('modal-pagamento');
        
        // Preencher itens
        let itensHTML = '';
        carrinhoItens.forEach(item => {
            itensHTML += `
                <div class="d-flex justify-content-between">
                    <span>${item.nome} (${item.quantidade}x)</span>
                    <span>R$ ${item.total.toFixed(2)}</span>
                </div>
            `;
        });
        modalItensEl.innerHTML = itensHTML;
        
        // Preencher total
        modalTotalEl.textContent = `R$ ${calcularValorTotal().toFixed(2)}`;
        
        // Preencher forma de pagamento
        const formaPagamento = formaPagamentoSelect.value;
        let formaPagamentoText = '';
        
        switch(formaPagamento) {
            case 'dinheiro': formaPagamentoText = 'Dinheiro'; break;
            case 'cartão_credito': formaPagamentoText = 'Cartão de Crédito'; break;
            case 'cartão_debito': formaPagamentoText = 'Cartão de Débito'; break;
            case 'pix': formaPagamentoText = 'PIX'; break;
            default: formaPagamentoText = formaPagamento;
        }
        
        modalPagamentoEl.textContent = formaPagamentoText;
    }
    
    /**
     * Registra a venda no servidor
     */
    function registrarVenda() {
        // Preparar dados da venda
        const dadosVenda = {
            agendamento_id: document.getElementById('agendamento-id').value || null,
            forma_pagamento: formaPagamentoSelect.value,
            observacoes: document.getElementById('observacoes').value,
            itens: carrinhoItens.map(item => ({
                servico_id: item.servico_id,
                quantidade: item.quantidade,
                preco: item.preco,
                desconto: item.desconto
            }))
        };
        
        // Enviar dados ao servidor
        fetch('/barbeiro/registrar-venda', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosVenda)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Fechar modal de confirmação
                confirmarVendaModal.hide();
                
                // Preencher modal de sucesso
                document.getElementById('sucesso-total').textContent = `R$ ${calcularValorTotal().toFixed(2)}`;
                
                const formaPagamento = formaPagamentoSelect.value;
                let formaPagamentoText = '';
                
                switch(formaPagamento) {
                    case 'dinheiro': formaPagamentoText = 'Dinheiro'; break;
                    case 'cartão_credito': formaPagamentoText = 'Cartão de Crédito'; break;
                    case 'cartão_debito': formaPagamentoText = 'Cartão de Débito'; break;
                    case 'pix': formaPagamentoText = 'PIX'; break;
                    default: formaPagamentoText = formaPagamento;
                }
                
                document.getElementById('sucesso-pagamento').textContent = formaPagamentoText;
                
                // Exibir modal de sucesso
                vendaConcluidaModal.show();
                
                // Limpar o carrinho
                limparCarrinho();
                
                // Remover o agendamento da lista se foi concluído
                if (dadosVenda.agendamento_id) {
                    const agendamentoEl = document.querySelector(`.selecionar-agendamento[data-agendamento-id="${dadosVenda.agendamento_id}"]`);
                    if (agendamentoEl) {
                        agendamentoEl.remove();
                    }
                }
            } else {
                alert('Erro ao registrar venda: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro ao registrar venda:', error);
            alert('Erro ao processar a venda. Por favor, tente novamente.');
        });
    }
});
