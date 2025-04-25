#!/usr/bin/env python3
import os
import subprocess
import time
import shutil
import signal
from pathlib import Path
from datetime import datetime
from string import Template

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress
import time

import re
import random
from typing import Tuple

# Configuración
TMP_DIR = "/tmp/robocomp_test"
TIMEOUT = 3  # segundos

CDSL_TEMPLATE = """
// Component generated dynamically - ${timestamp}
${imports}

Component ${name}
{
    Communications
    {
        ${implements}
        ${requires}
        ${subscribesTo}
        ${publishes}
    };
    language ${language};
    ${gui}
    ${options}
};
"""


LANGUAGES = ("Cpp11", "python")
GUI = ("", "QWidget", "QDialog", "QMainWindow")
OPTIONS = ("", "dsr")

TESTS ={
    "void":{
        "imports": [],
        "implements": "",
        "requires": "",
        "subscribesTo": "",
        "publishes": "",
    },
    "hetereogeneous":{
        "imports": [f"CameraSimple.idsl", f"Lidar3D.idsl", "JoystickAdapter.idsl", "CameraRGBDSimpleYoloPub.idsl"],
        "implements": "implements Lidar3D;",
        "requires": "requires CameraSimple;",
        "subscribesTo": "subscribesTo JoystickAdapter;",
        "publishes": "publishes CameraRGBDSimpleYoloPub;",
    },
    "simpleAll":{
        "imports": [f"FullTest.idsl", f"FullTestPub.idsl"],
        "implements": "implements FullTest;",
        "requires": "requires FullTest;",
        "subscribesTo": "subscribesTo FullTestPub;",
        "publishes": "publishes FullTestPub;",
    },
    "MultipleAll":{
        "imports": ["FullTest.idsl", "FullTestPub.idsl"],
        "implements": "implements FullTest, FullTest, FullTest;",
        "requires": "requires FullTest, FullTest, FullTest;",
        "subscribesTo": "subscribesTo FullTestPub, FullTestPub, FullTestPub;",
        "publishes": "publishes FullTestPub, FullTestPub, FullTestPub;",
    },
    "recursiveImplementation":{
        "imports": ["RecursiveTest1.idsl", "RecursiveTestPub.idsl"],
        "implements": "implements RecursiveTest1;",
        "requires": "requires RecursiveTest1;",
        "subscribesTo": "subscribesTo RecursiveTestPub;",
        "publishes": "publishes RecursiveTestPub;",
    }
}




# Configuración de la interfaz
console = Console()
progress = Progress()
task_ids = {}

# Diccionario para mantener el estado de las pruebas
test_status = {}



def cleanup():
    """Limpiar directorio temporal"""
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    return True


def generate_cdsl_file(name, config, lang, gui, options, root_path):
    """
    Genera un archivo CDSL dinámicamente basado en configuración
    
    Args:
        config (dict): Configuración del componente con las siguientes claves:
            - imports: list of str (archivos .idsl a importar)
            - implements: list of str (interfaces implementadas)
            - requires: list of str (interfaces requeridas)
            - subscribesTo: list of str (interfaces de suscripción)
            - publishes: list of str (interfaces publicadas)
            - language: str (cpp/python)
            - gui: str/None (configuración de GUI)
            - options: list of str (opciones adicionales)
    """
    
    # Procesar imports
    imports = "\n".join([f'import "{imp}";' for imp in config.get("imports", [])])


    # Configuración de GUI
    if gui:
        gui = f"gui Qt({gui});"
    else:
        gui = "// No GUI configuration"

    if options:
        options = f"options {options};"
    else:
        options = "// No DSR configuration"
    
    # Construir el archivo CDSL
    cdsl_content = Template(CDSL_TEMPLATE).substitute(
        timestamp=datetime.now().isoformat(),
        name=name,
        imports=imports,
        implements=config.get("implements", ""),
        requires=config.get("requires", ""),
        subscribesTo=config.get("subscribesTo", ""),
        publishes=config.get("publishes", ""),
        language=lang,
        gui=gui,
        options=options,
    )


    os.makedirs(os.path.join(root_path, name), exist_ok=True)
    f = open(os.path.join(root_path, name, name+".cdsl"), "w")
    f.write(cdsl_content)
    f.close()

    return True

