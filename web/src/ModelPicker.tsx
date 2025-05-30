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
      <h2>Model Picker</h2>
      <p>Select a model to use for inference.</p>
      {/* Add model selection UI here */}
      <select value={value ?? ""} onChange={(e) => onChange(e.target.value)}>
        <option value="" disabled>Select a model</option>
        {models.map((model, index) => (
          <option key={index} value={model.ModelPackageArn}>
            Model Package Version: {model.ModelPackageVersion}
          </option>
        ))}
      </select>
      {/* <ul>
        {models.map((model, index) => (
          <li key={index}>
            <strong>Model Package Version:</strong> {model.ModelPackageVersion} <br />
            <strong>Model Package ARN:</strong> {model.ModelPackageArn} <br />
            <strong>Creation Time:</strong> {new Date(model.CreationTime).toLocaleString()} <br />
          </li>
        ))}
      </ul> */}
      <button onClick={refreshModels}>
        Refresh Models
      </button>
    </div>
  );
}