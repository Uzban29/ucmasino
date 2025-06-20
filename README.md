# 🎲 ucmasino

Proyecto escolar: Juego de dados estilo casino con interfaz gráfica en Python.

## Descripción

Este repositorio contiene un juego de dados tipo casino desarrollado en Python, con las siguientes características principales:

- **Login y registro** de usuarios utilizando [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- **Mesa de juego interactiva** creada con [Pygame](https://www.pygame.org/news).
- **Conexión a base de datos MySQL** usando `mysql.connect` para gestionar usuarios y puntajes.

---

## 🚀 Tecnologías Utilizadas

- **Python 3.x**
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interfaz gráfica de login/registro
- [Pygame](https://www.pygame.org/news) - Interfaz gráfica para el juego
- [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/) - Conexión a base de datos

---

## 📁 Estructura del Proyecto

```plaintext
src/
├── menu/         # Login y registro
├── game/         # Juego de dados (Pygame)
├── db/           # Conexión y lógica de base de datos
└── assetes/      # Fuente BigBlue, imágenes, gifs
main.py           # Ejecutable principal 
```

---

## ⚙️ Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/Uzban29/ucmasino.git
   cd ucmasino
   ```

2. Instala las dependencias necesarias:

   ```bash
   pip install customtkinter pygame mysql-connector-python
   ```

3. Configura tu base de datos MySQL según las instrucciones en `src/db/`.

---

## 🕹️ Uso

Ejecuta el archivo principal:

```bash
python main.py
```

