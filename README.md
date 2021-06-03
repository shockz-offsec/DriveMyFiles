# Backup Script

- Principal despligue en Windows
- Posibilidad de Linux
- No se contempla MacOS

## Casos de uso
- Realizar recompilación, compresion y subida a la nube de diversos archivos / carpetas.
- Ejecución periodica de dicho script (a elegir por desarrolladores: cron/crontab/windows)
- Copia de seguridad de spotify mediante web (http://www.spotmybackup.com) exportado en json (inicialmente no se contempla la importación)
- Mostrar capacidad de la copia de seguridad local y en nube.
- Eliminar copias de seguridad antiguas.
- Compresión de archivos
- Barras de progreso

## Archivo de configuración
- Rutas de los archivos
- Credenciales drive ()
- Google Drive API Key
- Periodicidad a la que se ejecute el script
- Ruta local donde se almacena la informacion previamente a la subida a la nube
- Ruta del registro del script (Seguramente un directorio del paquete) (en principio es una ruta estática)
- Credenciales de spotify (si procede)
- Habilitar: backup de spotify (true/false) => True: se piden credenciales spotify

## Tecnologias y ficheros
- Python3
- Archivo con configuración (json)
- gdrive (binarios de forma estatica) =/ si se quisiera usar la api de drive se necesitarian de librerias externas // (modificar codigo para añadir api key)

## Aspecto a implementar para mejorar cara al usuario final

### GUI
- Botón para hacer copia a voluntad
- Opciones del archivo de configuración a través de la gui
- Establecer periodo cron/crontab/win 
- Elegir rutas mediante explorer

### Otros aspectos
- Bajar cambios a un directorio local.



## Otras características a contemplar
- Habilitar: cifrar archivo (true/false)
- Eliminar ficheros que hay en drive que no estan incluidos en las rutas de los archivos que se les quiere hacer backup
- Añadir marca de tiempo al archivo comprimido a no ser que se pueda obtener un timestamp de otro lugar


### Librerias Python

- shutil (copia, recompilacion de archivos)
- logging
- gdrive
- configparser (modificar el código de forma dinámica a raíz de necesidad)
- tarfile/zipfile u otro modulo de compresión
- os (eliminar copias locales temporales, comprobacion de existencia de ficheros/paths)
- requests (get/put/post para obtener el json asociado al spotify)
-   ºcrontab