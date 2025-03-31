#!/usr/bin/env python3
import os
import shutil
import zipfile
import datetime
import re
from pathlib import Path

def crear_copia_seguridad(directorio):
    """Crea una copia de seguridad comprimida del directorio completo"""
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_zip = f"{directorio.split("/")[0]}_{fecha}.zip"
    
    print(f"Creando copia de seguridad: {nombre_zip}")
    
    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directorio):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=directorio)
                zipf.write(file_path, arcname)
    
    return nombre_zip

def limpiar_directorio_src(directorio):
    """Elimina archivos obsoletos y duplicados en src/"""
    src_dir = os.path.join(directorio, "src")
    if not os.path.exists(src_dir):
        print(f"Advertencia: No se encontró el directorio src/ en {directorio}")
        return

    # Archivos que deben permanecer en src/
    archivos_a_conservar = {
        "specificworker.h",
        "specificworker.cpp",
        "CMakeListsSpecific.txt",
        "CMakeLists.txt",
        "mainUI.ui",
        "README.md"
    }

    # Archivos generados que podrían estar duplicados
    archivos_generados = {
        "genericworker.h", "genericworker.cpp",
        "commonbehaviorI.h", "commonbehaviorI.cpp",
        "genericmonitor.h", "genericmonitor.cpp",
        "specificmonitor.h", "specificmonitor.cpp",
        "main.cpp", "config.h",
    }

    print("\nLimpiando directorio src/:")
    
    # Eliminar archivos obsoletos/duplicados
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        
        # Eliminar archivos generados que no deberían estar en src/
        if item in archivos_generados and item not in archivos_a_conservar:
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Eliminado: src/{item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Eliminado directorio: src/{item}")

    # Verificar si hay archivos duplicados entre src/ y generated/
    generated_dir = os.path.join(directorio, "generated")
    if os.path.exists(generated_dir):
        for item in os.listdir(generated_dir):
            src_item_path = os.path.join(src_dir, item)
            if os.path.exists(src_item_path) and item not in archivos_a_conservar:
                print(f"Advertencia: Archivo duplicado {item} encontrado en src/ y generated/")
                # Opcional: descomentar para eliminar automáticamente los duplicados en src/
                os.remove(src_item_path)
                print(f"Eliminado duplicado: src/{item}")

def actualizar_cmake_src(directorio):
    """Actualiza el CMakeLists.txt en src combinando el nuevo formato con las configuraciones específicas"""
    src_dir = os.path.join(directorio, "src")
    cmake_new_path = os.path.join(src_dir, "CMakeLists.txt.new")
    cmake_specific_path = os.path.join(src_dir, "CMakeListsSpecific.txt")
    cmake_final_path = os.path.join(src_dir, "CMakeLists.txt")

    # Plantilla base ordenada como se desea
    template = """# Sources set
LIST(APPEND SOURCES
{sources}
)

# Headers set
LIST(APPEND HEADERS
{headers}
)



{others}

"""

    # Valores por defecto (fuentes básicas)
    sources = ["  ../src/specificworker.cpp"]
    headers = ["  ../src/specificworker.h"]
    others = []


    # Leer configuraciones específicas si existen
    if os.path.exists(cmake_specific_path):
        with open(cmake_specific_path, 'r') as f:
            specific_content = f.read()

        # Procesar contenido específico
        reading_sources = False
        reading_headers = False

        for line in specific_content.split('\n'):
            line = line.strip()
            
            # Detectar secciones
            if "SET ( SOURCES" in line or "SET(SOURCES" in line:
                reading_sources = True
                reading_headers = False
                continue
            elif "SET ( HEADERS" in line or "SET(HEADERS" in line:
                reading_sources = False
                reading_headers = True
                continue
            elif line.endswith(")") and (reading_sources or reading_headers):
                reading_sources = False
                reading_headers = False
                continue
                
            # Procesar líneas según la sección
            if reading_sources and line and not line.startswith("#"):
                if "specificmonitor.cpp" not in line:  # Filtrar monitors
                    sources.append(f"  ../src/{line.strip()}")
            elif reading_headers and line and not line.startswith("#"):
                if "specificmonitor.h" not in line:  # Filtrar monitors
                    headers.append(f"  ../src/{line.strip()}")
            else:
                others.append(line)

    # Eliminar duplicados en sources y headers
    sources = list(dict.fromkeys(sources))
    headers = list(dict.fromkeys(headers))

    # Construir contenido final
    final_content = template.format(
        sources="\n".join(sources),
        headers="\n".join(headers),
        others= "\n".join(others),
    )

    # Eliminar líneas vacías excesivas
    final_content = "\n".join([line for line in final_content.split("\n") if line.strip() or line.startswith("#")])

    # Escribir archivo final
    with open(cmake_final_path, 'w') as f:
        f.write(final_content)

    # Eliminar archivos temporales
    # for temp_file in [cmake_new_path, cmake_specific_path]:
    #     if os.path.exists(temp_file):
    #         os.remove(temp_file)

    print(f"Archivo CMakeLists.txt actualizado correctamente en {cmake_final_path}")

def actualizar_cmake_src_advanced(directorio):
    """Actualiza el CMakeLists.txt en src combinando el nuevo formato con las configuraciones específicas"""
    src_dir = os.path.join(directorio, "src")
    cmake_new_path = os.path.join(src_dir, "CMakeLists.txt.new")
    cmake_specific_path = os.path.join(src_dir, "CMakeListsSpecific.txt")
    cmake_final_path = os.path.join(src_dir, "CMakeLists.txt")

    # Plantilla base ordenada como se desea
    template = """# Sources set
LIST(APPEND SOURCES
{sources}
)

# Headers set
LIST(APPEND HEADERS
{headers}
)

{includes}

{definitions}

{find_packages}

{libs}
"""

    # Valores por defecto (fuentes básicas)
    sources = ["  ../src/specificworker.cpp"]
    headers = ["  ../src/specificworker.h"]
    includes = ""
    definitions = "add_definitions(-fmax-errors=1 -fno-char8_t)"
    find_packages = ""
    libs = "LIST(APPEND LIBS ${{LIBS}})"

    # Leer configuraciones específicas si existen
    if os.path.exists(cmake_specific_path):
        with open(cmake_specific_path, 'r') as f:
            specific_content = f.read()

        # Procesar contenido específico
        specific_includes = []
        specific_definitions = []
        specific_find_packages = []
        specific_libs = []
        reading_sources = False
        reading_headers = False

        for line in specific_content.split('\n'):
            line = line.strip()
            
            # Detectar secciones
            if "SET ( SOURCES" in line or "SET(SOURCES" in line:
                reading_sources = True
                reading_headers = False
                continue
            elif "SET ( HEADERS" in line or "SET(HEADERS" in line:
                reading_sources = False
                reading_headers = True
                continue
            elif line.endswith(")") and (reading_sources or reading_headers):
                reading_sources = False
                reading_headers = False
                continue
                
            # Procesar líneas según la sección
            if reading_sources and line and not line.startswith("#"):
                if "specificmonitor.cpp" not in line:  # Filtrar monitors
                    sources.append(f"  ../src/{line.strip()}")
            elif reading_headers and line and not line.startswith("#"):
                if "specificmonitor.h" not in line:  # Filtrar monitors
                    headers.append(f"  ../src/{line.strip()}")
            elif "INCLUDE(" in line:
                specific_includes.append(line)
            elif "find_package(" in line:
                specific_find_packages.append(line)
            elif "include_directories(" in line:
                specific_find_packages.append(line)
            elif "SET (LIBS" in line or "SET(LIBS" in line:
                libs_content = line.replace("SET (LIBS", "").replace("SET(LIBS", "").replace(")", "").strip()
                specific_libs = libs_content.split()
            elif "add_definitions(" in line:
                specific_definitions.append(line)
        
        # Construir secciones
        if specific_includes:
            includes = "\n".join(specific_includes) + "\n"
        
        if specific_find_packages:
            find_packages = "\n".join(specific_find_packages) + "\n"
        
        if specific_definitions:
            # Combinar definiciones manteniendo las más restrictivas
            definitions = "\n".join(specific_definitions) + "\n"
        
        if specific_libs:
            libs = f"LIST(APPEND LIBS ${{LIBS}} {' '.join(specific_libs)})\n"

    # Eliminar duplicados en sources y headers
    sources = list(dict.fromkeys(sources))
    headers = list(dict.fromkeys(headers))

    # Construir contenido final
    final_content = template.format(
        sources="\n".join(sources),
        headers="\n".join(headers),
        includes=includes,
        definitions=definitions,
        find_packages=find_packages,
        libs=libs
    )

    # Eliminar líneas vacías excesivas
    final_content = "\n".join([line for line in final_content.split("\n") if line.strip() or line.startswith("#")])

    # Escribir archivo final
    with open(cmake_final_path, 'w') as f:
        f.write(final_content)

    # Eliminar archivos temporales

    if os.path.exists(cmake_specific_path):
        os.remove(cmake_specific_path)

    print(f"Archivo CMakeLists.txt actualizado correctamente en {cmake_final_path}")

def verificar_estructura(directorio):
    """Verifica que la estructura final sea correcta"""
    print("\nVerificando estructura final:")
    
    # Directorios requeridos
    required_dirs = ['src', 'generated', 'etc']
    for dir_name in required_dirs:
        dir_path = os.path.join(directorio, dir_name)
        if not os.path.exists(dir_path):
            print(f"Advertencia: Falta directorio {dir_name}/")

    # Archivos requeridos en src/
    src_files = ['specificworker.h', 'specificworker.cpp', 'CMakeLists.txt']
    for file_name in src_files:
        file_path = os.path.join(directorio, 'src', file_name)
        if not os.path.exists(file_path):
            print(f"Advertencia: Falta archivo src/{file_name}")

    # Archivos en generated/
    generated_files = ['genericworker.h', 'genericworker.cpp', 'main.cpp']
    generated_dir = os.path.join(directorio, 'generated')
    if os.path.exists(generated_dir):
        for file_name in generated_files:
            file_path = os.path.join(generated_dir, file_name)
            if not os.path.exists(file_path):
                print(f"Advertencia: Falta archivo generated/{file_name}")
    else:
        print("Advertencia: No se encontró el directorio generated/")

def estandarizar_tipos(contenido):
    tipos_std = [
        'string', 'vector', 'optional', 'shared_ptr', 'unique_ptr', 'weak_ptr',
        'tuple', 'map', 'unordered_map', 'unordered_set',
        'list', 'array', 'deque', 'queue', 'stack', 'pair', 'variant',
        'bitset', 'chrono', 'complex', 'filesystem', 'mutex',
        'regex', 'atomic', 'cout', 'cerr', 'cin', 'endl', 'flush'
    ]
    patron = r'(?<!std::)(?<!\.)(?<!cv::)(?<!#include <)(?<![\w:])\b(' + '|'.join(tipos_std) + r')\b(?!\s*::)'
    return re.sub(patron, r'std::\1', contenido)

def actualizar_specificworker_h(directorio):
    """Actualiza el archivo specificworker.h con los nuevos requerimientos"""
    src_dir = os.path.join(directorio, "src")
    h_path = os.path.join(src_dir, "specificworker.h")
    
    if not os.path.exists(h_path):
        print(f"Error: No se encontró {h_path}")
        return

    with open(h_path, 'r') as f:
        contenido = f.read()


    contenido = estandarizar_tipos(contenido)
    

    # 1. Añadir HIBERNATION_ENABLED después de los otros defines
    if "#define HIBERNATION_ENABLED" not in contenido:
        contenido = contenido.replace(
            "#define SPECIFICWORKER_H",
            "#define SPECIFICWORKER_H\n\n// If you want reduce compute period automaticaly for lack of use\n#define HIBERNATION_ENABLED"
        )

    # 2. Actualizar la firma del constructor
    contenido = re.sub(
        r'SpecificWorker\(TuplePrx tprx, bool startup_check\)',
        'SpecificWorker(const ConfigLoader& configLoader, TuplePrx tprx, bool startup_check)',
        contenido
    )

    # 3. Reemplazar setParams por los nuevos estados y añadir documentación
    # Primero eliminamos setParams
    contenido = re.sub(
        r'^\s*(#include <innermodel/innermodel.h>|void initialize\(int period\)|bool setParams\(RoboCompCommonBehavior::ParameterList params\));\s*$\n', 
        '', 
        contenido, 
        flags=re.MULTILINE
    )
    # DSR AGENT
    # Eliminar cada declaración individualmente permitiendo espacios y comentarios
    declaraciones = [
        r'std::shared_ptr<DSR::DSRGraph>\s*G\s*;',
        r'std::string\s+agent_name\s*;',
        r'int\s+agent_id\s*;',
        r'bool\s+(tree|graph|qscene_2d|osg_3d)_view\s*;',
        r'std::unique_ptr<DSR::DSRViewer>\s+graph_viewer\s*;',
        r'QHBoxLayout\s+mainLayout\s*;'
    ]

    for decl in declaraciones:
        contenido = re.sub(
            fr'^\s*{decl}\s*(//.*)?$\n',
            '',
            contenido,
            flags=re.MULTILINE
        )
    # Luego añadimos los nuevos estados con documentación
    nuevos_estados = """
        /**
         * \\brief Initializes the worker one time.
         */
        void initialize();

        /**
         * \\brief Main compute loop of the worker.
         */
        void compute();

        /**
         * \\brief Handles the emergency state loop.
         */
        void emergency();

        /**
         * \\brief Restores the component from an emergency state.
         */
        void restore();
"""
        # Si no encontramos el marcador, añadimos al final de los métodos públicos

    if not "void emergency();" in contenido:
        contenido = re.sub(
            r'^\s*void compute\(\s*\);\s*$\n', 
            '', 
            contenido, 
            flags=re.MULTILINE
            )
        contenido = contenido.replace(
            "public slots:",
            "public slots:" + nuevos_estados
        )

    # # 4. Añadir documentación de la clase
    # if "class SpecificWorker : public GenericWorker" in contenido and not "\\brief Class SpecificWorker" in contenido:
    #     contenido = contenido.replace(
    #         "class SpecificWorker : public GenericWorker",
    #         "/**\n * \\brief Class SpecificWorker implements the core functionality of the component.\n */\nclass SpecificWorker : public GenericWorker"
    #     )

    # # 5. Añadir documentación al constructor y destructor
    # if "class SpecificWorker : public GenericWorker" in contenido and not "\\brief Class SpecificWorker" in contenido:
    #     contenido = contenido.replace(
    #         "class SpecificWorker : public GenericWorker",
    #         r"/**" + "\n * \\brief Class SpecificWorker implements the core functionality of the component.\n */\nclass SpecificWorker : public GenericWorker"
    #     )

    # # 5. Añadir documentación al constructor y destructor
    # contenido = re.sub(
    #     r'SpecificWorker\([^)]*\);',
    #     r'/**' + '\n         * \\brief Constructor for SpecificWorker.\n         * \\param configLoader Configuration loader for the component.\n         * \\param tprx Tuple of proxies required for the component.\n         * \\param startup_check Indicates whether to perform startup checks.\n         */\n        SpecificWorker(const ConfigLoader& configLoader, TuplePrx tprx, bool startup_check);',
    #     contenido
    # )

    # contenido = re.sub(
    #     r'~SpecificWorker\(\);',
    #     r'/**' + '\n         * \\brief Destructor for SpecificWorker.\n         */\n        ~SpecificWorker();',
    #     contenido
    # )

    # # 6. Añadir documentación a startup_check
    # contenido = re.sub(
    #     r'int startup_check\(\);',
    #     r'/**' + '\n         * \\brief Performs startup checks for the component.\n         * \\return An integer representing the result of the checks.\n         */\n        int startup_check();',
    #     contenido
    # )

    # 7. Añadir sección de signals si no existe
    if "signals:" not in contenido:
        contenido = contenido.replace(
            "};\n\n#endif",
            "\nsignals:\n        //void customSignal();\n};\n\n#endif"
        )

    # Escribir el archivo actualizado
    with open(h_path, 'w') as f:
        f.write(contenido)

    print(f"Archivo specificworker.h actualizado correctamente en {h_path}")

def limpiar_residuales(contenido, max_line=2):
    """
    Elimina residuales manteniendo máximo 2 líneas vacías
    1. Elimina 'this->' sin miembro
    2. Elimina puntos y coma sueltos
    3. Normaliza líneas vacías (máx 2 consecutivas)
    """
    # Paso 1: Eliminar this-> sin miembro
    contenido = re.sub(r'this->(?![\w])', '', contenido)
    
    # Paso 2: Eliminar ; sueltos en líneas
    contenido = re.sub(r'^\s*;\s*$', '', contenido, flags=re.MULTILINE)
    
    # Paso 3: Normalizar líneas vacías (máx 2 consecutivas)
    lineas = []
    vacias_consecutivas = 0
    for linea in contenido.split('\n'):
        if not linea.strip():  # Si es línea vacía
            vacias_consecutivas += 1
            if vacias_consecutivas <= max_line:
                lineas.append(linea)
        else:
            vacias_consecutivas = 0
            lineas.append(linea)
    
    return '\n'.join(lineas)

def actualizar_specificworker_cpp(directorio):
    """Actualiza el archivo specificworker.cpp según las directrices de la nueva versión"""
    src_dir = os.path.join(directorio, "src")
    cpp_path = os.path.join(src_dir, "specificworker.cpp")
    path_DSR = ""
    
    if not os.path.exists(cpp_path):
        print(f"Error: No se encontró {cpp_path}")
        return

    with open(cpp_path, 'r') as f:
        contenido = f.read()


    contenido = estandarizar_tipos(contenido)


    contenido = re.sub(
        r'^\s*(agent_name\s*=\s*params\.at\("agent_name"\)\.value\s*;|'
        r'agent_id\s*=\s*stoi\(\s*params\.at\("agent_id"\)\.value\s*\)\s*;|'
        r'(tree|graph|qscene_2d|osg_3d)_view\s*=\s*params\.at\("(tree|graph|2d|3d)_view"\)\.value\s*==\s*"true"\s*;)\s*'
        r'(\s*//.*?)?$\n?', 
        '', 
        contenido, 
        flags=re.MULTILINE
    )
    
    contenido = re.sub(
        r'\s*using opts = DSR::DSRViewer::view;.*?setWindowTitle\(QString::fromStdString\(agent_name \+ "-"\) \+ QString::number\(agent_id\)\);\s*',
        '',
        contenido,
        flags=re.DOTALL
    )

    contenido = re.sub(
        r'^\s*auto grid_nodes = G->get_nodes_by_type\("grid"\);\n'
        r'\s*for \(auto grid : grid_nodes\)\n'
        r'\s*G->delete_node\(grid\);\n'
        r'\s*G\.reset\(\);\s*$',
        '',
        contenido,
        flags=re.MULTILINE
    )
	
		
    match = re.search(
        r'G = std::make_shared<DSR::DSRGraph>\([^)]*,\s*"([^"]*)"\s*\)[^;]*;',
        contenido
    )
    if match:
        path_DSR = match.group(1)
        print(path_DSR)
        # Eliminar la línea completa
        contenido = re.sub(
            r'G = std::make_shared<DSR::DSRGraph>\([^)]*,\s*"([^"]*)"\s*\)[^;]*;',
            '',
            contenido,
            flags=re.DOTALL
        )
		
    contenido = re.sub(
        r'opts::',
        'DSR::DSRViewer::view::',
        contenido,
        flags=re.DOTALL
    )
		


    # 1. Refactorizar completamente el constructor
    constructor_nuevo = """SpecificWorker::SpecificWorker(const ConfigLoader& configLoader, TuplePrx tprx, bool startup_check) : GenericWorker(configLoader, tprx)
{
this->startup_check_flag = startup_check;
	if(this->startup_check_flag)
	{
		this->startup_check();
	}
	else
	{
		#ifdef HIBERNATION_ENABLED
			hibernationChecker.start(500);
		#endif

		
		// Example statemachine:
		/***
		//Your definition for the statesmachine (if you dont want use a execute function, use nullptr)
		states["CustomState"] = std::make_unique<GRAFCETStep>("CustomState", period, 
															std::bind(&SpecificWorker::customLoop, this),  // Cyclic function
															std::bind(&SpecificWorker::customEnter, this), // On-enter function
															std::bind(&SpecificWorker::customExit, this)); // On-exit function

		//Add your definition of transitions (addTransition(originOfSignal, signal, dstState))
		states["CustomState"]->addTransition(states["CustomState"].get(), SIGNAL(entered()), states["OtherState"].get());
		states["Compute"]->addTransition(this, SIGNAL(customSignal()), states["CustomState"].get()); //Define your signal in the .h file under the "Signals" section.

		//Add your custom state
		statemachine.addState(states["CustomState"].get());
		***/

		statemachine.setChildMode(QState::ExclusiveStates);
		statemachine.start();

		auto error = statemachine.errorString();
		if (error.length() > 0){
			qWarning() << error;
			throw error;
		}
		
	}
}"""
    contenido = re.sub(
        r'SpecificWorker::SpecificWorker\([^)]*\)\s*:[^\{]*\{[\s\S]*?\n\}',
        constructor_nuevo,
        contenido
    )

    # 2. Mover lógica de setParams a initialize
    # Extraer contenido de setParams si existe
    setparams_match = re.search(
        r'bool SpecificWorker::setParams\([^)]*\)\s*\{([\s\S]*?)\}',
        contenido
    )
    
    if setparams_match:
        params_content = setparams_match.group(1)
        
        # Función para balancear llaves y obtener el contenido completo
        def extract_balanced_content(text):
            balance = 1
            result = []
            for char in text:
                if char == '{':
                    balance += 1
                elif char == '}':
                    balance -= 1
                    if balance == 0:
                        break
                result.append(char)
            return ''.join(result)
        
        # Extraer contenido completo balanceando llaves
        full_match = re.search(
            r'bool SpecificWorker::setParams\([^)]*\)\s*\{([\s\S]*)\n\}',
            contenido
        )
        if full_match:
            params_content = extract_balanced_content(full_match.group(1))
            
        # Convertir parámetros al nuevo formato ConfigLoader
        params_content = re.sub(
            r'std::stoi\(params\["(.*?)"\].value\)',
            r'this->configLoader.get<int>("\1")',
            params_content
        )
        params_content = re.sub(
            r'std::stoi\(params\.at\("(.*?)"\)\.value\)',
            r'this->configLoader.get<int>("\1")',
            params_content
        )

        params_content = re.sub(
            r'std::stof\(params\["(.*?)"\].value\)',
            r'this->configLoader.get<double>("\1")',
            params_content
        )
        params_content = re.sub(
            r'std::stof\(params\.at\("(.*?)"\)\.value\)',
            r'this->configLoader.get<double>("\1")',
            params_content
        )

        # Luego las comparaciones con "true"
        params_content = re.sub(
            r'params\["(.*?)"\].value == "(true|True)"',
            r'this->configLoader.get<bool>("\1")',
            params_content
        )
        params_content = re.sub(
            r'params\.at\("(.*?)"\)\.value == "(true|True)"',
            r'this->configLoader.get<bool>("\1")',
            params_content
        )

        contenido = re.sub(
            r'(this->configLoader\.get<bool>\("[^"]+"\))(?:\s+or\s+\1\s*);',
            r'\1;',
            contenido
        )

        # Finalmente los casos generales (sin conversión)
        params_content = re.sub(
            r'params\["(.*?)"\].value',
            r'this->configLoader.get<std::string>("\1")',
            params_content
        )
        params_content = re.sub(
            r'params\.at\("(.*?)"\)\.value',
            r'this->configLoader.get<std::string>("\1")',
            params_content
        )
        # Eliminar el último return (y cualquier línea vacía después)
        params_content = re.sub(r'\n\s*return\s+\w+\s*;\s*(\n\s*)?$', '', params_content.strip())

        # Crear nuevo initialize con la lógica convertida
        initialize_impl = f"""
void SpecificWorker::initialize()
{"{"}
{params_content}

//chekpoint robocompUpdater
"""
        
        # Insertar la nueva implementación de initialize
        contenido = re.sub(
            r'void SpecificWorker::initialize\([^)]*\)\s*\{[\s\S]*?\n',
            initialize_impl,
            contenido
        )
        #TODO
        # contenido = re.sub(
        #     r'//chekpoint robocompUpdater[\s\S]*?if\s*\(\s*this->startup_check_flag\s*\)\s*\{[\s\S]*?this->startup_check\(\);\s*\}\s*else\s*\{',
        #     '',
        #     contenido,
        #     flags=re.DOTALL
        # )


    # 3. Eliminar setParams
    contenido = re.sub(
        r'bool SpecificWorker::setParams\([^)]*\)\s*\{[\s\S]*?\n\}\s*',
        '',
        contenido
    )

    # 4. Añadir nuevos estados si no existen
    estados = """
void SpecificWorker::emergency()
{
    std::cout << "Emergency worker" << std::endl;
	//computeCODE
	//
	//if (SUCCESSFUL)
    //  emmit goToRestore()
}

//Execute one when exiting to emergencyState
void SpecificWorker::restore()
{
    std::cout << "Restore worker" << std::endl;
	//computeCODE
	//Restore emergency component

}"""
    
    if "void SpecificWorker::emergency()" not in contenido:
        # Buscar la función compute() completa con su contenido
        compute_match = re.search(
            r'(void SpecificWorker::compute\(\)\s*\{[\s\S]*?\n\})',
            contenido
        )
        
        if compute_match:
            # Insertar los nuevos estados después de la función compute()
            contenido = contenido.replace(
                compute_match.group(1),
                f"{compute_match.group(1)}\n\n{estados}"
            )
        else:
            # Si no se encuentra compute(), insertar al final del archivo
            contenido += f"\n\n{estados}"


    # 5. Actualizar gestión del periodo
    contenido = re.sub(
        r'timer(\.|->)start\([^)]*\);',  # Versión corregida
        '',
        contenido
    )

    contenido = re.sub(
    r'Period\s*(\+|-)=\s*(\w+);',
    r'setPeriod("Compute", getPeriod("Compute") \1 \2);',
    contenido
    )

    contenido = re.sub(
        r'(this->|\.)?Period\s*=\s*([^;]+);',
        r'setPeriod("Compute", \2);',
        contenido
    )

    contenido = re.sub(
        r'timer->setPeriod\((\w+)\)',
        r'setPeriod("Compute", \1)',
        contenido
    )


    # Luego reemplazar timer.setInterval
    contenido = re.sub(
        r'timer\.setInterval\(this->Period\)',
        r'',
        contenido
    )


    contenido = re.sub(
        r'timer.setInterval\((\w+)\)',
        r'setPeriod("Compute", \1)',
        contenido
    )


    contenido = re.sub(
        r'(timer->getPeriod\(\)|this->Period)',
        'getPeriod("Compute")',
        contenido
    )
    


    contenido = limpiar_residuales(contenido)

    # Escribir el archivo actualizado
    with open(cpp_path, 'w') as f:
        f.write(contenido)

    print(f"Archivo specificworker.cpp actualizado correctamente en {cpp_path}")
    return path_DSR

def actualizar_config(directorio, path_DSR):

    """Actualiza el archivo specificworker.h con los nuevos requerimientos"""
    etc_dir = os.path.join(directorio, "etc")
    list_configs = os.listdir(etc_dir)

    for file in list_configs:
        if not "." in file: #no tiene extension
            config_path = os.path.join(etc_dir, file)
            with open(config_path, 'r') as f:
                contenido = f.read()

            contenido = re.sub(r'(^CommonBehavior\.Endpoints\s*=.*$|^InnerModelPath\s*=.*$)', '', contenido, flags=re.MULTILINE)

            # 1. Reemplazar Endpoints y Proxies (añadiendo comillas de cierre)
            contenido = re.sub(r'(\w+)\.Endpoints=(.*)', r'Endpoints.\1 = "\2"', contenido)
            contenido = re.sub(r'(\w+)Proxy\s*=\s*(.*)', r'Proxies.\1 = "\2"', contenido)
            contenido = re.sub(r'TopicManager.Proxy\s*=\s*(.*)', r'Proxies.TopicManager = "\1"', contenido)

            # 1. Compactar los reemplazos con un diccionario
            sustituciones = {
                r'agent_id': r'Agent.id',
                r'agent_name': r'Agent.name',
                r'tree_view': r'ViewAgent.tree',
                r'graph_view': r'ViewAgent.graph',
                r'2d_view': r'ViewAgent.2d',
                r'3d_view': r'ViewAgent.3d'
            }

            for patron, reemplazo in sustituciones.items():
                contenido = re.sub(patron, reemplazo, contenido)
            
            contenido = re.sub(
                r'(Agent\.name\s*=\s*[^\n]+\n)',
                fr'\1Agent.configFile = "{path_DSR}"\n',
                contenido
            )


            # 2. Variables Ice que SIEMPRE llevan comillas
            variables_ice = [
                'Ice.Warn.Connections',
                'Ice.Trace.Network',
                'Ice.Trace.Protocol',
                'Ice.MessageSizeMax'
            ]


            for var in variables_ice:
                contenido = re.sub(
                    fr'^{var}\s*=\s*([^"\n]+)',
                    f'{var} = "\\1"',
                    contenido,
                    flags=re.MULTILINE
                )
            
            # 2. Añadir comillas solo a strings que lo necesiten
            def añadir_comillas(match):
                key = match.group(1).strip()
                value_with_comment = match.group(2).strip()
                
                # Separar el valor del comentario
                if '#' in value_with_comment:
                    value = value_with_comment.split('#')[0].strip()
                    comment = ' #' + value_with_comment.split('#', 1)[1]
                else:
                    value = value_with_comment
                    comment = ''
                
                # No añadir comillas si:
                # - Ya las tiene
                # - Es número (incluyendo negativos)
                # - Es booleano
                if (value.startswith('"') and value.endswith('"')) or \
                re.match(r'^-?\d+\.?\d*$', value) or \
                value.lower() in ['true', 'false']:
                    return f'{key} = {value}{comment}'
                return f'{key} = "{value}"{comment}'

            contenido = re.sub(r'^(\s*[^#\s][^=]*)\s*=\s*(.*)$', añadir_comillas, contenido, flags=re.MULTILINE)

            # 3. Añadir periodos si no existen
            if 'Period.Compute' not in contenido:
                contenido += '\nPeriod.Compute = 100\nPeriod.Emergency = 500\n'

            # 4. Normalizar formato de asignaciones
            contenido = re.sub(r'\s*=\s*', ' = ', contenido)

            # 5. Añadir comillas a parámetros Ice.* (excepto números)
            def formatear_ice(match):
                key = match.group(1)
                value = match.group(2)
                return f'{key} = "{value}"'

            contenido = re.sub(r'(Ice\.[^\s=]+)\s*=\s*([^"\s]+)', formatear_ice, contenido)

            contenido  = limpiar_residuales(contenido, 1)

            with open(config_path, 'w') as f:
                f.write(contenido)

def update(directorio):
    
    if not os.path.isdir(directorio):
        print(f"Error: El directorio {directorio} no existe")
        return
    
    # Crear copia de seguridad primero
    backup_file = crear_copia_seguridad(directorio)
    print(f"\nCopia de seguridad creada en: {backup_file}")
    
    # Limpiar directorio src/
    limpiar_directorio_src(directorio)
    
    # Actualizar CMakeLists.txt en src/
    actualizar_cmake_src(directorio)

    # # Actualizar apecifickworker.h en src/
    actualizar_specificworker_h(directorio)

    # Actualizar apecifickworker.cpp en src/
    path_DSR = actualizar_specificworker_cpp(directorio)


    # Actualizar config en src/
    actualizar_config(directorio, path_DSR)

    
    # Verificar estructura final
    verificar_estructura(directorio)
    
    print("\nProceso completado. Recomendaciones:")
    print("- Revise manualmente los archivos en src/ para asegurarse de que solo quedan los archivos específicos")
    print("- Verifique que no haya archivos duplicados entre src/ y generated/")
    print("- Si hay archivos .ui u otros recursos, asegúrese de que estén referenciados en CMakeLists.txt")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Limpieza de componentes RoboComp después de generación con robocompdsl')
    parser.add_argument('directorio', help='Directorio del componente a limpiar')
    args = parser.parse_args()
    update(args.directorio)