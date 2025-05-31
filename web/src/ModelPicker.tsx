import { useEffect, useState } from "react";
import { listModels, type ModelListResponse } from "./utils/downloadModel";

export default function ModelPicker ({value, onChange}: {
  value: string | null;
  onChange: (modelName: string) => void;}) {
  const [models, setModels] = useState<ModelListResponse>([]);
  const refreshModels = () => {
    listModels().then(setModels).catch((error) => {
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
            v{model.ModelPackageVersion} {model.CreationTime.substring(0, 19)}
          </option>
        ))}
      </select>
      <button onClick={refreshModels}>
        Refresh Models
      </button>
    </div>
  );
}
