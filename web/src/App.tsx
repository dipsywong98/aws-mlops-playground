import { useMemo, useState } from 'react';
import CanvasDraw from './CanvasDraw';
import Inference from './Inference';
import ModelPicker from './ModelPicker';
import type { InferenceSession } from 'onnxruntime-web';
import { loadModelFileAsSession } from './utils/runModel';
import { getModelDownloadUrl } from './utils/downloadModel';

export default function App() {
  const [outputArray, setOutputArray] = useState<number[][]>(Array(28).fill(Array(28).fill(0)));
  const [pickedModelName, setPickedModelName] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Record<string, InferenceSession>>({});

  const handleModelNameChange = async (modelName: string) => {
    setPickedModelName(modelName);
    if (!(modelName in sessions)) {
      const downloadUrl = await getModelDownloadUrl(modelName);
      // const downloadUrl = '/mnist-0.onnx'; // For local testing, replace with actual download URL in production
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

  return (
    <div>
      <h1>Hello, world!</h1>
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
