import React, { useRef } from 'react';

export default function CanvasDraw({ onUpdate}: {value?: number[][], onUpdate?: (value: number[][]) => void}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    onUpdate?.(Array(28).fill(Array(28).fill(0)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'black';

    const rect = canvas.getBoundingClientRect();
    const startX = e.clientX - rect.left;
    const startY = e.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(startX, startY);

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const x = moveEvent.clientX - rect.left;
      const y = moveEvent.clientY - rect.top;
      ctx.lineTo(x, y);
      ctx.stroke();
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);

      // Generate the 28x28 array
      const imageData = ctx.getImageData(0, 0, 300, 300);
      const data = imageData.data;
      const newOutputArray = Array(28)
        .fill(0)
        .map(() => Array(28).fill(0));

      for (let i = 0; i < 28; i++) {
        for (let j = 0; j < 28; j++) {
          const x = Math.floor((i * 300) / 28);
          const y = Math.floor((j * 300) / 28);
          const pixelIndex = (y * 300 + x) * 4;
          const alpha = data[pixelIndex + 3]; // Alpha channel
          newOutputArray[j][i] = alpha > 0 ? 1 : 0;
        }
      }

      onUpdate?.(newOutputArray);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <div>
        <canvas
          ref={canvasRef}
          width={300}
          height={300}
          style={{ border: '1px solid black', cursor: 'crosshair' }}
          onMouseDown={handleMouseDown}
        ></canvas>
        <div>
          <button onClick={handleClear}>clear</button>
        </div>
      </div>
      {/* <pre>{outputArray?.map(array => array.join('')).join('\n')}</pre> */}
    </div>
  );
}