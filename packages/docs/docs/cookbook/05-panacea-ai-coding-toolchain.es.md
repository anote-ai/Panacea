# Panacea AI Coding Toolchain

Esta receta explica cómo se entrega la experiencia de codificación AI de Panacea a través de CLI, SDK y VS Code.

## Lo que aprenderás

- Los diferentes puntos de entrada de codificación AI en Panacea
- Cómo se relacionan la CLI, el SDK y la extensión de VS Code con el backend compartido
- Capacidades clave del producto para asistencia de código privado
- Dónde buscar en el repositorio detalles de implementación

## Por qué esto es importante

Panacea está construido como un producto unificado con múltiples interfaces:

- una **CLI** que potencia `anote chat`, búsqueda de código y revisión de repositorios
- una **extensión de VS Code** para asistencia AI en el editor
- un **SDK** para incrustar Panacea en otras aplicaciones

Estas interfaces comparten un backend y una capa de razonamiento impulsada por agentes, lo que hace que el producto sea consistente en flujos de trabajo de escritorio, web y código.

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/packages/cli` | Implementación de CLI en TypeScript para flujos de trabajo de desarrolladores |
| `Panacea/packages/vscode` | Extensión de VS Code e integración de chat |
| `Panacea/packages/sdk` | SDK en TypeScript para acceso programático |
| `Panacea/packages/backend` | Servicio backend compartido que potencia todas las interacciones de UI y CLI |

## Cómo funciona

- Una acción de usuario de codificación comienza en la CLI, SDK o extensión de VS Code.
- La solicitud se envía a la API backend de Panacea.
- El backend utiliza orquestación de agentes y proveedores de modelos para producir respuestas conscientes del código.
- La respuesta se devuelve en la misma interfaz, con sugerencias de código, explicaciones o correcciones.

## Características útiles del producto

- **CLI**: `anote chat`, búsqueda de repositorios, revisión de código, generación de código y asistencia impulsada por embeddings.
- **VS Code**: chat en línea, vistas previas de diferencias, acciones de código y respuestas en streaming.
- **SDK**: un envoltorio de cliente para la API de Panacea, que permite integraciones personalizadas.

## Ejecútalo localmente

Desde la raíz del espacio de trabajo (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Esto inicia los servicios backend y frontend compartidos.

En otra terminal, ejecuta el paquete CLI:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Luego puedes usar la CLI localmente o construirla con `npm run build`.

Para el desarrollo de VS Code, abre `Panacea/packages/vscode` en VS Code y lanza la extensión con el depurador.

## Notas para el libro de recetas

Esta receta es útil para compañeros de equipo que necesitan un recorrido de alto nivel por el producto de codificación AI de múltiples interfaces de Panacea. También puede señalar a los lectores archivos de implementación que pueden modificar o extender.
