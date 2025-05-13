/**
 * Função para criar um gráfico de linha
 * @param {string} elementId - ID do elemento canvas para renderizar o gráfico
 * @param {string} titulo - Título do gráfico 
 * @param {Array} labels - Array com os labels do eixo X
 * @param {Array} dados - Array com os valores numéricos
 * @param {string} corBorda - Cor da borda da linha (opcional)
 * @param {string} corFundo - Cor do preenchimento da área (opcional)
 */
function createLineChart(elementId, titulo, labels, dados, corBorda = 'rgba(40, 167, 69, 1)', corFundo = 'rgba(40, 167, 69, 0.1)') {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: titulo,
                data: dados,
                backgroundColor: corFundo,
                borderColor: corBorda,
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'R$ ' + context.raw.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Função para criar um gráfico de barras
 * @param {string} elementId - ID do elemento canvas para renderizar o gráfico
 * @param {string} titulo - Título do gráfico 
 * @param {Array} labels - Array com os labels do eixo X
 * @param {Array} dados - Array com os valores numéricos
 * @param {string} cor - Cor das barras (opcional)
 */
function createBarChart(elementId, titulo, labels, dados, cor = 'rgba(0, 123, 255, 0.7)') {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: titulo,
                data: dados,
                backgroundColor: cor,
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'R$ ' + context.raw.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Função para criar um gráfico de pizza
 * @param {string} elementId - ID do elemento canvas para renderizar o gráfico
 * @param {string} titulo - Título do gráfico 
 * @param {Array} labels - Array com os labels das fatias
 * @param {Array} dados - Array com os valores numéricos
 * @param {Array} cores - Array com as cores das fatias (opcional)
 */
function createPieChart(elementId, titulo, labels, dados, cores = null) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Cores padrão se não forem fornecidas
    if (!cores) {
        cores = [
            'rgba(40, 167, 69, 0.7)',
            'rgba(0, 123, 255, 0.7)',
            'rgba(23, 162, 184, 0.7)',
            'rgba(255, 193, 7, 0.7)',
            'rgba(108, 117, 125, 0.7)',
            'rgba(220, 53, 69, 0.7)',
            'rgba(111, 66, 193, 0.7)',
            'rgba(253, 126, 20, 0.7)'
        ];
    }
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: titulo,
                data: dados,
                backgroundColor: cores,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `R$ ${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Formatar a forma de pagamento para exibição
 * @param {string} formaPagamento - Forma de pagamento no formato armazenado no banco
 * @returns {string} - Forma de pagamento formatada para exibição
 */
function formatarFormaPagamento(formaPagamento) {
    switch(formaPagamento) {
        case 'dinheiro': return 'Dinheiro';
        case 'cartão_credito': return 'Cartão de Crédito';
        case 'cartão_debito': return 'Cartão de Débito';
        case 'pix': return 'PIX';
        default: return formaPagamento;
    }
}

/**
 * Formatar valor monetário para exibição em R$
 * @param {number} valor - Valor numérico
 * @returns {string} - Valor formatado como string monetária
 */
function formatarValorMonetario(valor) {
    return `R$ ${valor.toFixed(2)}`;
}
