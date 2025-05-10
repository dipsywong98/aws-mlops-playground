import { useCallback, useEffect, useMemo, useState } from "react";
import { createModelCpu, runModel, warmupModel } from "./utils/runModel";
import { Tensor } from "onnxruntime-web";
import { softmax } from "./utils/math";

const postprocess = (rawOutput: Tensor): number[] => {
  return softmax(Array.prototype.slice.call(rawOutput.data));
}

export default function Inference({modelPath, inputArray}: {modelPath: string, inputArray: number[][]}) {
  const [output, setOutput] = useState<number[]>(Array(10).fill(0));
  const session = useMemo(async () => {
    const response = await fetch(modelPath);
    const modelFile = await response.arrayBuffer()
    const cpuSession = await createModelCpu(modelFile);
    const session = cpuSession;
    await warmupModel(session, [1, 1, 28, 28])
    return session;
  }, [modelPath])

  const handleInference = useCallback(async (inputArray: number[][]) => {
    const [result] = await runModel(await session, new Tensor('float32', new Float32Array(inputArray.flat()), [1, 1, 28, 28]));
    setOutput(postprocess(result));
  }, [session]);

  useEffect(() => {
    handleInference(inputArray)
  }, [handleInference, inputArray]);

  return (
    <div>
      <button onClick={() => handleInference(inputArray)}>Run Inference</button>
      <p>Output:</p>
      <ol start={0}> {output.map((p) => <li>{p.toFixed(2)}</li>)}</ol>
    </div>
  );
}