def generate_component(name, path):
    """Generar componente usando robocompdsl"""
    result = subprocess.run(["robocompdsl", name+".cdsl", ".",], capture_output=True, text=True, cwd=path)
    if result.returncode != 0:
        console.print(f"[red]Error al generar el componente {name}, return {result.returncode}:[/red]\n {result.stderr}")
        return False
    return True

def compile_component(name, path):
    result = subprocess.run(args=["cmake -B build && make -C build -j1"],shell=True, capture_output=True, cwd=path)
    if result.returncode != 0:
        console.print(f"[red]Error al compilar el componente {name}, return {result.returncode}:[/red]\n {result.stderr}")
        return False
    return True


def configure_component(config_path: str) -> bool:
    """
    Modifica puertos y prefixes en el texto de configuración.
    Devuelve el texto modificado y un diccionario con los cambios realizados.
    """

     # Leer el archivo original
    try:
        with open(config_path, 'r') as f:
            config_text = f.read()
    except Exception as e:
        return False
    
    puertos_usados = set()
    prefix_usados = set()

    def generar_puerto_unico(match):
        if "TopicManager" in match.string.split('\n')[match.string.count('\n', 0, match.start())]:
            return match.group(0)
        while True:
            puerto = random.randint(10000, 65535)
            if puerto not in puertos_usados:
                puertos_usados.add(puerto)
                return f"{match.group(1)}{puerto}{match.group(3)}"
    
    patron_puerto = re.compile(r'(-p\s+)(\d{1,5})(\b|$)')
    config_text = patron_puerto.sub(generar_puerto_unico, config_text)
    
    # Expresión regular para prefixes
    def reemplazar_prefix(match):
        while True:
            prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(1, 9)))
            if prefix not in prefix_usados:
                prefix_usados.add(prefix)
                return f"{match.group(1)}{match.group(2)}{prefix}{match.group(4)}"
    
    patron_prefix = re.compile(r'((PubPrefix|Prefix)\d*\s*=\s*["\']?)([a-zA-Z]?)(["\']?)', re.IGNORECASE)
    config_text = patron_prefix.sub(reemplazar_prefix, config_text)

    try:
        with open(config_path, 'w') as f:
            f.write(config_text)
    except Exception as e:
        return False
    
    return True

