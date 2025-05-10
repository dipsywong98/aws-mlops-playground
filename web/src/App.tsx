import { useState } from 'react';
import CanvasDraw from './CanvasDraw';
import Inference from './Inference';

export default function App() {
  const [outputArray, setOutputArray] = useState<number[][]>(Array(28).fill(Array(28).fill(0)));
  return (
    <div>
      <h1>Hello, world!</h1>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <div>
          <CanvasDraw value={outputArray} onUpdate={setOutputArray} />
        </div>
        <div>
          <Inference modelPath="/mnist.onnx" inputArray={outputArray} />
        </div>
      </div>
    </div>
  );
}
