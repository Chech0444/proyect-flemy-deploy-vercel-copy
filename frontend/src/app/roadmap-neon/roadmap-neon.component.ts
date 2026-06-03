import { Component } from '@angular/core';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Mission {
  id: string;
  icon: string;
  title: string;
  level: 'INIT' | 'DEV' | 'PRO';
  description: string;
  duration: string;
  lessons: number;
  xp: number;
  topics: string[];
}

interface Sector {
  id: string;
  label: string;
  missions: Mission[];
}

@Component({
  selector: 'app-roadmap-neon',
  imports: [NgClass, NgFor, NgIf, RouterLink],
  templateUrl: './roadmap-neon.component.html',
  styleUrl: './roadmap-neon.component.css'
})
export class RoadmapNeonComponent {
  activeTrack = 'full';
  selectedMission: string | null = null;
  bootSequence = true;

  constructor() {
    setTimeout(() => this.bootSequence = false, 2500);
  }

  sectors: Sector[] = [
    {
      id: 'full',
      label: 'Ruta Completa',
      missions: [
        { id: 'm1', icon: 'psychology', title: 'Fundamentos de Programación', level: 'INIT', description: 'Lógica computacional, variables, condicionales, ciclos y estructuras de datos fundamentales.', duration: '20 hrs', lessons: 48, xp: 500, topics: ['Lógica', 'Variables', 'Condicionales', 'Ciclos', 'Arreglos'] },
        { id: 'm2', icon: 'code', title: 'Desarrollo Web Frontend', level: 'INIT', description: 'HTML semántico, CSS moderno, JavaScript y responsive design.', duration: '35 hrs', lessons: 72, xp: 850, topics: ['HTML5', 'CSS3', 'JavaScript', 'Flexbox', 'Grid'] },
        { id: 'm3', icon: 'database', title: 'Bases de Datos y Backend', level: 'DEV', description: 'APIs REST, SQL, NoSQL y autenticación de usuarios.', duration: '30 hrs', lessons: 56, xp: 1200, topics: ['REST', 'SQL', 'MongoDB', 'JWT', 'Deploy'] },
        { id: 'm4', icon: 'smart_toy', title: 'Inteligencia Artificial', level: 'DEV', description: 'Machine learning, NLP y generación de contenido con IA.', duration: '40 hrs', lessons: 64, xp: 2000, topics: ['ML', 'NLP', 'PyTorch', 'Fine-tuning', 'RAG'] },
        { id: 'm5', icon: 'terminal', title: 'DevOps y Cloud', level: 'PRO', description: 'Docker, CI/CD, Kubernetes y cloud services.', duration: '25 hrs', lessons: 40, xp: 2500, topics: ['Docker', 'K8s', 'AWS', 'Terraform', 'GitOps'] },
        { id: 'm6', icon: 'rocket_launch', title: 'Proyecto Final Integrador', level: 'PRO', description: 'Proyecto real completo desde la planificación hasta el despliegue.', duration: '50 hrs', lessons: 12, xp: 5000, topics: ['Full-stack', 'Testing', 'CI/CD', 'Docs', 'Deploy'] },
      ]
    },
    {
      id: 'web',
      label: 'Web',
      missions: [
        { id: 'w1', icon: 'code', title: 'HTML & CSS Profesional', level: 'INIT', description: 'HTML semántico, CSS Grid, Flexbox y animaciones.', duration: '15 hrs', lessons: 36, xp: 400, topics: ['HTML5', 'CSS3', 'Flexbox', 'Grid', 'Animaciones'] },
        { id: 'w2', icon: 'javascript', title: 'JavaScript Avanzado', level: 'DEV', description: 'Closures, promesas, async/await y patrones de diseño.', duration: '25 hrs', lessons: 48, xp: 1000, topics: ['ES6+', 'Async', 'Patrones', 'Testing', 'DOM'] },
        { id: 'w3', icon: 'frame_source', title: 'Frameworks Modernos', level: 'PRO', description: 'Angular, React o Vue con arquitectura escalable.', duration: '40 hrs', lessons: 60, xp: 2000, topics: ['Componentes', 'Estado', 'Ruteo', 'SSR', 'Perf'] },
      ]
    },
    {
      id: 'ia',
      label: 'IA',
      missions: [
        { id: 'a1', icon: 'functions', title: 'Matemáticas para IA', level: 'DEV', description: 'Álgebra lineal, cálculo y estadística aplicada al ML.', duration: '20 hrs', lessons: 32, xp: 800, topics: ['Álgebra', 'Cálculo', 'Probabilidad', 'Estadística'] },
        { id: 'a2', icon: 'smart_toy', title: 'Machine Learning', level: 'DEV', description: 'Modelos supervisados y no supervisados con Python.', duration: '35 hrs', lessons: 48, xp: 1800, topics: ['Regresión', 'Clasificación', 'Clustering', 'Feature'] },
        { id: 'a3', icon: 'psychology', title: 'Deep Learning & NLP', level: 'PRO', description: 'Redes neuronales y transformers con TensorFlow/PyTorch.', duration: '45 hrs', lessons: 56, xp: 3500, topics: ['CNN', 'RNN', 'Transformers', 'Fine-tuning'] },
      ]
    },
    {
      id: 'devops',
      label: 'DevOps',
      missions: [
        { id: 'd1', icon: 'terminal', title: 'Linux y Redes', level: 'INIT', description: 'Terminal, administración de sistemas y redes.', duration: '15 hrs', lessons: 30, xp: 350, topics: ['Terminal', 'Permisos', 'Procesos', 'Redes'] },
        { id: 'd2', icon: 'cloud', title: 'Cloud Computing', level: 'DEV', description: 'AWS, GCP, Azure con infraestructura como código.', duration: '30 hrs', lessons: 44, xp: 1500, topics: ['AWS', 'Terraform', 'Serverless', 'Escalado'] },
        { id: 'd3', icon: 'deployed_code', title: 'Kubernetes y Orquestación', level: 'PRO', description: 'Contenedores a escala con K8s, Helm y service mesh.', duration: '35 hrs', lessons: 40, xp: 2800, topics: ['K8s', 'Helm', 'Service Mesh', 'Observabilidad'] },
      ]
    }
  ];

  get activeMissions(): Mission[] {
    const sector = this.sectors.find(s => s.id === this.activeTrack);
    return sector ? sector.missions : [];
  }

  setActiveTrack(id: string): void {
    this.activeTrack = id;
    this.selectedMission = null;
  }

  toggleMission(id: string): void {
    this.selectedMission = this.selectedMission === id ? null : id;
  }

  levelLabel(l: 'INIT' | 'DEV' | 'PRO'): string {
    return { INIT: 'NOVATO', DEV: 'DEVELOPER', PRO: 'PRO HACKER' }[l];
  }
}
