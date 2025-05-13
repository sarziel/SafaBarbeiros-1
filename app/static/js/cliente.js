/**
 * Arquivo JavaScript específico para funcionalidades das páginas do cliente
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar elementos de data e hora em formulários
    initDateTimeElements();
    
    // Configurar a busca de serviços ao selecionar barbeiro
    setupServicosBarbeiroFetch();
    
    // Configurar a busca de horários ao selecionar serviço e data
    setupHorariosDisponiveis();
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
    
    // Definir data máxima para 30 dias depois
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30);
    const maxYyyy = maxDate.getFullYear();
    const maxMm = String(maxDate.getMonth() + 1).padStart(2, '0');
    const maxDd = String(maxDate.getDate()).padStart(2, '0');
    const formattedMaxDate = maxYyyy + '-' + maxMm + '-' + maxDd;
    
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.hasAttribute('min')) {
            input.min = formattedDate;
        }
        if (!input.hasAttribute('max')) {
            input.max = formattedMaxDate;
        }
    });
}

/**
 * Configura o evento de busca de serviços ao selecionar um barbeiro
 */
function setupServicosBarbeiroFetch() {
    const barbeiroSelect = document.getElementById('barbeiro_id');
    if (!barbeiroSelect) return;
    
    const servicoSelect = document.getElementById('servico_id');
    const servicosDiv = document.getElementById('servicosDiv');
    const horariosDiv = document.getElementById('horariosDiv');
    
    barbeiroSelect.addEventListener('change', function() {
        if (this.value) {
            // Buscar serviços do barbeiro
            fetch(`/agendamento/servicos-barbeiro/${this.value}`)
                .then(response => response.json())
                .then(data => {
                    servicoSelect.innerHTML = '<option value="">Selecione um serviço</option>';
                    
                    if (data.servicos && data.servicos.length > 0) {
                        data.servicos.forEach(servico => {
                            const option = document.createElement('option');
                            option.value = servico.id;
                            option.textContent = `${servico.nome} - R$ ${servico.preco.toFixed(2)}`;
                            servicoSelect.appendChild(option);
                        });
                        servicosDiv.style.display = 'block';
                    } else {
                        servicosDiv.style.display = 'none';
                    }
                    
                    // Limpar horários
                    document.getElementById('hora').innerHTML = '<option value="">Selecione um horário</option>';
                    horariosDiv.style.display = 'none';
                })
                .catch(error => console.error('Erro ao buscar serviços:', error));
        } else {
            servicosDiv.style.display = 'none';
            horariosDiv.style.display = 'none';
        }
    });
}

/**
 * Configura o evento de busca de horários disponíveis ao selecionar serviço e data
 */
function setupHorariosDisponiveis() {
    const servicoSelect = document.getElementById('servico_id');
    const dataInput = document.getElementById('data');
    const barbeiroSelect = document.getElementById('barbeiro_id');
    
    if (!servicoSelect || !dataInput || !barbeiroSelect) return;
    
    const horaSelect = document.getElementById('hora');
    const horariosDiv = document.getElementById('horariosDiv');
    
    // Função para buscar horários disponíveis
    function fetchHorariosDisponiveis() {
        const barbeiro = barbeiroSelect.value;
        const servico = servicoSelect.value;
        const data = dataInput.value;
        
        if (barbeiro && servico && data) {
            // Buscar horários disponíveis
            fetch(`/agendamento/horarios-disponiveis?barbeiro_id=${barbeiro}&servico_id=${servico}&data=${data}`)
                .then(response => response.json())
                .then(data => {
                    horaSelect.innerHTML = '<option value="">Selecione um horário</option>';
                    
                    if (data.horarios && data.horarios.length > 0) {
                        data.horarios.forEach(horario => {
                            const option = document.createElement('option');
                            option.value = horario;
                            option.textContent = horario;
                            horaSelect.appendChild(option);
                        });
                        horariosDiv.style.display = 'block';
                    } else {
                        horaSelect.innerHTML = '<option value="">Sem horários disponíveis</option>';
                        horariosDiv.style.display = 'block';
                    }
                })
                .catch(error => console.error('Erro ao buscar horários:', error));
        }
    }
    
    // Adicionar event listeners
    servicoSelect.addEventListener('change', fetchHorariosDisponiveis);
    dataInput.addEventListener('change', fetchHorariosDisponiveis);
}
