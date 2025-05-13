/**
 * Arquivo JavaScript específico para funcionalidades das páginas do barbeiro
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar elementos de data e hora em formulários
    initDateTimeElements();
    
    // Inicializar elementos de calendário na agenda
    initCalendarNavigation();
});

/**
 * Inicializa elementos de data e hora em formulários
 */
function initDateTimeElements() {
    // Definir data mínima para hoje em inputs de data
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = yyyy + '-' + mm + '-' + dd;
    
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.hasAttribute('min')) {
            input.min = formattedDate;
        }
    });
}

/**
 * Inicializa funcionalidades de navegação de calendário na agenda
 */
function initCalendarNavigation() {
    const dataAgendaEl = document.getElementById('data-agenda');
    if (!dataAgendaEl) return;
    
    // Inicializar botões de navegação
    const btnAnterior = document.querySelector('button[onclick="navegarData(-1)"]');
    const btnHoje = document.querySelector('button[onclick="irParaHoje()"]');
    const btnProximo = document.querySelector('button[onclick="navegarData(1)"]');
    
    if (btnAnterior && btnHoje && btnProximo) {
        // Verificar se estamos na data de hoje para desabilitar o botão "Hoje"
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        
        const dataAtual = new Date(dataAgendaEl.value);
        dataAtual.setHours(0, 0, 0, 0);
        
        if (dataAtual.getTime() === hoje.getTime()) {
            btnHoje.disabled = true;
        }
    }
}

/**
 * Muda a data da agenda e navega para a URL correspondente
 * @param {string} data - Data no formato YYYY-MM-DD
 */
function mudarData(data) {
    window.location.href = `/barbeiro/agenda?data=${data}`;
}

/**
 * Navega para a data anterior ou próxima na agenda
 * @param {number} dias - Número de dias para navegar (positivo ou negativo)
 */
function navegarData(dias) {
    const dataAtual = document.getElementById('data-agenda').value;
    const data = new Date(dataAtual);
    data.setDate(data.getDate() + dias);
    
    const ano = data.getFullYear();
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const dia = String(data.getDate()).padStart(2, '0');
    
    mudarData(`${ano}-${mes}-${dia}`);
}

/**
 * Navega para a data de hoje na agenda
 */
function irParaHoje() {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    const dia = String(hoje.getDate()).padStart(2, '0');
    
    mudarData(`${ano}-${mes}-${dia}`);
}

/**
 * Alterna a visualização dos campos de data personalizados no relatório
 * @param {string} value - Valor selecionado do período
 */
function toggleCustomDates(value) {
    const customDateFields = document.querySelectorAll('.custom-dates');
    
    if (value === 'customizado') {
        customDateFields.forEach(field => field.style.display = 'block');
    } else {
        customDateFields.forEach(field => field.style.display = 'none');
    }
}
