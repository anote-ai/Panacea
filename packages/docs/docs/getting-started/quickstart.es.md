# Inicio Rápido

## 1. Inicializar

```bash
anote init
```

Esto te guía a través de la configuración de tu clave API y proveedor de LLM preferido.

## 2. Hacer una pregunta

```bash
# Pregunta general
anote ask "¿cómo funciona la autenticación en esta base de código?"

# Enfocarse en un archivo
anote ask --file src/auth.ts "explica esto"

# Pasar código
cat src/handler.py | anote ask "¿qué podría salir mal aquí?"
```

## 3. Corregir errores automáticamente

```bash
# Corregir e iterar hasta que las pruebas pasen (hasta 5 rondas)
anote fix --loop --max-iterations 5
```

## 4. Indexar para búsqueda semántica

```bash
# Indexar tu base de código (ejecutar una vez, luego mantener actualizado)
anote index

# Buscar semánticamente
anote search "validación de token JWT"
anote search "grupo de conexiones a la base de datos"
```

## 5. Revisar un PR

```bash
anote review --pr 42
```

## 6. Generar un changelog

```bash
anote changelog --since v1.2.0
```
