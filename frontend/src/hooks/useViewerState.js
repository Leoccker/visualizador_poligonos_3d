import { useState, useCallback, useEffect } from 'react';

export function useViewerState() {
  const [renderMode, setRenderMode] = useState('both'); // 'wireframe', 'solid', 'both'
  const [projection, setProjection] = useState('perspective'); // 'perspective', 'isometric'
  const [transformMode, setTransformMode] = useState('rotate'); // 'rotate', 'translate', 'scale'

  const [rotation, setRotation] = useState([0, 0, 0]);
  const [position, setPosition] = useState([0, 0, 0]);
  const [scale, setScale] = useState(1);

  const TRANSLATION_STEP = 0.08;
  const ROTATION_STEP = Math.PI / 180 * 7; // ~7 degrees
  const SCALE_STEP = 1.08;

  const reset = useCallback(() => {
    setRotation([0, 0, 0]);
    setPosition([0, 0, 0]);
    setScale(1);
    setProjection('perspective');
    setRenderMode('both');
    setTransformMode('rotate');
  }, []);

  // Keyboard shortcuts handler
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ignore if typing in an input
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }

      const key = event.key.toLowerCase();
      const shift = event.shiftKey;

      if (event.key === 'Escape') {
        reset();
        return;
      }

      if (key === 'p') setProjection(p => p === 'perspective' ? 'isometric' : 'perspective');
      else if (key === 'w') setRenderMode('wireframe');
      else if (key === 's') {
        if (shift) setTransformMode('scale');
        else setRenderMode('solid');
      }
      else if (key === 'b') setRenderMode('both');
      else if (key === 'r') setTransformMode('rotate');
      else if (key === 't') setTransformMode('translate');

      // Arrow keys logic based on current transform mode
      else if (['arrowleft', 'arrowright', 'arrowup', 'arrowdown'].includes(key)) {
        event.preventDefault(); // Prevent scrolling
        
        if (transformMode === 'translate') {
          if (key === 'arrowleft') setPosition(p => [p[0] - TRANSLATION_STEP, p[1], p[2]]);
          else if (key === 'arrowright') setPosition(p => [p[0] + TRANSLATION_STEP, p[1], p[2]]);
          else if (key === 'arrowup') setPosition(p => [p[0], p[1] + TRANSLATION_STEP, p[2]]);
          else if (key === 'arrowdown') setPosition(p => [p[0], p[1] - TRANSLATION_STEP, p[2]]);
        } else if (transformMode === 'scale') {
          if (['arrowup', 'arrowright'].includes(key)) setScale(s => Math.min(s * SCALE_STEP, 10));
          else setScale(s => Math.max(s / SCALE_STEP, 0.1));
        } else if (transformMode === 'rotate') {
          if (key === 'arrowleft') setRotation(r => [r[0], r[1] - ROTATION_STEP, r[2]]);
          else if (key === 'arrowright') setRotation(r => [r[0], r[1] + ROTATION_STEP, r[2]]);
          else if (key === 'arrowup') setRotation(r => [r[0] - ROTATION_STEP, r[1], r[2]]);
          else if (key === 'arrowdown') setRotation(r => [r[0] + ROTATION_STEP, r[1], r[2]]);
        }
      }
      
      // X, Y, Z for specific axis rotation
      else if (transformMode === 'rotate' && ['x', 'y', 'z'].includes(key)) {
        const amount = ROTATION_STEP * (shift ? -1 : 1);
        if (key === 'x') setRotation(r => [r[0] + amount, r[1], r[2]]);
        else if (key === 'y') setRotation(r => [r[0], r[1] + amount, r[2]]);
        else if (key === 'z') setRotation(r => [r[0], r[1], r[2] + amount]);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [transformMode, reset]);

  return {
    renderMode,
    setRenderMode,
    projection,
    setProjection,
    transformMode,
    setTransformMode,
    rotation,
    setRotation,
    position,
    setPosition,
    scale,
    setScale,
    reset,
  };
}
