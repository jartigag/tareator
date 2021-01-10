Esta herramienta ayuda a gestionar una lista de tareas típica, como por ejemplo este mismo README.

<p align="center"><a href="https://asciinema.org/a/360282" target="_blank"><img src="https://asciinema.org/a/360282.svg" /></a></p>

Pretende ser:

- Sencilla de usar

- Fácil de modificar

- Modular y extensible

Se ha orientado a que, de su uso cotidiano, se extraigan los datos necesarios para completar automáticamente las entradas de un [time-tracker](https://en.wikipedia.org/wiki/Time-tracking_software).

Además, produce un fichero CSV en el que se registra cuándo se ha realizado cada acción. Sobre él se podrán hacer análisis posteriores con otras herramientas.

Se hace una explicación un poco más desarrollada en [este post](https://jartigag.xyz/tareator).

# tareator

## v1.0
- [x] Elegir nombre

### Funcionalidades básicas
- [x] Añadir tareas como pendientes
- [x] Marcar tareas como completadas
- [x] Marcar una tarea como "en progreso"

### Registro temporal
- [x] Generar `register.csv`
- [x] Añadir acciones (no tareas) que van directamente a `register.csv`

### Publicación en time-tracker
- [x] Generar `commit.tmp`
- [x] #alias
- [x] Editar `intervals.template`
- [x] Redondear con bloques de 15 mins

### Funcionalidades extra
- [x] Deshacer última acción
- [x] Subtareas

## v2.0

### Funcionalidades ocultas
- [x] Registrar "--{open,close} tareator--"
- [x] e (abrir `tareas.md` en editor)
- [x] r (abrir `register.csv` en editor)
- [x] --silent flag

### Visualización
- [x] Demo mínima con cal-heatmap

![](screenshot.png)
