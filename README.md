Esta herramienta ayuda a gestionar una lista de tareas típica, como por ejemplo este mismo README.

Pretende ser:
- Sencilla de usar
- Fácil de modificar
- Modular y extensible

Se ha orientado a que, de su uso cotidiano, se extraiga el contenido para completar automáticamente las entradas de un time-tracker.

Además, produce un fichero CSV en el que se registra cuándo se ha realizado cada acción, sobre el cual se podrá hacer un análisis posterior con otras herramientas.

# Tareas

- [/] Elegir nombre

## Funcionalidades básicas

- [x] Añadir tareas como pendientes
- [x] Marcar tareas como completadas
- [x] Marcar una tarea como "en progreso"

## Registro temporal: logbook

- [x] Generar `logbook.csv`
- [x] Añadir acciones (no tareas) que van directamente a `logbook.csv`

## Publicación en time-tracker

- [x] Generar `commit.tmp`
- [x] #alias
- [ ] Redondear con bloques de 15 mins
- [ ] Proporcionar `commit.template`

## Funcionalidades extra

- [ ] Deshacer última acción
- [ ] Subtareas
