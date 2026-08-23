# Gestionar Sesiones

Cada conversación de `anote chat` se guarda localmente como una sesión: sus mensajes, uso de tokens y directorio de trabajo.

## Listar sesiones

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Sesiones guardadas (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  hace 10m  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      hace 2h   /Users/you/other-project
```

## Mostrar una sesión

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # más historial de mensajes
```

Imprime la conversación, totales de tokens y directorio de trabajo para esa sesión. Puedes pasar un prefijo corto del ID de la sesión en lugar del completo.

## Eliminar una sesión

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Próximos pasos

- [Flujos de trabajo comunes](common-workflows.md)
- [Cómo funciona Panacea](../core-concepts/how-it-works.md) — turnos, compactación y cómo la longitud de la sesión afecta el contexto
