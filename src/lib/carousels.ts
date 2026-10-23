// Swiper settings copied from the live theme JS (capture/theme-source). Shared by all carousels.
// Additions for accessibility: autoplay pauses on hover/focus and is off under reduced motion.
import Swiper from 'swiper';
import { Autoplay, Navigation, A11y } from 'swiper/modules';
import 'swiper/css';

export const CONFIGS: Record<string, object> = {
  '.testimonial-carousel': {
    loop: true,
    autoplay: { delay: 7000, disableOnInteraction: false },
    breakpoints: { 640: { slidesPerView: 1, spaceBetween: 10 }, 768: { slidesPerView: 2.5, spaceBetween: 15 }, 1024: { slidesPerView: 3.5, spaceBetween: 15 } },
  },
  '.about-image-carousel': { loop: true, slidesPerView: 1, autoplay: { delay: 2500, disableOnInteraction: false } },
  '.project-image-carousel': { loop: true, slidesPerView: 1, autoplay: { delay: 2500, disableOnInteraction: true } },
  '.riba-stages-carousel': {
    loop: true,
    autoplay: { delay: 2500, disableOnInteraction: true },
    breakpoints: { 640: { slidesPerView: 1, spaceBetween: 10 }, 768: { slidesPerView: 1.6, spaceBetween: 15 }, 1024: { slidesPerView: 3.2, spaceBetween: 15 } },
    navigation: { prevEl: '.riba-stages-carousel-nav__prev', nextEl: '.riba-stages-carousel-nav__next' },
  },
  '.location-projects-carousel': {
    loop: true,
    autoplay: { delay: 4000, disableOnInteraction: false },
    breakpoints: { 768: { slidesPerView: 1, spaceBetween: 0 }, 1024: { slidesPerView: 2, spaceBetween: 15 } },
  },
};

/** Initialise every carousel matching `selector` on the page. Optional prev/next buttons inside it. */
export function initCarousel(selector: string, extra: object = {}) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll<HTMLElement>(selector).forEach((el) => {
    const base: any = { ...CONFIGS[selector], ...extra };
    if (reduce) base.autoplay = false;
    else if (base.autoplay) base.autoplay = { ...base.autoplay, pauseOnMouseEnter: true };
    const swiper = new Swiper(el, { modules: [Autoplay, Navigation, A11y], a11y: { enabled: true }, ...base });
    if (base.autoplay) {
      el.addEventListener('focusin', () => swiper.autoplay?.stop());
      el.addEventListener('focusout', () => swiper.autoplay?.start());
    }
  });
}
