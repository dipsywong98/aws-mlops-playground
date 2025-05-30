import { useCallback, useEffect, useState } from "react";
import { runModel,  } from "./utils/runModel";
import { InferenceSession, Tensor } from "onnxruntime-web";
import { softmax } from "./utils/math";

const postprocess = (rawOutput: Tensor): number[] => {
  return softmax(Array.prototype.slice.call(rawOutput.data));
}

export default function Inference({inputArray, session}: {inputArray: number[][], session: InferenceSession}) {
  const [output, setOutput] = useState<number[]>(Array(10).fill(0));

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
