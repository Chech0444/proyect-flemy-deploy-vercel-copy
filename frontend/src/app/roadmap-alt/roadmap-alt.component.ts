import { Component } from '@angular/core';
import { NgClass, NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';

interface SkillNode {
  icon: string;
  title: string;
  level: string;
  description: string;
  duration: string;
  lessons: number;
  row: number;
  col: number;
}

interface TrackAlt {
  id: string;
  label: string;
  nodes: SkillNode[];
}

@Component({
  selector: 'app-roadmap-alt',
  imports: [NgClass, NgFor, RouterLink],
  templateUrl: './roadmap-alt.component.html',
  styleUrl: './roadmap-alt.component.css'
})
export class RoadmapAltComponent {
  activeTrack = 'full';

  tracks: TrackAlt[] = [
    {
      id: 'full',
      label: 'Ruta Completa',
      nodes: [
        { icon: 'psychology', title: 'Fundamentos de Programación', level: 'Principiante', description: 'Lógica, variables, condicionales y ciclos.', duration: '20 hrs', lessons: 48, row: 1, col: 1 },
        { icon: 'code', title: 'Desarrollo Web Frontend', level: 'Principiante', description: 'HTML, CSS y JavaScript para interfaces modernas.', duration: '35 hrs', lessons: 72, row: 1, col: 3 },
        { icon: 'database', title: 'Bases de Datos y Backend', level: 'Intermedio', description: 'APIs, SQL, NoSQL y autenticación.', duration: '30 hrs', lessons: 56, row: 2, col: 2 },
        { icon: 'smart_toy', title: 'Inteligencia Artificial', level: 'Intermedio', description: 'Machine learning, NLP y prompt engineering.', duration: '40 hrs', lessons: 64, row: 2, col: 4 },
        { icon: 'terminal', title: 'DevOps y Cloud', level: 'Avanzado', description: 'Docker, CI/CD y cloud services.', duration: '25 hrs', lessons: 40, row: 3, col: 1 },
        { icon: 'rocket_launch', title: 'Proyecto Final Integrador', level: 'Avanzado', description: 'Proyecto real full-stack completo.', duration: '50 hrs', lessons: 12, row: 3, col: 3 },
      ]
    },
    {
      id: 'web',
      label: 'Desarrollo Web',
      nodes: [
        { icon: 'code', title: 'HTML & CSS Profesional', level: 'Principiante', description: 'HTML semántico, CSS Grid y Flexbox.', duration: '15 hrs', lessons: 36, row: 1, col: 1 },
        { icon: 'javascript', title: 'JavaScript Avanzado', level: 'Intermedio', description: 'Closures, promesas y async/await.', duration: '25 hrs', lessons: 48, row: 2, col: 2 },
        { icon: 'frame_source', title: 'Frameworks Modernos', level: 'Avanzado', description: 'Angular, React o Vue con escalabilidad.', duration: '40 hrs', lessons: 60, row: 3, col: 1 },
      ]
    },
    {
      id: 'ia',
      label: 'Inteligencia Artificial',
      nodes: [
        { icon: 'functions', title: 'Matemáticas para IA', level: 'Intermedio', description: 'Álgebra lineal y estadística aplicada.', duration: '20 hrs', lessons: 32, row: 1, col: 2 },
        { icon: 'smart_toy', title: 'Machine Learning', level: 'Intermedio', description: 'Modelos supervisados y no supervisados.', duration: '35 hrs', lessons: 48, row: 2, col: 1 },
        { icon: 'psychology', title: 'Deep Learning & NLP', level: 'Avanzado', description: 'Redes neuronales y transformers.', duration: '45 hrs', lessons: 56, row: 3, col: 2 },
      ]
    },
    {
      id: 'devops',
      label: 'DevOps & Cloud',
      nodes: [
        { icon: 'terminal', title: 'Linux y Redes', level: 'Principiante', description: 'Terminal, administración y redes.', duration: '15 hrs', lessons: 30, row: 1, col: 1 },
        { icon: 'cloud', title: 'Cloud Computing', level: 'Intermedio', description: 'AWS, GCP y Terraform.', duration: '30 hrs', lessons: 44, row: 2, col: 2 },
        { icon: 'deployed_code', title: 'Kubernetes y Orquestación', level: 'Avanzado', description: 'K8s, Helm y service mesh.', duration: '35 hrs', lessons: 40, row: 3, col: 1 },
      ]
    }
  ];

  get activeNodes(): SkillNode[] {
    const track = this.tracks.find(t => t.id === this.activeTrack);
    return track ? track.nodes : [];
  }

  get gridCols(): string {
    const maxCol = Math.max(...this.activeNodes.map(n => n.col));
    return `grid-cols-${Math.min(maxCol, 4)}`;
  }

  setActiveTrack(id: string): void {
    this.activeTrack = id;
  }

  nodeColor(level: string): string {
    switch (level) {
      case 'Principiante': return 'emerald';
      case 'Intermedio': return 'amber';
      case 'Avanzado': return 'rose';
      default: return 'sky';
    }
  }

  connections(): { from: SkillNode; to: SkillNode }[] {
    const nodes = this.activeNodes;
    const conns: { from: SkillNode; to: SkillNode }[] = [];
    for (let i = 0; i < nodes.length - 1; i++) {
      const a = nodes[i];
      const b = nodes[i + 1];
      const dist = Math.abs(a.row - b.row) + Math.abs(a.col - b.col);
      if (dist <= 3) {
        conns.push({ from: a, to: b });
      }
    }
    return conns;
  }
}
