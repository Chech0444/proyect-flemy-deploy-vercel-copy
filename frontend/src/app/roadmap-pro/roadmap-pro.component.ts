import { Component } from '@angular/core';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Topic {
  name: string;
  optional?: boolean;
}

interface Module {
  id: string;
  title: string;
  description: string;
  topics: Topic[];
  duration: string;
  difficulty: 1 | 2 | 3 | 4 | 5;
  prerequisites: string[];
  projects: string[];
  outcomes: string[];
  icon: string;
}

interface Level {
  name: string;
  color: string;
  badge: string;
  modules: Module[];
}

interface SkillRoadmap {
  id: string;
  title: string;
  objective: string;
  icon: string;
  color: string;
  levels: Level[];
  careers: string[];
  certifications: string[];
  technologies: string[];
}

@Component({
  selector: 'app-roadmap-pro',
  imports: [NgClass, NgFor, NgIf, RouterLink],
  templateUrl: './roadmap-pro.component.html',
  styleUrl: './roadmap-pro.component.css'
})
export class RoadmapProComponent {
  activeRoadmap = 'fullstack';

  roadmaps: SkillRoadmap[] = [
    {
      id: 'fullstack',
      title: 'Desarrollo Web Full Stack',
      objective: 'Formar profesionales capaces de construir aplicaciones web completas, desde la base de datos hasta la interfaz de usuario, dominando tanto el frontend como el backend.',
      icon: 'code',
      color: 'sky',
      careers: ['Desarrollador Full Stack', 'Desarrollador Frontend', 'Desarrollador Backend', 'Arquitecto Web', 'Tech Lead'],
      certifications: ['Meta Frontend Developer', 'Meta Backend Developer', 'AWS Developer', 'Google Cloud Engineer'],
      technologies: ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker', 'AWS', 'Git', 'REST APIs'],
      levels: [
        {
          name: 'Principiante',
          color: 'emerald',
          badge: 'FUNDAMENTOS',
          modules: [
            {
              id: 'fs-01', icon: 'psychology', title: 'Fundamentos de Programación',
              description: 'Domina la lógica computacional y los principios básicos de la programación.',
              duration: '4 semanas', difficulty: 1, prerequisites: [],
              outcomes: ['Escribir algoritmos básicos', 'Usar variables y estructuras de control', 'Depurar código simple'],
              projects: ['Calculadora interactiva', 'Juego de adivinanzas'],
              topics: [
                { name: 'Algoritmos y lógica' }, { name: 'Variables y tipos de datos' },
                { name: 'Estructuras de control' }, { name: 'Funciones' },
                { name: 'Arreglos y objetos' }
              ]
            },
            {
              id: 'fs-02', icon: 'code', title: 'HTML & CSS',
              description: 'Construye interfaces web semánticas y responsivas con HTML5 y CSS3 moderno.',
              duration: '5 semanas', difficulty: 1, prerequisites: [],
              outcomes: ['Maquetar páginas web semánticas', 'Aplicar diseños responsivos', 'Usar Flexbox y Grid'],
              projects: ['Página personal responsive', 'Clon de landing page'],
              topics: [
                { name: 'HTML semántico' }, { name: 'CSS3 avanzado' },
                { name: 'Flexbox' }, { name: 'CSS Grid' },
                { name: 'Responsive Design' }, { name: 'Animaciones CSS' }
              ]
            },
            {
              id: 'fs-03', icon: 'javascript', title: 'JavaScript Esencial',
              description: 'Aprende JavaScript moderno: desde lo básico hasta manipulación del DOM y eventos.',
              duration: '6 semanas', difficulty: 2, prerequisites: ['fs-01'],
              outcomes: ['Manipular el DOM', 'Manejar eventos', 'Usar ES6+ features'],
              projects: ['Todo List app', 'Reloj dinámico'],
              topics: [
                { name: 'Sintaxis moderna (ES6+)' }, { name: 'DOM manipulation' },
                { name: 'Eventos' }, { name: 'Fetch API' },
                { name: 'Módulos ES' }
              ]
            },
            {
              id: 'fs-04', icon: 'database', title: 'Git y Control de Versiones',
              description: 'Domina Git para trabajar en equipo y gestionar el historial de tu código.',
              duration: '2 semanas', difficulty: 1, prerequisites: [],
              outcomes: ['Usar Git en proyectos', 'Colaborar con pull requests', 'Resolver conflictos'],
              projects: ['Contribución a repo open source'],
              topics: [
                { name: 'Git básico' }, { name: 'Ramas y merges' },
                { name: 'Pull requests' }, { name: 'Git flow' },
                { name: 'GitHub/GitLab' }
              ]
            }
          ]
        },
        {
          name: 'Intermedio',
          color: 'amber',
          badge: 'ESPECIALIZACIÓN',
          modules: [
            {
              id: 'fs-05', icon: 'frame_source', title: 'Framework Frontend (React)',
              description: 'Construye aplicaciones web modernas con React, hooks, estado global y routing.',
              duration: '8 semanas', difficulty: 3, prerequisites: ['fs-03'],
              outcomes: ['Crear SPA con React', 'Manejar estado global', 'Implementar rutas'],
              projects: ['E-commerce SPA', 'Dashboard interactivo'],
              topics: [
                { name: 'Componentes y JSX' }, { name: 'Hooks' },
                { name: 'Estado global (Context/Zustand)' }, { name: 'React Router' },
                { name: 'Testing con Testing Library' }
              ]
            },
            {
              id: 'fs-06', icon: 'storage', title: 'Backend con Node.js',
              description: 'Crea APIs RESTful con Node.js, Express y autenticación de usuarios.',
              duration: '7 semanas', difficulty: 3, prerequisites: ['fs-03'],
              outcomes: ['Crear APIs RESTful', 'Autenticar usuarios', 'Manejar errores'],
              projects: ['API de blog', 'Sistema de usuarios'],
              topics: [
                { name: 'Node.js runtime' }, { name: 'Express.js' },
                { name: 'Rutas y middlewares' }, { name: 'JWT y autenticación' }
              ]
            },
            {
              id: 'fs-07', icon: 'table_chart', title: 'Bases de Datos',
              description: 'Diseña y gestiona bases de datos relacionales y no relacionales.',
              duration: '5 semanas', difficulty: 2, prerequisites: [],
              outcomes: ['Diseñar esquemas SQL', 'Consultas complejas', 'Usar MongoDB'],
              projects: ['Sistema de inventario', 'API con PostgreSQL'],
              topics: [
                { name: 'SQL y PostgreSQL' }, { name: 'Diseño de esquemas' },
                { name: 'Consultas avanzadas' }, { name: 'MongoDB básico' },
                { name: 'ORMs (Prisma/TypeORM)' }
              ]
            },
            {
              id: 'fs-08', icon: 'api', title: 'APIs y Arquitectura REST',
              description: 'Diseña APIs robustas siguiendo principios REST y buenas prácticas.',
              duration: '3 semanas', difficulty: 3, prerequisites: ['fs-06'],
              outcomes: ['Diseñar APIs RESTful', 'Documentar con Swagger', 'Versionar APIs'],
              projects: ['API REST documentada'],
              topics: [
                { name: 'Principios REST' }, { name: 'Versionado' },
                { name: 'Documentación (Swagger/OpenAPI)' }, { name: 'Rate limiting' }
              ]
            }
          ]
        },
        {
          name: 'Avanzado',
          color: 'rose',
          badge: 'MAESTRÍA',
          modules: [
            {
              id: 'fs-09', icon: 'cloud', title: 'DevOps y Despliegue',
              description: 'Automatiza despliegues, configura contenedores y CI/CD para producción.',
              duration: '5 semanas', difficulty: 4, prerequisites: ['fs-04'],
              outcomes: ['Dockerizar aplicaciones', 'Configurar CI/CD', 'Desplegar en cloud'],
              projects: ['Pipeline CI/CD completo', 'App dockerizada'],
              topics: [
                { name: 'Docker' }, { name: 'CI/CD (GitHub Actions)' },
                { name: 'Nginx' }, { name: 'Cloud (AWS/Vercel)' }
              ]
            },
            {
              id: 'fs-10', icon: 'architecture', title: 'Arquitectura Frontend',
              description: 'Diseña arquitecturas frontend escalables con patrones modernos.',
              duration: '4 semanas', difficulty: 4, prerequisites: ['fs-05'],
              outcomes: ['Arquitectura basada en componentes', 'Optimizar rendimiento', 'SSR/SSG'],
              projects: ['App con Next.js SSR'],
              topics: [
                { name: 'Arquitectura de componentes' }, { name: 'SSR y SSG' },
                { name: 'Optimización de rendimiento' },
                { name: 'Patrones avanzados' }
              ]
            },
            {
              id: 'fs-11', icon: 'security', title: 'Seguridad Web',
              description: 'Protege aplicaciones web contra vulnerabilidades comunes.',
              duration: '3 semanas', difficulty: 4, prerequisites: ['fs-06', 'fs-08'],
              outcomes: ['Prevenir OWASP Top 10', 'Implementar HTTPS', 'Manejar autenticación segura'],
              projects: ['Auditoría de seguridad'],
              topics: [
                { name: 'OWASP Top 10' }, { name: 'HTTPS y SSL' },
                { name: 'CSRF/XSS' }, { name: 'SQL Injection' },
                { name: 'Seguridad en APIs' }
              ]
            },
            {
              id: 'fs-12', icon: 'rocket_launch', title: 'Proyecto Final Integrador',
              description: 'Construye una aplicación full-stack completa desde cero hasta producción.',
              duration: '8 semanas', difficulty: 5, prerequisites: ['fs-05', 'fs-06', 'fs-07', 'fs-09'],
              outcomes: ['Arquitectura full-stack', 'Producción real', 'Documentación profesional'],
              projects: ['App full-stack completa', 'Portafolio profesional'],
              topics: [
                { name: 'Planificación' }, { name: 'Stack completo' },
                { name: 'Testing E2E' }, { name: 'Deploy' },
                { name: 'Documentación' }
              ]
            }
          ]
        }
      ]
    },
    {
      id: 'devops',
      title: 'DevOps & Cloud',
      objective: 'Formar ingenieros capaces de diseñar, implementar y mantener infraestructura moderna en la nube con automatización y mejores prácticas.',
      icon: 'cloud',
      color: 'cyan',
      careers: ['DevOps Engineer', 'Site Reliability Engineer', 'Cloud Architect', 'Platform Engineer', 'Infrastructure Engineer'],
      certifications: ['AWS Solutions Architect', 'CKA (Kubernetes)', 'Terraform Associate', 'AWS DevOps Engineer'],
      technologies: ['Docker', 'Kubernetes', 'Terraform', 'AWS', 'CI/CD', 'Linux', 'Prometheus', 'GitOps'],
      levels: [
        {
          name: 'Principiante', color: 'emerald', badge: 'FUNDAMENTOS',
          modules: [
            { id: 'do-01', icon: 'terminal', title: 'Linux Esencial', description: 'Domina la terminal Linux, administración del sistema y scripting básico.', duration: '4 semanas', difficulty: 1, prerequisites: [], outcomes: ['Administrar sistema Linux', 'Escribir scripts bash', 'Gestionar procesos'], projects: ['Script de backup automatizado'], topics: [{ name: 'Terminal y comandos' }, { name: 'Permisos y usuarios' }, { name: 'Procesos' }, { name: 'Bash scripting' }] },
            { id: 'do-02', icon: 'lan', title: 'Redes y Protocolos', description: 'Comprende redes, protocolos y cómo se comunican los servicios.', duration: '3 semanas', difficulty: 2, prerequisites: [], outcomes: ['Configurar redes básicas', 'Entender TCP/IP', 'Diagnosticar conectividad'], projects: ['Laboratorio de redes'], topics: [{ name: 'TCP/IP' }, { name: 'DNS' }, { name: 'HTTP/HTTPS' }, { name: 'Firewalls' }] },
            { id: 'do-03', icon: 'code', title: 'Git Avanzado', description: 'Estrategias de branching, hooks y automatización con Git.', duration: '2 semanas', difficulty: 1, prerequisites: [], outcomes: ['Estrategias de branching', 'Git hooks', 'Automatización'], projects: ['Git workflow automation'], topics: [{ name: 'Branching strategies' }, { name: 'Git hooks' }, { name: 'Git bisect' }] }
          ]
        },
        {
          name: 'Intermedio', color: 'amber', badge: 'ESPECIALIZACIÓN',
          modules: [
            { id: 'do-04', icon: 'docker', title: 'Contenedores con Docker', description: 'Domina Docker para empaquetar y distribuir aplicaciones.', duration: '4 semanas', difficulty: 3, prerequisites: ['do-01'], outcomes: ['Crear imágenes Docker', 'Orquestar multi-container', 'Optimizar imágenes'], projects: ['App multi-contenedor'], topics: [{ name: 'Dockerfile' }, { name: 'Docker Compose' }, { name: 'Registries' }, { name: 'Volúmenes y redes' }] },
            { id: 'do-05', icon: 'deployed_code', title: 'Orquestación con Kubernetes', description: 'Orquesta contenedores a escala con Kubernetes.', duration: '6 semanas', difficulty: 4, prerequisites: ['do-04'], outcomes: ['Desplegar en K8s', 'Gestionar servicios', 'Scaling automático'], projects: ['Cluster K8s completo'], topics: [{ name: 'Pods y Deployments' }, { name: 'Services' }, { name: 'ConfigMaps' }, { name: 'Helm' }] },
            { id: 'do-06', icon: 'build_circle', title: 'CI/CD', description: 'Automatiza integración y despliegue continuo.', duration: '3 semanas', difficulty: 3, prerequisites: ['do-04', 'do-03'], outcomes: ['Pipeline CI/CD completo', 'Tests automatizados', 'Deploy continuo'], projects: ['Pipeline multi-etapa'], topics: [{ name: 'GitHub Actions' }, { name: 'Jenkins' }, { name: 'ArgoCD' }] }
          ]
        },
        {
          name: 'Avanzado', color: 'rose', badge: 'MAESTRÍA',
          modules: [
            { id: 'do-07', icon: 'cloud', title: 'Cloud Computing (AWS)', description: 'Arquitectura en AWS con servicios serverless y escalables.', duration: '6 semanas', difficulty: 4, prerequisites: ['do-01'], outcomes: ['Arquitectura AWS', 'Serverless', 'Alta disponibilidad'], projects: ['Infraestructura AWS completa'], topics: [{ name: 'EC2, S3, RDS' }, { name: 'Lambda' }, { name: 'VPC' }, { name: 'Auto Scaling' }] },
            { id: 'do-08', icon: 'terraform', title: 'Infraestructura como Código', description: 'Gestiona infraestructura con Terraform y Pulumi.', duration: '4 semanas', difficulty: 4, prerequisites: ['do-07'], outcomes: ['Escribir Terraform', 'Módulos reutilizables', 'Estado remoto'], projects: ['Infraestructura modular'], topics: [{ name: 'Terraform' }, { name: 'Módulos' }, { name: 'Estado remoto' }, { name: 'Pulumi' }] },
            { id: 'do-09', icon: 'monitoring', title: 'Monitoreo y Observabilidad', description: 'Implementa monitoreo, logging y tracing para sistemas en producción.', duration: '3 semanas', difficulty: 4, prerequisites: ['do-05', 'do-07'], outcomes: ['Monitoreo completo', 'Alertas', 'Dashboards'], projects: ['Stack de observabilidad'], topics: [{ name: 'Prometheus' }, { name: 'Grafana' }, { name: 'ELK Stack' }, { name: 'OpenTelemetry' }] }
          ]
        }
      ]
    },
    {
      id: 'ia',
      title: 'Inteligencia Artificial',
      objective: 'Formar profesionales capaces de diseñar, implementar y desplegar soluciones de IA y machine learning en producción.',
      icon: 'psychology',
      color: 'fuchsia',
      careers: ['ML Engineer', 'Data Scientist', 'AI Researcher', 'NLP Engineer', 'Computer Vision Engineer'],
      certifications: ['TensorFlow Developer', 'AWS ML Specialty', 'DeepLearning.AI Specialization', 'Azure AI Engineer'],
      technologies: ['Python', 'TensorFlow', 'PyTorch', 'LangChain', 'Hugging Face', 'RAG', 'Vector DBs', 'MLOps'],
      levels: [
        {
          name: 'Principiante', color: 'emerald', badge: 'FUNDAMENTOS',
          modules: [
            { id: 'ia-01', icon: 'functions', title: 'Matemáticas para IA', description: 'Álgebra lineal, cálculo y estadística fundamentales para machine learning.', duration: '5 semanas', difficulty: 2, prerequisites: [], outcomes: ['Operaciones con matrices', 'Cálculo diferencial', 'Probabilidad'], projects: ['Análisis estadístico'], topics: [{ name: 'Álgebra lineal' }, { name: 'Cálculo' }, { name: 'Probabilidad' }, { name: 'Estadística' }] },
            { id: 'ia-02', icon: 'code', title: 'Python para Datos', description: 'Python con librerías científicas para análisis y visualización de datos.', duration: '4 semanas', difficulty: 1, prerequisites: [], outcomes: ['Análisis con Pandas', 'Visualización', 'Numpy'], projects: ['EDA completo'], topics: [{ name: 'NumPy' }, { name: 'Pandas' }, { name: 'Matplotlib' }, { name: 'Jupyter' }] }
          ]
        },
        {
          name: 'Intermedio', color: 'amber', badge: 'ESPECIALIZACIÓN',
          modules: [
            { id: 'ia-03', icon: 'smart_toy', title: 'Machine Learning', description: 'Modelos supervisados, no supervisados y pipelines completos.', duration: '7 semanas', difficulty: 3, prerequisites: ['ia-01', 'ia-02'], outcomes: ['Modelos ML', 'Validación', 'Feature engineering'], projects: ['Pipeline ML completo'], topics: [{ name: 'Regresión' }, { name: 'Clasificación' }, { name: 'Clustering' }, { name: 'Scikit-learn' }] },
            { id: 'ia-04', icon: 'psychology', title: 'Deep Learning', description: 'Redes neuronales, CNN, RNN con TensorFlow y PyTorch.', duration: '6 semanas', difficulty: 4, prerequisites: ['ia-03'], outcomes: ['Redes neuronales', 'CNNs', 'RNNs'], projects: ['Clasificador de imágenes'], topics: [{ name: 'TensorFlow' }, { name: 'PyTorch' }, { name: 'CNN' }, { name: 'RNN/LSTM' }] },
            { id: 'ia-05', icon: 'chat', title: 'NLP y LLMs', description: 'Procesamiento de lenguaje natural y modelos de lenguaje grandes.', duration: '5 semanas', difficulty: 4, prerequisites: ['ia-03'], outcomes: ['Modelos NLP', 'Fine-tuning LLMs', 'RAG'], projects: ['Chatbot con RAG'], topics: [{ name: 'Transformers' }, { name: 'Hugging Face' }, { name: 'LangChain' }, { name: 'RAG' }] }
          ]
        },
        {
          name: 'Avanzado', color: 'rose', badge: 'MAESTRÍA',
          modules: [
            { id: 'ia-06', icon: 'cloud', title: 'MLOps', description: 'Despliega y monitorea modelos ML en producción.', duration: '4 semanas', difficulty: 5, prerequisites: ['ia-03'], outcomes: ['ML pipelines', 'Model serving', 'Monitoreo'], projects: ['MLOps pipeline'], topics: [{ name: 'MLflow' }, { name: 'Docker para ML' }, { name: 'Model serving' }, { name: 'Feature stores' }] },
            { id: 'ia-07', icon: 'rocket_launch', title: 'Proyecto Final IA', description: 'Proyecto completo de IA desde datos hasta producción.', duration: '8 semanas', difficulty: 5, prerequisites: ['ia-04', 'ia-05', 'ia-06'], outcomes: ['Solución IA completa', 'Deploy en cloud', 'Documentación'], projects: ['Producto IA completo'], topics: [{ name: 'Definición del problema' }, { name: 'Arquitectura' }, { name: 'Implementación' }, { name: 'Deploy' }] }
          ]
        }
      ]
    },
    {
      id: 'mobile',
      title: 'Desarrollo Móvil',
      objective: 'Formar desarrolladores capaces de crear aplicaciones móviles nativas y multiplataforma con estándares profesionales.',
      icon: 'smartphone',
      color: 'orange',
      careers: ['Mobile Developer', 'iOS Developer', 'Android Developer', 'React Native Developer', 'Flutter Developer'],
      certifications: ['Meta Android Developer', 'Meta iOS Developer', 'Google Associate Android Developer', 'Flutter Certified'],
      technologies: ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Firebase', 'App Store', 'Play Store'],
      levels: [
        {
          name: 'Principiante', color: 'emerald', badge: 'FUNDAMENTOS',
          modules: [
            { id: 'mo-01', icon: 'code', title: 'JavaScript para Móvil', description: 'JavaScript moderno orientado a desarrollo móvil con React Native.', duration: '4 semanas', difficulty: 1, prerequisites: [], outcomes: ['ES6+ avanzado', 'Async/await', 'Módulos'], projects: ['App CLI básica'], topics: [{ name: 'ES6+' }, { name: 'Promesas' }, { name: 'Módulos' }, { name: 'TypeScript básico' }] },
            { id: 'mo-02', icon: 'phone_iphone', title: 'UX/UI Móvil', description: 'Principios de diseño de interfaces móviles y experiencia de usuario.', duration: '3 semanas', difficulty: 1, prerequisites: [], outcomes: ['Diseño mobile-first', 'Prototipado', 'Principios UX'], projects: ['Prototipo en Figma'], topics: [{ name: 'Material Design' }, { name: 'iOS HIG' }, { name: 'Prototipado' }, { name: 'Accesibilidad' }] }
          ]
        },
        {
          name: 'Intermedio', color: 'amber', badge: 'ESPECIALIZACIÓN',
          modules: [
            { id: 'mo-03', icon: 'frame_source', title: 'React Native', description: 'Construye apps nativas multiplataforma con React Native.', duration: '8 semanas', difficulty: 3, prerequisites: ['mo-01'], outcomes: ['Apps multiplataforma', 'Navegación', 'APIs nativas'], projects: ['App de clima'], topics: [{ name: 'Componentes RN' }, { name: 'Navegación' }, { name: 'APIs nativas' }, { name: 'Estado global' }] },
            { id: 'mo-04', icon: 'storage', title: 'Backend para Móvil', description: 'APIs y servicios backend optimizados para aplicaciones móviles.', duration: '4 semanas', difficulty: 3, prerequisites: ['mo-01'], outcomes: ['APIs REST móviles', 'Firebase', 'Push notifications'], projects: ['Backend para app'], topics: [{ name: 'Firebase' }, { name: 'REST APIs' }, { name: 'Push notifications' }, { name: 'WebSockets' }] }
          ]
        },
        {
          name: 'Avanzado', color: 'rose', badge: 'MAESTRÍA',
          modules: [
            { id: 'mo-05', icon: 'flutter', title: 'Flutter Avanzado', description: 'Desarrollo nativo compilado con Flutter y Dart.', duration: '6 semanas', difficulty: 4, prerequisites: ['mo-03'], outcomes: ['Apps en Flutter', 'Widgets avanzados', 'Animaciones'], projects: ['App con Flutter'], topics: [{ name: 'Dart' }, { name: 'Widgets' }, { name: 'Estado (Bloc/Riverpod)' }, { name: 'Animaciones' }] },
            { id: 'mo-06', icon: 'rocket_launch', title: 'Publicación y Distribución', description: 'Publica apps en App Store y Google Play con CI/CD móvil.', duration: '3 semanas', difficulty: 4, prerequisites: ['mo-03', 'mo-04'], outcomes: ['Publicar en stores', 'CI/CD móvil', 'ASO'], projects: ['App publicada'], topics: [{ name: 'App Store' }, { name: 'Google Play' }, { name: 'CodePush' }, { name: 'Fastlane' }] }
          ]
        }
      ]
    }
  ];

  selectedModule: string | null = null;
  showAll = false;

  get current(): SkillRoadmap {
    return this.roadmaps.find(r => r.id === this.activeRoadmap) || this.roadmaps[0];
  }

  setActive(id: string) { this.activeRoadmap = id; this.selectedModule = null; }
  toggleModule(id: string) { this.selectedModule = this.selectedModule === id ? null : id; }
  toggleShowAll() { this.showAll = !this.showAll; }

  getModuleTitle(id: string): string {
    for (const r of this.roadmaps) {
      for (const l of r.levels) {
        const m = l.modules.find(m => m.id === id);
        if (m) return m.title;
      }
    }
    return id;
  }

  difficultyStars(n: number): string[] {
    const filled = n;
    const total = 5;
    return Array.from({ length: total }, (_, i) => i < filled ? 'filled' : 'empty');
  }
}
