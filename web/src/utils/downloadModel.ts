import config from "./config";
import z from "zod";



export const ModelInfo = z.object({
  ModelPackageVersion: z.number(),
  ModelPackageArn: z.string(),
  CreationTime: z.string()
})

export const ListModelsResponse = z.array(ModelInfo);
export type ModelInfo = z.infer<typeof ModelInfo>;

export type ModelListResponse = z.infer<typeof ListModelsResponse>;


export const listModels = async (): Promise<ModelListResponse> => {
  const url = config.GET_MODEL_URL
  // const url = '/models.json'
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch models list from ${url}`);
  }

  return ListModelsResponse.parse(await response.json());
}

export const getModelDownloadUrl = async (modelName: string): Promise<string> => {
  const url = `${config.GET_MODEL_URL}?ModelPackageArn=${modelName}`;
  const resp = await fetch(url).then(r => {
    if (!r.ok) {
      throw new Error(`Failed to fetch model download URL from ${url}`);
    }
    return r.json()
  });
  console.log(resp)
  const { download_url } = resp
  if (!download_url) {
    throw new Error(`Download URL not found for model: ${modelName}`);
  }
  return resp.download_url;
}
