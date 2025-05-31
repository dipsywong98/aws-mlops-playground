import { useEffect, useMemo, useState } from 'react';
import CanvasDraw from './CanvasDraw';
import Inference from './Inference';
import ModelPicker from './ModelPicker';
import type { InferenceSession } from 'onnxruntime-web';
import { loadModelFileAsSession } from './utils/runModel';
import { getModelDownloadUrl } from './utils/downloadModel';

const writeUpUrl = 'https://hackmd.io/-dDxFNT0ROadEo6dUEqMyA'

export default function App() {
  const [outputArray, setOutputArray] = useState<number[][]>(Array(28).fill(Array(28).fill(0)));
  const [pickedModelName, setPickedModelName] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Record<string, InferenceSession>>({});

  const handleModelNameChange = async (modelName: string) => {
    setPickedModelName(modelName);
    if (!(modelName in sessions)) {
      const downloadUrl = await getModelDownloadUrl(modelName);
      // const downloadUrl = './mnist_local_pytorch.onnx'; // For local testing, replace with actual download URL in production
      console.log(`Downloading model: ${modelName} from ${downloadUrl}`);
      const modelFile = await fetch(downloadUrl).then(r => r.arrayBuffer());
      console.log(modelFile)
      const session = await loadModelFileAsSession(modelFile);
      setSessions({...sessions, [modelName]: session });
    }
  }

  const inferenceResult = useMemo(() => {
    if (!pickedModelName) {
      return 'pick a model first'
    }
    if (!sessions[pickedModelName]) {
      return 'loading model...'
    }
    return <Inference session={sessions[pickedModelName]} inputArray={outputArray} />;
  }, [pickedModelName, sessions, outputArray]);

  useEffect(() => {
    if (window.location.href.includes('openWriteUp')) {
      window.location.href = writeUpUrl
    }
  }, [])

  return (
    <div>
      <h1>MNIST Playground</h1>
      <p>
        <a href="https://dipsy.me" target='_blank'>Made by Dipsy</a>
        {' | '}
        <a href="https://github.com/dipsywong98/aws-mlops-playground/" target='_blank'>Repo</a>
        {' | '}
        <a href={writeUpUrl} target='_blank'>Write Up</a>
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <ModelPicker value={pickedModelName} onChange={handleModelNameChange} />
        <div>
          <CanvasDraw value={outputArray} onUpdate={setOutputArray} />
        </div>
        <div>
          {inferenceResult}
        </div>
      </div>
    </div>
  );
}
