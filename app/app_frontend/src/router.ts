// Autor: Jaime Martínez Benítez
// TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
// Archivo: "router.ts"
// Descripcion: Define las rutas del frontend y sus redirecciones.

import { createRouter, createWebHistory, type RouteLocation, type RouteRecordRaw } from 'vue-router'
import VentanaPrincipal from './VentanaPrincipal.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },

  // Auth: mismas acciones que /api/auth/... pero sin el prefijo /api/auth.
  { path: '/login', name: 'login', component: VentanaPrincipal },
  { path: '/register', name: 'register', component: VentanaPrincipal },
  { path: '/password-reset', name: 'password-reset', component: VentanaPrincipal },
  { path: '/profile', name: 'profile', component: VentanaPrincipal },
  { path: '/profile/edit', name: 'edit-profile', component: VentanaPrincipal },

  // Pantalla resumen de la aplicación.
  { path: '/dashboard', name: 'dashboard', component: VentanaPrincipal },

  // Recursos principales: mismo formato que /api/tasks/ y /api/projects/.
  { path: '/tasks', name: 'tasks', component: VentanaPrincipal },
  { path: '/tasks/new', name: 'task-create', component: VentanaPrincipal },
  { path: '/tasks/:id(\\d+)', name: 'task-detail', component: VentanaPrincipal },
  { path: '/tasks/:id(\\d+)/edit', name: 'task-edit', component: VentanaPrincipal },
  { path: '/tasks/:id(\\d+)/delete', name: 'task-delete', component: VentanaPrincipal },
  { path: '/projects', name: 'projects', component: VentanaPrincipal },
  { path: '/projects/new', name: 'project-create', component: VentanaPrincipal },
  { path: '/projects/:id(\\d+)', name: 'project-detail', component: VentanaPrincipal },
  { path: '/projects/:id(\\d+)/edit', name: 'project-edit', component: VentanaPrincipal },
  { path: '/projects/:id(\\d+)/delete', name: 'project-delete', component: VentanaPrincipal },

  // Endpoints informativos y de productividad.
  { path: '/calendar', name: 'calendar', component: VentanaPrincipal },
  { path: '/statistics', name: 'statistics', component: VentanaPrincipal },
  { path: '/statistics/dashboard', redirect: '/statistics' },
  { path: '/achievements', name: 'achievements', component: VentanaPrincipal },
  { path: '/export', name: 'export', component: VentanaPrincipal },
  { path: '/productivity-sessions', name: 'techniques', component: VentanaPrincipal },
  { path: '/productivity-sessions/pomodoro', name: 'technique-pomodoro', component: VentanaPrincipal },
  { path: '/productivity-sessions/pomodoro/break', name: 'technique-pomodoro-break', component: VentanaPrincipal },
  { path: '/productivity-sessions/pomodoro/summary', name: 'technique-pomodoro-summary', component: VentanaPrincipal },
  { path: '/productivity-sessions/52-17', name: 'technique-5217', component: VentanaPrincipal },
  { path: '/productivity-sessions/52-17/break', name: 'technique-5217-break', component: VentanaPrincipal },
  { path: '/productivity-sessions/52-17/summary', name: 'technique-5217-summary', component: VentanaPrincipal },
  { path: '/productivity-sessions/time-blocking', name: 'technique-time-blocking', component: VentanaPrincipal },

  // Compatibilidad con las rutas antiguas en español.
  { path: '/registro', redirect: '/register' },
  { path: '/recuperar-contrasena', redirect: '/password-reset' },
  { path: '/inicio', redirect: '/dashboard' },
  { path: '/perfil', redirect: '/profile' },
  { path: '/perfil/editar', redirect: '/profile/edit' },
  { path: '/calendario', redirect: '/calendar' },
  { path: '/estadisticas', redirect: '/statistics' },
  { path: '/logros', redirect: '/achievements' },
  { path: '/exportar', redirect: '/export' },
  { path: '/tecnicas', redirect: '/productivity-sessions' },
  { path: '/tecnicas/pomodoro', redirect: '/productivity-sessions/pomodoro' },
  { path: '/tecnicas/pomodoro/descanso', redirect: '/productivity-sessions/pomodoro/break' },
  { path: '/tecnicas/pomodoro/resumen', redirect: '/productivity-sessions/pomodoro/summary' },
  { path: '/tecnicas/52-17', redirect: '/productivity-sessions/52-17' },
  { path: '/tecnicas/52-17/descanso', redirect: '/productivity-sessions/52-17/break' },
  { path: '/tecnicas/52-17/resumen', redirect: '/productivity-sessions/52-17/summary' },
  { path: '/tecnicas/time-blocking', redirect: '/productivity-sessions/time-blocking' },
  { path: '/tareas', redirect: '/tasks' },
  { path: '/tareas/nueva', redirect: '/tasks/new' },
  { path: '/tareas/:id(\\d+)', redirect: (to: RouteLocation) => `/tasks/${to.params.id}` },
  { path: '/tareas/:id(\\d+)/editar', redirect: (to: RouteLocation) => `/tasks/${to.params.id}/edit` },
  { path: '/tareas/:id(\\d+)/eliminar', redirect: (to: RouteLocation) => `/tasks/${to.params.id}/delete` },
  { path: '/proyectos', redirect: '/projects' },
  { path: '/proyectos/nuevo', redirect: '/projects/new' },
  { path: '/proyectos/:id(\\d+)', redirect: (to: RouteLocation) => `/projects/${to.params.id}` },
  { path: '/proyectos/:id(\\d+)/editar', redirect: (to: RouteLocation) => `/projects/${to.params.id}/edit` },
  { path: '/proyectos/:id(\\d+)/eliminar', redirect: (to: RouteLocation) => `/projects/${to.params.id}/delete` },

  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
