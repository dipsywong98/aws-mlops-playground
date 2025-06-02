import { useEffect, useState } from "react";
import { listModels, type ModelInfo, type ModelListResponse } from "./utils/downloadModel";

const localModels: Array<ModelInfo> = [
  {
    ModelPackageVersion: 'onnx-demo',
    ModelPackageArn: './mnist.onnx',
    CreationTime: '',
  },
  {
    ModelPackageVersion: 'local-pytorch',
    ModelPackageArn: './mnist_local_pytorch.onnx',
    CreationTime: '',
  },
  {
    ModelPackageVersion: 'local-pytorch-cntk',
    ModelPackageArn: './mnist_cnn_CNTK_translated.onnx',
    CreationTime: '',
  },
  {
    ModelPackageVersion: 'local-pytorch-cntk2',
    ModelPackageArn: './mnist_cnn_CNTK_translated2.onnx',
    CreationTime: '',
  },
]

export default function ModelPicker({ value, onChange }: {
  value: string | null;
  onChange: (modelName: string) => void;
}) {
  const [models, setModels] = useState<ModelListResponse>(localModels);
  const refreshModels = () => {
    listModels().then((r) => setModels([...r, ...localModels])).catch((error) => {
      console.error("Failed to fetch models:", error);
    })
  }
  useEffect(() => {
    refreshModels()
  }, []);
  return (
    <div>
      <select value={value ?? ""} onChange={(e) => onChange(e.target.value)}>
        <option value="" disabled>Select a model</option>
        {models.map((model, index) => (
          <option key={index} value={model.ModelPackageArn}>
            {typeof(model.ModelPackageVersion) === 'number' ? `v${model.ModelPackageVersion}` : model.ModelPackageVersion} {model.CreationTime.substring(0, 19)}
          </option>
        ))}
      </select>
      <button onClick={refreshModels}>
        Refresh Models
      </button>
    </div>
  );
}
