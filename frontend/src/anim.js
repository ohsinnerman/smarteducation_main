// GSAP-based animation helpers used across pages.
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';

// Animate a number from 0 → target on mount (for stat tiles).
export function useCountUp(target, duration = 1.1) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const n = Number(target) || 0;
    const obj = { v: 0 };
    const tween = gsap.to(obj, {
      v: n,
      duration,
      ease: 'power2.out',
      onUpdate: () => setValue(obj.v),
    });
    return () => tween.kill();
  }, [target, duration]);
  return value;
}

// Stagger-fade a container's direct children in on mount.
export function useStaggerIn(deps = []) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    const items = ref.current.querySelectorAll('[data-anim]');
    const tween = gsap.fromTo(
      items,
      { y: 18, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.5, stagger: 0.06, ease: 'power2.out' }
    );
    return () => tween.kill();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return ref;
}

// One-shot fade/slide for a single element (page transitions).
export function useFadeIn() {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    const t = gsap.fromTo(ref.current, { opacity: 0, y: 10 },
      { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' });
    return () => t.kill();
  }, []);
  return ref;
}
