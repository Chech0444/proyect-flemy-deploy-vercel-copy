import { Component } from '@angular/core';
import { NgClass, NgFor, NgIf, KeyValuePipe } from '@angular/common';
import { RouterLink } from '@angular/router';

interface TimelineCourse {
  id: number;
  title: string;
  description: string;
  duration: string;
  lessons: number;
  level: 'beginner' | 'intermediate' | 'advanced';
  emoji: string;
  stepName: string;
  slug: string;
}

interface CertRoute {
  courseIds: number[];
  complementary: number[];
  title: string;
  description: string;
}

@Component({
  selector: 'app-roadmap-timeline',
  imports: [NgClass, NgFor, NgIf, KeyValuePipe, RouterLink],
  templateUrl: './roadmap-timeline.component.html',
  styleUrl: './roadmap-timeline.component.css'
})
export class RoadmapTimelineComponent {
  activeCert = 'fullstack';

  courses: TimelineCourse[] = [
    {
      id: 1, title: 'Introducción a la Programación',
      description: 'Domina la lógica computacional, variables, estructuras de control, funciones y los fundamentos que todo programador debe conocer.',
      duration: '15 horas', lessons: 60, level: 'beginner',
      emoji: '🧠', stepName: 'Fundamentos', slug: 'intro-programacion'
    },
    {
      id: 2, title: 'HTML y CSS desde Cero',
      description: 'Construye interfaces web semánticas y responsivas. Aprende HTML5, CSS3, Flexbox, Grid y diseño adaptable.',
      duration: '20 horas', lessons: 80, level: 'beginner',
      emoji: '🎨', stepName: 'Web Basics', slug: 'html-css'
    },
    {
      id: 3, title: 'JavaScript Esencial',
      description: 'Domina JavaScript moderno: ES6+, manipulación del DOM, eventos, asincronía y consumo de APIs.',
      duration: '25 horas', lessons: 90, level: 'beginner',
      emoji: '⚡', stepName: 'Lógica', slug: 'javascript'
    },
    {
      id: 4, title: 'Python Avanzado',
      description: 'Programación orientada a objetos, módulos, testing, decoradores y automatización con Python.',
      duration: '30 horas', lessons: 70, level: 'intermediate',
      emoji: '🐍', stepName: 'Backend', slug: 'python-avanzado'
    },
    {
      id: 5, title: 'React Moderno',
      description: 'Hooks, estado global, React Router, SSR con Next.js y patrones avanzados de componentes.',
      duration: '35 horas', lessons: 100, level: 'intermediate',
      emoji: '⚛️', stepName: 'Frontend', slug: 'react-moderno'
    },
    {
      id: 6, title: 'Bases de Datos SQL y NoSQL',
      description: 'PostgreSQL, MongoDB, modelado de datos, consultas avanzadas, índices y optimización.',
      duration: '20 horas', lessons: 50, level: 'intermediate',
      emoji: '🗄️', stepName: 'Datos', slug: 'bases-datos'
    },
    {
      id: 7, title: 'Node.js y APIs REST',
      description: 'Express, autenticación JWT, middlewares, WebSockets y despliegue de APIs en producción.',
      duration: '25 horas', lessons: 65, level: 'advanced',
      emoji: '🚀', stepName: 'APIs', slug: 'nodejs-apis'
    },
    {
      id: 8, title: 'DevOps y Cloud',
      description: 'Docker, CI/CD, AWS, Terraform, monitoreo y despliegue continuo de aplicaciones.',
      duration: '30 horas', lessons: 55, level: 'advanced',
      emoji: '☁️', stepName: 'DevOps', slug: 'devops-cloud'
    },
    {
      id: 9, title: 'Proyecto Full Stack Final',
      description: 'Construye una aplicación completa desde cero: frontend, backend, base de datos, testing y deploy.',
      duration: '40 horas', lessons: 30, level: 'advanced',
      emoji: '🏆', stepName: 'Integración', slug: 'proyecto-final'
    }
  ];

  routes: Record<string, CertRoute> = {
    completa: {
      courseIds: [1, 2, 3, 4, 5, 6, 7, 8, 9],
      complementary: [],
      title: 'Ruta Completa',
      description: 'Todos los cursos de la plataforma, desde los fundamentos hasta el proyecto final integrador.'
    },
    frontend: {
      courseIds: [2, 3, 5],
      complementary: [4],
      title: 'Frontend',
      description: 'Especialización en desarrollo frontend. HTML, CSS, JavaScript y React con frameworks modernos.'
    },
    backend: {
      courseIds: [1, 4, 6, 7],
      complementary: [8],
      title: 'Backend',
      description: 'Domina el desarrollo backend con Python, Node.js, bases de datos y APIs REST.'
    },
    fullstack: {
      courseIds: [1, 2, 3, 4, 5, 6, 7, 9],
      complementary: [8],
      title: 'Full Stack',
      description: 'Conviértete en desarrollador Full Stack cubriendo frontend, backend, bases de datos y proyecto integrador.'
    },
    devops: {
      courseIds: [7, 8, 9],
      complementary: [6],
      title: 'DevOps & Cloud',
      description: 'Infraestructura moderna, contenedores, CI/CD y despliegue en la nube.'
    }
  };

  get currentRoute(): CertRoute {
    return this.routes[this.activeCert];
  }

  get filteredCourses(): { course: TimelineCourse; isComplementary: boolean; stepNumber: number }[] {
    const route = this.currentRoute;
    const result: { course: TimelineCourse; isComplementary: boolean; stepNumber: number }[] = [];
    let step = 1;

    for (const id of route.courseIds) {
      const course = this.courses.find(c => c.id === id);
      if (course) {
        result.push({ course, isComplementary: false, stepNumber: step++ });
      }
    }

    for (const id of route.complementary) {
      const course = this.courses.find(c => c.id === id);
      if (course && !route.courseIds.includes(id)) {
        result.push({ course, isComplementary: true, stepNumber: step++ });
      }
    }

    return result;
  }

  get showCertGoal(): boolean {
    return this.activeCert !== 'completa';
  }

  setCert(cert: string) {
    this.activeCert = cert;
  }

  levelClass(level: string): string {
    return 'level-' + level;
  }

  levelLabel(level: string): string {
    return level === 'beginner' ? 'Principiante' : level === 'intermediate' ? 'Intermedio' : 'Avanzado';
  }
}
