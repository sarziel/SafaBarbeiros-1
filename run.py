import os
from app import create_app
from config import get_config

# Criar a aplicação Flask com a configuração apropriada
app = create_app(get_config())

if __name__ == '__main__':
    # Definir porta e host para a execução do servidor
    port = int(os.environ.get('PORT', 5000))
    
    # Executar a aplicação
    app.run(host='0.0.0.0', port=port, debug=True)
