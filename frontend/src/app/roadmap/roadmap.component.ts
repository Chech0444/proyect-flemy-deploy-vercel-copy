import { Component } from '@angular/core';
import { NgClass, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';

interface RoadmapStep {
  icon: string;
  title: string;
  level: string;
  levelClass: string;
  description: string;
  duration: string;
  lessons: number;
  topics: string[];
}

interface Track {
  id: string;
  label: string;
  steps: RoadmapStep[];
}

@Component({
  selector: 'app-roadmap',
  imports: [NgClass, NgFor, RouterLink],
  templateUrl: './roadmap.component.html',
  styleUrl: './roadmap.component.css'
})
export class RoadmapComponent {
  activeTrack = 'full';

  tracks: Track[] = [
    {
      id: 'full',
      label: 'Ruta Completa',
      steps: [
        {
          icon: 'psychology',
          title: 'Fundamentos de Programación',
          level: 'Principiante',
          levelClass: 'beginner',
          description: 'Aprende las bases de la lógica de programación, variables, condicionales, ciclos y estructuras de datos fundamentales.',
          duration: '20 hrs',
          lessons: 48,
          topics: ['Lógica computacional', 'Variables y tipos', 'Condicionales', 'Ciclos', 'Arreglos']
        },
        {
          icon: 'code',
          title: 'Desarrollo Web Frontend',
          level: 'Principiante',
          levelClass: 'beginner',
          description: 'Domina HTML, CSS y JavaScript para construir interfaces web modernas y responsivas.',
          duration: '35 hrs',
          lessons: 72,
          topics: ['HTML semántico', 'CSS moderno', 'JavaScript', 'Responsive design', 'Accesibilidad']
        },
        {
          icon: 'database',
          title: 'Bases de Datos y Backend',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Construye APIs y maneja bases de datos relacionales y no relacionales con las mejores prácticas.',
          duration: '30 hrs',
          lessons: 56,
          topics: ['SQL', 'NoSQL', 'APIs REST', 'Autenticación', 'Despliegue']
        },
        {
          icon: 'smart_toy',
          title: 'Inteligencia Artificial',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Explora machine learning, procesamiento de lenguaje natural y generación de contenido con IA.',
          duration: '40 hrs',
          lessons: 64,
          topics: ['ML fundamentals', 'NLP', 'Prompt engineering', 'IA generativa', 'Ética en IA']
        },
        {
          icon: 'terminal',
          title: 'DevOps y Cloud',
          level: 'Avanzado',
          levelClass: 'advanced',
          description: 'Aprende CI/CD, contenedores, orquestación y despliegue en la nube para entornos profesionales.',
          duration: '25 hrs',
          lessons: 40,
          topics: ['Docker', 'CI/CD', 'Cloud services', 'Monitoreo', 'Seguridad']
        },
        {
          icon: 'rocket_launch',
          title: 'Proyecto Final Integrador',
          level: 'Avanzado',
          levelClass: 'advanced',
          description: 'Aplica todo lo aprendido en un proyecto real completo, desde la planificación hasta el despliegue.',
          duration: '50 hrs',
          lessons: 12,
          topics: ['Arquitectura', 'Stack completo', 'Testing', 'Documentación', 'Presentación']
        }
      ]
    },
    {
      id: 'web',
      label: 'Desarrollo Web',
      steps: [
        {
          icon: 'code',
          title: 'HTML & CSS Profesional',
          level: 'Principiante',
          levelClass: 'beginner',
          description: 'Construye interfaces modernas con HTML semántico, CSS Grid, Flexbox y animaciones.',
          duration: '15 hrs',
          lessons: 36,
          topics: ['HTML5', 'CSS3', 'Flexbox', 'Grid', 'Animaciones']
        },
        {
          icon: 'javascript',
          title: 'JavaScript Avanzado',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Domina closures, promesas, async/await y patrones avanzados de JavaScript.',
          duration: '25 hrs',
          lessons: 48,
          topics: ['ES6+', 'Async/Await', 'Patrones', 'DOM avanzado', 'Testing']
        },
        {
          icon: 'frame_source',
          title: 'Frameworks Modernos',
          level: 'Avanzado',
          levelClass: 'advanced',
          description: 'Domina Angular, React o Vue con proyectos prácticos y arquitectura escalable.',
          duration: '40 hrs',
          lessons: 60,
          topics: ['Componentes', 'Estado global', 'Ruteo', 'SSR', 'Performance']
        }
      ]
    },
    {
      id: 'ia',
      label: 'Inteligencia Artificial',
      steps: [
        {
          icon: 'functions',
          title: 'Matemáticas para IA',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Repasa álgebra lineal, cálculo y estadística aplicada al machine learning.',
          duration: '20 hrs',
          lessons: 32,
          topics: ['Álgebra lineal', 'Cálculo', 'Probabilidad', 'Estadística', 'Optimización']
        },
        {
          icon: 'smart_toy',
          title: 'Machine Learning',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Implementa modelos de ML supervisado y no supervisado con Python y scikit-learn.',
          duration: '35 hrs',
          lessons: 48,
          topics: ['Regresión', 'Clasificación', 'Clustering', 'Validación', 'Feature engineering']
        },
        {
          icon: 'psychology',
          title: 'Deep Learning & NLP',
          level: 'Avanzado',
          levelClass: 'advanced',
          description: 'Construye redes neuronales y modelos de lenguaje con TensorFlow y PyTorch.',
          duration: '45 hrs',
          lessons: 56,
          topics: ['Redes neuronales', 'CNN', 'RNN', 'Transformers', 'Fine-tuning']
        }
      ]
    },
    {
      id: 'devops',
      label: 'DevOps & Cloud',
      steps: [
        {
          icon: 'terminal',
          title: 'Linux y Redes',
          level: 'Principiante',
          levelClass: 'beginner',
          description: 'Domina la terminal Linux, administración de sistemas y fundamentos de redes.',
          duration: '15 hrs',
          lessons: 30,
          topics: ['Terminal', 'Permisos', 'Procesos', 'Redes', 'Servicios']
        },
        {
          icon: 'cloud',
          title: 'Cloud Computing',
          level: 'Intermedio',
          levelClass: 'intermediate',
          description: 'Despliega aplicaciones en AWS, GCP o Azure con infraestructura como código.',
          duration: '30 hrs',
          lessons: 44,
          topics: ['AWS', 'Terraform', 'Serverless', 'Escalado', 'Costos']
        },
        {
          icon: 'deployed_code',
          title: 'Kubernetes y Orquestación',
          level: 'Avanzado',
          levelClass: 'advanced',
          description: 'Orquesta contenedores a escala con Kubernetes, Helm y service mesh.',
          duration: '35 hrs',
          lessons: 40,
          topics: ['K8s', 'Helm', 'Service mesh', 'Observabilidad', 'GitOps']
        }
      ]
    }
  ];

  get activeSteps(): RoadmapStep[] {
    const track = this.tracks.find(t => t.id === this.activeTrack);
    return track ? track.steps : [];
  }

  setActiveTrack(id: string): void {
    this.activeTrack = id;
  }
}
