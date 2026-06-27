import {
  Component,
  OnInit,
  OnDestroy,
  AfterViewInit,
  ElementRef,
  ViewChild,
  Renderer2,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css'],
})
export class LandingComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('heroHeading') heroHeading!: ElementRef<HTMLElement>;

  private observer!: IntersectionObserver;
  private navScrollListener: (() => void) | null = null;
  private isBrowser: boolean;

  constructor(
    private el: ElementRef,
    private renderer: Renderer2,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    if (!this.isBrowser) return;

    this.initScrollReveal();
    this.initNavScroll();
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
    this.navScrollListener?.();
  }

  scrollTo(id: string): void {
    if (!this.isBrowser) return;
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  /** Intersection Observer for staggered reveal animations */
  private initScrollReveal(): void {
    const targets = this.el.nativeElement.querySelectorAll('[data-reveal]');

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement;
            const delay = el.dataset['revealDelay'] || '0';
            el.style.transitionDelay = `${delay}ms`;
            el.classList.add('revealed');
            this.observer.unobserve(el);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );

    targets.forEach((t: Element) => this.observer.observe(t));
  }

  /** Nav background on scroll */
  private initNavScroll(): void {
    const nav = this.el.nativeElement.querySelector('.nav');
    if (!nav) return;

    const handler = () => {
      if (window.scrollY > 20) {
        nav.classList.add('nav--scrolled');
      } else {
        nav.classList.remove('nav--scrolled');
      }
    };

    window.addEventListener('scroll', handler, { passive: true });
    this.navScrollListener = () =>
      window.removeEventListener('scroll', handler);
  }
}
