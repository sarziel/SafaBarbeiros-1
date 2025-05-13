import os
import logging
from run import app

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    # Definir porta para execução do servidor
    port = int(os.environ.get('PORT', 5000))
    
    # Executar a aplicação
    app.run(host='0.0.0.0', port=port, debug=True)
