"""
Start backend server with ML engine loaded
"""
import subprocess
import sys
import os

def start_server():
    print('🚀 Starting backend server with ML engine...')
    print('=' * 80)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print(f'📁 Working directory: {backend_dir}')
    print('🔄 Loading ML engine and starting uvicorn...')
    print('=' * 80)
    
    # Start uvicorn server
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'main:app',
            '--reload',
            '--host', '0.0.0.0',
            '--port', '8000'
        ], check=True)
    except KeyboardInterrupt:
        print('\n\n🛑 Server stopped by user')
    except Exception as e:
        print(f'\n❌ Error starting server: {e}')
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(start_server())
