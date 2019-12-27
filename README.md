Esta herramienta ayuda a gestionar una lista de tareas típica, como por ejemplo este mismo README.

Pretende ser:
- Sencilla de usar
- Fácil de modificar
- Modular y extensible

Además, produce un fichero CSV en el que se registra cuándo se ha realizado cada acción, permitiendo analizarlas después con otras herramientas.

Se ha orientado a escribir las entradas de un time-tracker de forma natural, con los eventos generados al completar la lista de tareas.

# Tareas

- [ ] Elegir nombre

## Funcionalidades básicas

- [x] Añadir tareas como pendientes
- [x] Marcar tareas como completadas
- [x] Marcar una tarea como "en progreso"

## Registro temporal: logbook

- [x] Generar `logbook.csv`
- [x] Añadir acciones (no tareas) que van directamente a `logbook.csv`

## Publicación en time-tracker

- [x] Generar `commit.tmp`
- [ ] #alias
- [ ] Redondear con bloques de 15 mins
- [ ] UI de revisión antes de confirmar commit

## Funcionalidades extra

- [ ] Deshacer última acción
- [ ] Subtareas
