# POC Edge-Content Offline-First

Este repositorio contiene una prueba de concepto (POC) de un sistema **offline-first** de entrega de contenido (PDF/Vídeos) usando un servidor central y un servidor edge (cache local), todo simulado en Python.

---

## 📂 Estructura de carpetas y archivos

```bash
your-project/
├── .github/
│   └── workflows/
│       └── ci.yml             # Configuración de GitHub Actions
├── data.py                    # Datos mock: usuarios, contenidos, chunks, cache
├── cache.py                   # Lógica de gestión de cache (evicción)
├── app.py                     # Aplicación Flask con endpoints REST
├── requirements.txt           # Dependencias Python
└── tests/                     # Suite de pruebas pytest
    ├── conftest.py            # Fixture de cliente Flask
    ├── test_offline.py        # Test de acceso offline
    ├── test_bandwidth.py      # Test de descarga en chunks + compresión
    ├── test_storage.py        # Test de límites de almacenamiento
    └── test_reliability.py    # Test de reintento y reanudación
```

---

## 🚀 Instalación y ejecución local

1. Clonar el repositorio y entrar en la carpeta del proyecto:

   ```bash
   git clone <url-repo>
   cd your-project
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Iniciar la aplicación Flask:

   ```bash
   export FLASK_APP=app.py
   flask run
   ```

   La API quedará disponible en `http://127.0.0.1:5000`.

5. En otro terminal (o en background) ejecutar los tests:

   ```bash
   pytest
   ```

---

## 📡 Endpoints disponibles

| Método | Ruta             | Descripción                                                   |
| ------ | ---------------- | ------------------------------------------------------------- |
| POST   | `/login`         | Autentica usuario y guarda token en cache local para offline. |
| GET    | `/content`       | Listado de contenidos disponibles (metadatos).                |
| GET    | `/download/<id>` | Descarga un contenido en chunks comprimidos, guarda en cache. |
| POST   | `/sync-chunk`    | Simula subida de un chunk modificado al servidor (colas).     |
| POST   | `/auth/sync`     | Sincroniza cambios de credenciales (stub en POC).             |

---

## 📦 Simulación de componentes

* **Usuarios (`data.py`)**: Diccionario con user/password y token JWT.
* **Content DB**: Metadatos de archivos (`size`, `chunks`).
* **Chunks Store**: Lista de bytes por archivo, simula troceo.
* **Cache**: Almacenamiento local por usuario, con límite de 10 GB y políticas de evicción.
* **Message Queue**: Lista en memoria para simular colas BMQ.

---

## 🛠️ Funciones de fitness (tests automatizados)

1. **Acceso offline** (`test_offline.py`): Verifica login y lectura desde cache sin red.
2. **Optimización de ancho de banda** (`test_bandwidth.py`): Descarga en chunks + "compresión" (reducción de tamaño).
3. **Límites de almacenamiento** (`test_storage.py`): Evicción de archivos cuando se supera 10 GB.
4. **Confiabilidad** (`test_reliability.py`): Simula caídas aleatorias y reintentos por chunk.

Cada test está implementado con **pytest** y ejerce la lógica que debe validar cada fitness function.

---

## ✅ Integración continua con GitHub Actions

El archivo `.github/workflows/ci.yml` define un workflow que:

1. Se dispara en `push` o `pull_request`.
2. Instala Python 3.9 y dependencias.
3. Inicia la app Flask en background.
4. Espera 2 segundos para arranque.
5. Ejecuta `pytest`.

Si todos los tests pasan, la acción finaliza con éxito.
