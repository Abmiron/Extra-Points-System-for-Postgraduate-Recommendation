import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Student from '../views/Student.vue'
import Teacher from '../views/Teacher.vue'
import Admin from '../views/Admin.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/student',
    name: 'Student',
    component: Student
  },
  {
    path: '/teacher',
    name: 'Teacher',
    component: Teacher
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin
  },
  {
    path:'/:pathMatch(.*)*',
    redirect:'/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router