def test_component(name, path):
    # Iniciar el proceso (sin shell=True por seguridad)
    process = subprocess.Popen(
        [f"bin/{name}", "etc/config"],
        cwd=path,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Esperar el tiempo de timeout
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        if process.poll() is not None:  # El proceso terminó
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                console.print(f"[red]Error al ejecutar el componente {name}, return {process.returncode}:[/red]\n {stderr}")
            return False
        time.sleep(0.1)
    
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
    return True


def generate_test_status_table() -> Table:
    """Genera una tabla Rich con el estado actual de las pruebas."""
    table = Table(title="Estado de Pruebas")
    table.add_column("Prueba", style="cyan")
    table.add_column("Operación Actual", style="magenta")
    table.add_column("Estado", justify="right")
    table.add_column("Detalles", style="green")

    for test_name, status in test_status.items():
        # Determinar el ícono de estado
        if status['ok'] is None:
            state = "[yellow]⏳[/yellow] En progreso"
        elif status['ok']:
            state = "[green]✓[/green] Éxito"
        else:
            state = "[red]✗[/red] Fallo"
        
        table.add_row(
            test_name,
            status['current_operation'],
            state,
            status['details']
        )
    
    return table

def run_single_test(name: str, config: dict, lang: str, gui: str, option: str, update_callback: callable) -> bool:
    """Ejecuta una sola prueba y llama al callback para actualizar."""
    full_name = f"{name}_{lang}{f'_{gui}' if gui else ''}{f'_{option}' if option else ''}"
    
    def update_status(operation: str, details: str, ok: bool = None):
        test_status[full_name] = {
            'ok': ok,
            'current_operation': operation,
            'details': details
        }
        update_callback()
    
    try:
        # 1. Generar archivo CDSL
        update_status('Generando CDSL', 'Creando archivo de definición')
        ok = generate_cdsl_file(full_name, config, lang, gui, option, TMP_DIR)
        if not ok:
            update_status('Falló', 'Generación CDSL fallida', False)
            return False
        
        component_path = os.path.join(TMP_DIR, full_name)
        # 2. Generar componentes
        update_status('Generando componente', 'Ejecutando robocompdsl')
        ok = generate_component(full_name, component_path)
        if not ok:
            update_status('Falló', 'Generación componente fallida', False)
            return False
        
        # 3. Compilar componente
        update_status('Compilando', 'Compilando componente')
        ok = compile_component(full_name, component_path)
        if not ok:
            update_status('Falló', 'Compilación fallida', False)
            return False
        
        update_status('Configurando', 'Editando el config')
        ok = configure_component(os.path.join(component_path, "etc/config"))
        if not ok:
            update_status('Falló', 'Configuración fallida', False)
            return False
        
        # 4. Probar componente
        update_status('Ejecutando', 'Verificando funcionamiento')
        ok = test_component(full_name, component_path)
        update_status('Completado', 'Prueba exitosa' if ok else 'Prueba fallida', ok)
        return ok
        
    except Exception as e:
        update_status('Error', f'Excepción: {str(e)}', False)
        return False

def main():
    global test_status
    
    try:
        ROBOCOMP = os.environ['ROBOCOMP']
    except KeyError:
        console.print('[yellow]ROBOCOMP environment variable not set, using default value[/yellow]')
        ROBOCOMP = '/home/robocomp/robocomp'

    # Preparar entorno
    cleanup()
    os.makedirs(TMP_DIR, exist_ok=True)
    
    # Copiar archivos necesarios
    with console.status("[bold green]Copiando archivos de recursos..."):
        resource_dir = os.path.join(Path(__file__).parent.resolve(), "resources/generate_and_test_robocomp")
        for file in os.listdir(resource_dir):
            shutil.copy(
                os.path.join(resource_dir, file),
                os.path.join(ROBOCOMP, "interfaces/IDSLs", file)
            )

    # Inicializar estado de pruebas
    test_status = {}

    subprocess.run(args=["rcnode"], shell=True, capture_output=True)

    # Ejecutar pruebas en paralelo con visualización en tiempo real
    with Live(console=console, refresh_per_second=4) as live:
        def update_display():
            """Función para actualizar la visualización"""
            live.update(generate_test_status_table())
        
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = []
            
            # Enviar todas las pruebas al executor
            for name, config in TESTS.items():
                for lang in LANGUAGES:
                    for gui in GUI:
                        for option in OPTIONS:
                            future = executor.submit(
                                run_single_test,
                                name, config, lang, gui, option,
                                update_display  # Pasamos el callback
                            )
                            futures.append(future)
                            # Inicializar estado
                            full_name = f"{name}_{lang}{f'_{gui}' if gui else ''}{f'_{option}' if option else ''}"
                            test_status[full_name] = {
                                'ok': None,
                                'current_operation': 'En cola',
                                'details': 'Esperando para ejecutar'
                            }
                            update_display()
            
            # Esperar a que terminen todos los hilos
            for future in as_completed(futures):
                try:
                    future.result()  # Solo para capturar excepciones no manejadas
                except Exception as e:
                    console.print(f"[red]Error no manejado: {e}[/red]")
    
    # Estadísticas
    total = len(test_status)
    passed = sum(1 for status in test_status.values() if status['ok'])
    failed = total - passed
    
    console.print(f"\n[bold]Total:[/bold] {total}  [green]✓ Éxito:[/green] {passed}  [red]✗ Fallo:[/red] {failed}")
    
    # Limpieza (opcional, comentar para depuración)
    # cleanup()

if __name__ == "__main__":
    main()