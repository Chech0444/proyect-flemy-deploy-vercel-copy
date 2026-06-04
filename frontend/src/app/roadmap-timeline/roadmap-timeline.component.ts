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
  activeCert = 'backend';

  courses: TimelineCourse[] = [
    {
      id: 1, title: 'Java desde Cero',
      description: 'Aprende la sintaxis de Java, variables, tipos de datos, estructuras de control, arrays y los fundamentos del lenguaje más usado en el mundo empresarial.',
      duration: '20 horas', lessons: 75, level: 'beginner',
      emoji: '☕', stepName: 'Fundamentos', slug: 'java-desde-cero'
    },
    {
      id: 2, title: 'POO con Java',
      description: 'Domina la Programación Orientada a Objetos: clases, herencia, interfaces, polimorfismo, encapsulamiento y principios SOLID.',
      duration: '25 horas', lessons: 80, level: 'beginner',
      emoji: '🧩', stepName: 'POO', slug: 'poo-java'
    },
    {
      id: 3, title: 'Java Standard Library',
      description: 'Colecciones, Streams, lambdas, manejo de archivos, excepciones, genéricos y programación funcional en Java.',
      duration: '18 horas', lessons: 60, level: 'beginner',
      emoji: '📚', stepName: 'Librerías', slug: 'java-standard-library'
    },
    {
      id: 4, title: 'JDBC y JPA con Hibernate',
      description: 'Conexión a bases de datos relacionales con JDBC, mapeo objeto-relacional con JPA/Hibernate, relaciones y consultas JPQL.',
      duration: '22 horas', lessons: 70, level: 'intermediate',
      emoji: '🗄️', stepName: 'Bases de Datos', slug: 'jpa-hibernate'
    },
    {
      id: 5, title: 'Spring Boot Essentials',
      description: 'Inversión de control, inyección de dependencias, Spring MVC, configuración automática y creación de aplicaciones empresariales.',
      duration: '30 horas', lessons: 90, level: 'intermediate',
      emoji: '🍃', stepName: 'Spring', slug: 'spring-boot'
    },
    {
      id: 6, title: 'APIs REST con Spring Boot',
      description: 'Crea APIs RESTful profesionales con Spring Boot: validación, seguridad con JWT, documentación con Swagger y manejo de errores.',
      duration: '20 horas', lessons: 65, level: 'intermediate',
      emoji: '🔌', stepName: 'APIs REST', slug: 'api-rest-spring'
    },
    {
      id: 7, title: 'Java Testing Avanzado',
      description: 'JUnit 5, Mockito, pruebas de integración con Spring Test, TDD y cobertura de código con JaCoCo.',
      duration: '15 horas', lessons: 50, level: 'advanced',
      emoji: '🧪', stepName: 'Testing', slug: 'java-testing'
    },
    {
      id: 8, title: 'Microservicios con Spring Cloud',
      description: 'Arquitectura de microservicios: Eureka, Gateway, Resilience4j, Config Server, tracing distribuido y comunicación asíncrona.',
      duration: '28 horas', lessons: 80, level: 'advanced',
      emoji: '🌐', stepName: 'Microservicios', slug: 'microservicios-spring'
    },
    {
      id: 9, title: 'Proyecto Final: App Java Empresarial',
      description: 'Construye una aplicación completa desde cero: backend con Spring Boot, frontend con Angular/Thymeleaf, base de datos, pruebas y deploy en producción.',
      duration: '40 horas', lessons: 45, level: 'advanced',
      emoji: '🏆', stepName: 'Proyecto Final', slug: 'proyecto-final-java'
    }
  ];

  routes: Record<string, CertRoute> = {
    backend: {
      courseIds: [1, 2, 3, 4, 5, 6, 9],
      complementary: [7],
      title: 'Backend Java',
      description: 'Domina el desarrollo backend con Java: desde los fundamentos hasta APIs REST empresariales con Spring Boot y JPA.'
    },
    fullstack: {
      courseIds: [1, 2, 3, 4, 5, 6, 9],
      complementary: [7, 8],
      title: 'Full Stack Java',
      description: 'Conviértete en desarrollador Full Stack Java cubriendo backend, APIs, microservicios y proyecto integrador.'
    },
    microservices: {
      courseIds: [5, 6, 7, 8, 9],
      complementary: [4],
      title: 'Microservicios',
      description: 'Especialización en microservicios con Spring Cloud: APIs, tolerancia a fallos, descubrimiento y despliegue.'
    },
    testing: {
      courseIds: [1, 5, 6, 7],
      complementary: [3],
      title: 'Testing Java',
      description: 'Enfócate en calidad de software: unit tests, integración, TDD y aseguramiento de calidad en proyectos Java.'
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
