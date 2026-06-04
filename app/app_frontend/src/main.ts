// Autor: Jaime Martínez Benítez
// TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
// Archivo: "main.ts"
// Descripcion: Monta la aplicación Vue y registra el enrutador.

import { createApp } from 'vue'
import VentanaPrincipal from './VentanaPrincipal.vue'
import router from './router'

createApp(VentanaPrincipal).use(router).mount('#app')
